# FlashBackup

## Executive summary
The application aims to back up data from removable devices to the connected PC every fixed amount of time.

## Installation and execution
In order to run the service, type in the following lines:
```
python detector.py install
python detector.py start
```
If there is a need to register a new device, type in
```
python main.py
```
and use the intuitive UI.

#### Requirements:
 * Windows (tested on Windows 7 and Windows 10)
 * Python 3
 * Additional python packages:
  - PyQt5
  - pywin32
  - wmi
  - configparser


## Files
 * main.py - initializes and starts the UI.
 * UI.py - the user interface (see figure below)
 * detector.py - starts a windows service that runs a backup procedure (if required) every time a registered flash drive detected *note* The operation determining whether a backup should be ran, and running it is in the jurisdiction of the **copyer.py** module
 * reset.bat - restarts the windows service specified in *detector.py*
 * copyer.py - responsible for determination whether a backup for the given device is required (by querying the log), and doing the actual backup.
 * controller.py - responsible for OS-related queries such as getting a serial number by a drive letter, or check whether a mounted device is a removable drive.
 * flashBackup.ini - the file that stores the configurations.
 * utils.py - various helper functions.

 ![](/demo.jpeg?raw=true "")
