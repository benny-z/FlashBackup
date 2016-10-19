import time
import os, shutil
from os import sep, chdir, rename, remove
from os.path import join, getsize, exists
from configparser import SafeConfigParser
import datetime
from sys import argv
import traceback
from utils import log, attempt_with_timeout, get_drive_letter_by_device_serial, log_fw, conf_filename, wait_for_file_to_appear
from time import sleep

max_days_delta = 7
parser = SafeConfigParser()

def do_backup(src_base, dst_base):
	log('starting do_backup src: %s; dst:%s' % (src_base, dst_base))
	chdir(src_base)
	for root, dirs, files in os.walk(src_base):
		for filename in files:
			src_file_fullpath = unicode(join(root, filename))
			dst_directory = unicode(root.replace(src_base, dst_base))
			dst_file_fullpath = unicode(join(dst_directory, filename))
			
			if not exists(dst_directory):
				os.makedirs(dst_directory)
			if not exists(dst_file_fullpath) or getsize(src_file_fullpath) != getsize(dst_file_fullpath):
				try:
					if exists(dst_file_fullpath):
						dst_file_tmp_fullpath = "%s.being.copied" % dst_file_fullpath
						shutil.copy2(src_file_fullpath, dst_file_tmp_fullpath)
						rename(dst_file_fullpath, "%s.old" % dst_file_fullpath)
						rename(dst_file_tmp_fullpath, dst_file_fullpath)
						remove("%s.old" % dst_file_fullpath)
					else:
						shutil.copy2(src_file_fullpath, dst_file_fullpath)
					if 'stdout' == log_fw:
						print('copied %s' % unicode(src_file_fullpath))
				except:
					log(traceback.format_exc())
	log('backup done')

def is_backup_required(last_update_datetime):
	last_update_datetime = int(last_update_datetime)
	if 0 == last_update_datetime:
		return True
	last_backup_datetime = datetime.datetime.fromordinal(last_update_datetime)
	current_datetime = datetime.datetime.now()
	delta = current_datetime - last_backup_datetime
	return delta.days >= max_days_delta

def get_device_info(conf_filename, serial):
	parser.read(conf_filename)
	for section_name in parser.sections():
		# just checking that all the required options are in place
		if all([parser.has_option(section_name, option) for option in ('dst_folder', 'serial', 'last_backup_time')]): 
			if parser.get(section_name, 'serial').lower() == serial.lower():
				return section_name, parser.items(section_name)
	return None, None

def update_conf_file(conf_filename, conf_section_name, drive_letter):
	last_update = str(datetime.datetime.toordinal(datetime.datetime.now()))
	parser.set(conf_section_name, 'last_backup_time', last_update)
	parser.set(conf_section_name, 'drive_letter', drive_letter)
	with open(conf_filename, 'w') as conf_file:
		parser.write(conf_file)

def run(serial):
	conf_section_name, device_info = get_device_info(conf_filename, serial)

	if None in (conf_section_name, device_info):
		log('there has occured some exception in finding the given drive in the conf file for the serial: %s' % (serial))
		return

	dst_base = [value for name, value in device_info if name == 'dst_folder'][0]
	last_update = [value for name, value in device_info if name == 'last_backup_time'][0]
	drive_letter = [value for name, value in device_info if name == 'drive_letter']

	try:
		temp_drive_letter = attempt_with_timeout(get_drive_letter_by_device_serial, timeout = 60, time_delta = 1)(serial)
		drive_letter = temp_drive_letter
	except:
		if [] == drive_letter:
			log('failed to get the drive letter')
			return
		drive_letter = drive_letter[0]	
		

	if is_backup_required(last_update):
		if not drive_letter.endswith(sep): drive_letter = drive_letter + sep
		if not dst_base.endswith(sep): dst_base = dst_base + sep

		log('waiting for the PC to recognize %s' % drive_letter)
		if False == wait_for_file_to_appear(drive_letter):
			log('request timeout, the file %s does not exist' % drive_letter)
			return

		try:
			attempt_with_timeout(do_backup, timeout = 600, time_delta = 10)(drive_letter, dst_base)
		except Exception as e:
			log('the following exception has occured during the backup process:\n%s' % str(e))
			return

		update_conf_file(conf_filename, conf_section_name, drive_letter)

if '__main__' == __name__:
	log_fw = 'stdout'
	serial = argv[1]
	if len(argv) > 2:
		conf_filename = argv[2]

	run(serial)
