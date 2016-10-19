import win32serviceutil
import win32service
import win32event
import servicemanager
import win32con
from os import chdir, path, getcwd
from time import sleep
import copyer
import traceback
import _winreg
import win32gui
import win32gui_struct
struct = win32gui_struct.struct
pywintypes = win32gui_struct.pywintypes
import win32con
from win32api import OutputDebugString
from utils import log

GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEREMOVECOMPLETE = 0x8004

import ctypes

#
# Cut-down clone of UnpackDEV_BROADCAST from win32gui_struct, to be
# used for monkey-patching said module with correct handling
# of the "name" param of DBT_DEVTYPE_DEVICEINTERFACE
#


def _UnpackDEV_BROADCAST(lparam):
    if lparam == 0:
        return None
    hdr_format = "iii"
    hdr_size = struct.calcsize(hdr_format)
    hdr_buf = win32gui.PyGetMemory(lparam, hdr_size)
    size, devtype, reserved = struct.unpack("iii", hdr_buf)
    # Due to x64 alignment issues, we need to use the full format string over
    # the entire buffer.  ie, on x64:
    # calcsize('iiiP') != calcsize('iii')+calcsize('P')
    buf = win32gui.PyGetMemory(lparam, size)

    extra = {}
    if devtype == win32con.DBT_DEVTYP_DEVICEINTERFACE:
        fmt = hdr_format + "16s"
        _, _, _, guid_bytes = struct.unpack(fmt, buf[:struct.calcsize(fmt)])
        extra['classguid'] = pywintypes.IID(guid_bytes, True)
        extra['name'] = ctypes.wstring_at(lparam + struct.calcsize(fmt))
    else:
        raise NotImplementedError("unknown device type %d" % (devtype,))
    return win32gui_struct.DEV_BROADCAST_INFO(devtype, **extra)
win32gui_struct.UnpackDEV_BROADCAST = _UnpackDEV_BROADCAST


class DeviceEventService(win32serviceutil.ServiceFramework):

    _svc_name_ = "Backuper"
    _svc_display_name_ = "Backuper"
    _svc_description_ = "a service that backs up stuff"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        #
        # Specify that we're interested in device interface
        # events for USB devices
        #
        filter = win32gui_struct.PackDEV_BROADCAST_DEVICEINTERFACE(
            GUID_DEVINTERFACE_USB_DEVICE
        )
        self.hDevNotify = win32gui.RegisterDeviceNotification(
            self.ssh,  # copy of the service status handle
            filter,
            win32con.DEVICE_NOTIFY_SERVICE_HANDLE
        )

    #
    # Add to the list of controls already handled by the underlying
    # ServiceFramework class. We're only interested in device events
    #
    def GetAcceptedControls(self):
        rc = win32serviceutil.ServiceFramework.GetAcceptedControls(self)
        #rc |= win32service.SERVICE_CONTROL_DEVICEEVENT
        return rc

    #
    # Handle non-standard service events (including our device broadcasts)
    # by logging to the Application event log
    #
    def SvcOtherEx(self, control, event_type, data):
        if control == win32service.SERVICE_CONTROL_DEVICEEVENT:
            info = win32gui_struct.UnpackDEV_BROADCAST(data)
            #
            # This is the key bit here where you'll presumably
            # do something other than log the event. Perhaps pulse
            # a named event or write to a secure pipe etc. etc.
            #
            if event_type == DBT_DEVICEARRIVAL:
                device_name = info.name
                log("Device %s connected" % info.name)
                device_serial = device_name.split('#')[2]
                copyer.run(device_serial)
            elif event_type == DBT_DEVICEREMOVECOMPLETE:
                log("Device %s removed" % info.name)

    #
    # Standard stuff for stopping and running service; nothing
    # specific to device notifications
    #
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, '')
        )

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(DeviceEventService)
