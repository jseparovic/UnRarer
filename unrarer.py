#!/usr/bin/python

from os.path import isdir, basename
from sys import argv
import traceback
from time import sleep
from daemons.prefab import run
from libs.common import *
import logging

LOG_LEVEL = logging.INFO
LOG_FILE = '/var/log/unrarer.log'
SLEEP_SECONDS = 5
UNRARER_CONF_FILE = '/etc/unrarer.conf'
PID_FILE = "/var/run/unrarer.pid"


class UnRarer(run.RunDaemon):
    def __init__(self, pidfile, scanpath):
        super(UnRarer, self).__init__(pidfile=pidfile)
        self.scanpath = scanpath

    def scan(self):
        logging.debug("Scanning %s" % self.scanpath)
        dirs = [f for f in listdir(self.scanpath)]

        for directory in dirs:
            path = join(self.scanpath, directory)
            if isdir(path):
                logging.debug("Searching in %s" % path)
                files = [f for f in listdir(path)]
                logging.debug("Files: %s" % files)
                for f in files:
                    file = join(path, f)
                    logging.debug("Checking file: " + file)
                    if file.endswith(".rar"):
                        logging.info("Found rar file: " + file + ". Extracting ...")
                        cmd_res = call_command(['unrar', 'x', '-o+', file, path])
                        if cmd_res.exit_code == 0:
                            logging.info("Done! Removing rar files")
                            purge(path, '.*\\.rar$')
                            purge(path, '.*\\.r[0-9]{2}$')
                        else:
                            logging.error("Error unraring %s: %s" % (file, cmd_res.output))

    def run(self):
        logging.info("UnRarer to scan %s for directories containing rar files" % self.scanpath)
        while True:
            try:
                self.scan()

            except Exception:
                logging.error('An Unhandled Exception occurred:\n' + traceback.format_exc())

            finally:
                try:
                    sleep(SLEEP_SECONDS)
                except (OSError, IOError) as ex:
                    logging.warn("Exception caught as UnRarer received termination orders from daemon. "
                                 "Exception = %s", str(ex))


if __name__ == '__main__':
    action = argv[1]
    setup_logging(log_file=LOG_FILE, level=LOG_LEVEL)
    scan_path = get_config_var(UNRARER_CONF_FILE, "main", "SCAN_PATH")
    d = UnRarer(pidfile=PID_FILE, scanpath=scan_path)

    if action == "start":
        logging.info("Starting UnRarer")
        d.start()

    elif action == "stop":
        d.stop()

    elif action == "restart":
        d.restart()

