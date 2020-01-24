
from os import listdir, remove
from os.path import join
from re import search
import tempfile
import subprocess
import logging
import threading
import ConfigParser


def setup_logging(log_file, level, threads=False):
    root_logger = logging.getLogger()
    root_logger.handlers = []
    log_format = '%(asctime)s - %(levelname)s'
    if threads:
        log_format += ' - %(threadName)s'
    log_format += ' - %(message)s'
    log_formatter = logging.Formatter(log_format)
    # log to file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(level)


def purge(dir, pattern):
    for f in listdir(dir):
        if search(pattern, f):
            file = join(dir, f)
            logging.info("Removing file: " + file)
            remove(file)


class CmdResult:
    def __init__(self, exit_code, output, timed_out=False):
        self.exit_code = exit_code
        self.output = output
        self.timed_out = timed_out


class TimerResult:
    def __init__(self):
        self.timed_out = False

    def set_timed_out(self, timed_out):
        self.timed_out = timed_out

    def get_timed_out(self):
        return self.timed_out


def kill(p, argv, timer_result):
    timer_result.set_timed_out(True)
    logging.info("Command has timed out %s" % argv)
    p.kill()


def call_command(argv, timeout=0):
    """ Execute the command """
    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(argv, stdout=tempf, stderr=tempf)
        timer_result = TimerResult()

        if timeout > 0:
            timer = threading.Timer(timeout, kill, [proc, argv, timer_result])
            timer.start()
        exit_code = proc.wait()
        if timeout > 0:
            timer.cancel()
        tempf.seek(0)
        output = tempf.read().decode('utf-8')
    logging.debug("Command timed out=%s" % timer_result.get_timed_out())
    logging.debug("Command exit code: %s" % exit_code)
    logging.debug("Command output:\n%s" % output)

    return CmdResult(exit_code, output, timer_result.get_timed_out())


def get_config_var(file, section, variable):
    config = ConfigParser.RawConfigParser()
    config.read(file)
    return config.get(section, variable)


