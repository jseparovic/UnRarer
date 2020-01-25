# UnRarer (systemd service)
service to automatically unrar files given a specific path of directories
```
this service scans through directories at given path and looks for rar files
if a rar file is found, it will extract the rar and then delete the rar files

to install just run:
   ./install.sh SCAN_PATH
where SCAN_PATH in the path where your directories to scan are

the install script will also run "easy_install daemons", so "yum install -y python-setuptools" if you're on centos 7

eg. 
   ./install.sh /mnt/torrents/completed

log file is written to:
    /var/log/unrarer.log

Note: it only goes into 1 level of directories. 

ie.
SCANPATH
   -Dir
     -rar file

not:
SCANPATH
   -Dir
     -SubDir
       -rar file

Would need a change to keep searching more levels down

```
