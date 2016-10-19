from configparser import SafeConfigParser
import pythoncom
import wmi
from utils import conf_filename, wait_for_result, log_fw
from PyQt5.QtWidgets import QMessageBox, QDialog, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from threading import Thread
from copyer import run

parser = SafeConfigParser()


def is_removable_drive(drive_letter):
    pythoncom.CoInitialize()
    c = wmi.WMI()
    drive_letter = drive_letter.replace('\\', '')
    return len([localDisk for localDisk in c.Win32_LogicalDisk(Description='Removable Disk', DeviceID=drive_letter)]) > 0


def get_serial_by_drive_letter(drive_letter):
    pythoncom.CoInitialize()
    c = wmi.WMI()
    logical_drive = [logicalDisk.Antecedent.deviceID for logicalDisk in c.Win32_LogicalDiskToPartition(
    ) if logicalDisk.Dependent.deviceID.lower() in drive_letter.lower()][0]
    return [diskDrive.Antecedent.PNPDeviceID for diskDrive in c.Win32_DiskDriveToDiskPartition() if logical_drive == diskDrive.Dependent.deviceID][0].split('\\')[-1].split('&')[0]


def is_record_exists(conf_filename, serial):
    parser.read(conf_filename)
    for section_name in parser.sections():
        if parser.has_option(section_name, 'serial') and serial == parser.get(section_name, 'serial'):
            raise Exception('Conf file already contains this device.\n\
In order to remove it, manually delete the [%s] section' % section_name)


def modify_conf_file(conf_filename, serial, drive_letter, backup_folder):
    is_record_exists(conf_filename, serial)

    section_name = '%s_%s' % (drive_letter, serial)
    parser.read(conf_filename)

    parser.add_section(section_name)
    parser.set(section_name, 'serial', serial)
    parser.set(section_name, 'dst_folder', backup_folder)
    parser.set(section_name, 'last_backup_time', '0')
    parser.set(section_name, 'drive_letter', drive_letter)

    with open(conf_filename, 'w') as conf_file:
        parser.write(conf_file)


def add_new_record(drive_letter, backup_folder):
    if not is_removable_drive(drive_letter):
        raise Exception('You have selected a non-removable drive.\n\
Please select a removable device.')
    serial = get_serial_by_drive_letter(drive_letter)
    if serial is None:
        raise Exception('There has occured some kind of error with\n\
getting the device serial number by its drive letter')
    modify_conf_file(conf_filename, serial, drive_letter, backup_folder)
    if QMessageBox.Yes == QMessageBox.question(None, 'hooray!', '''Congrats!
Your backup setting have been updated.
Would you like to start the backup process right now?''', QMessageBox.Yes, QMessageBox.No):
        log_fw = 'stdout'

        wait_lbl = QLabel("Please wait for the backup process to finish")
        layout = QVBoxLayout()
        dlg = QDialog()
        dlg.setWindowFlags(Qt.Dialog | Qt.Desktop)
        dlg.setLayout(layout)
        layout.addWidget(wait_lbl)

        t = Thread(target=dlg.exec_)
        t.start()

        run(serial)
        dlg.close()
