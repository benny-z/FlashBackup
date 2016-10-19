from os.path import exists, join, dirname, realpath
from time import sleep
import pythoncom
import wmi

import servicemanager

conf_filename = join(dirname(realpath(__file__)), 'flashBackup.ini')
log_fw = 'event_logs'

def log(content):
	if 'event_logs' == log_fw:
		content = unicode(content)
		servicemanager.LogMsg (servicemanager.EVENTLOG_INFORMATION_TYPE, 0xF000, (content, ''))
	if 'stdout' == log_fw:
		print(content)

def wait_for_file_to_appear(filename):
  return wait_for_result(exists, True, 600, 1)(filename)

def attempt_with_timeout(func, timeout, time_delta):
  def dec(*args, **kwargs):
    total_time = 0
    while total_time < timeout:
      try:
        return func(*args, **kwargs)  
      except:
        sleep(time_delta)
        total_time += time_delta
      func(*args, **kwargs)
    return dec  

def wait_for_result(func, wanted_result, timeout = -1, time_delta = -1):
  def dec(*args, **kwargs):  
      total_time = 0
      result = None
      while (-1 == timeout and -1 == time_delta) or total_time < timeout:
          result = func(*args, **kwargs)
          if wanted_result == result:
          	return result
          sleep(time_delta)
          total_time += time_delta
          return result
  return dec

def get_drive_letter_by_device_serial(serial):
  # new method
  pythoncom.CoInitialize()
  c = wmi.WMI()
  deviceID = [diskDrive.Dependent.deviceID for diskDrive in c.Win32_DiskDriveToDiskPartition() if serial in diskDrive.Antecedent.PNPDeviceID][0]
  return '%s\\' % [logicalDisk.Dependent.deviceID for logicalDisk in c.Win32_LogicalDiskToPartition() if deviceID == logicalDisk.Antecedent.deviceID][0]

  # old method
  '''
  base_key = 'SOFTWARE\Microsoft\Windows Portable Devices\Devices'
  devices_reg_key = _winreg.OpenKey(win32con.HKEY_LOCAL_MACHINE, base_key)
  
  number_of_sub_keys, number_of_values, lastMod = _winreg.QueryInfoKey(devices_reg_key)
  try:
    for i in range(number_of_sub_keys):
      sub_key_name = _winreg.EnumKey(devices_reg_key, i)
      if device_name in str(sub_key_name):
        sub_key = _winreg.OpenKey(devices_reg_key, sub_key_name)
        letter = _winreg.QueryValueEx(sub_key, 'FriendlyName')[0]
        if ':\\' in letter:
          # sometimes there are "friendly names" such as NOKIA, that don't represent a drive letter
          return letter
  except:
    log(traceback.format_exc())
  '''
