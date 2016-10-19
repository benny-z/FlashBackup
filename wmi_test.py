import wmi

def get_drive_letter_by_device_serial(serial):
  # new method
  c = wmi.WMI()
  return [diskDrive.Caption for diskDrive in c.win32_diskdrive() if diskDrive.MediaType == 'Removable Media' and serial in diskDrive.PNPDeviceID][0]

print(get_drive_letter_by_device_serial('352'))

