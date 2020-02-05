# -*- encoding=utf-8 -*-
import os
import time
import pathlib
import logging
import datetime
import threading
import configparser


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
log_path = os.path.join(pathlib.Path('.').absolute(), 'log.txt')
handler = logging.FileHandler(log_path)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s[%(lineno)d]:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

title = '仓库货物管理系统'

config_json = {
    "IN": {

    },
    "OUT": {

    }
}


class Config(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.__conf_file = pathlib.Path.joinpath(pathlib.Path('.').absolute(), 'conf.ini')
        self.__conf = configparser.ConfigParser()
        if not os.path.exists(self.__conf_file):
            self.__conf['User'] = {}
            self.__conf['List'] = {}
            self.write()
        self.__conf.read(self.__conf_file)

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, '_instance'):
            with Config._instance_lock:
                if not hasattr(Config, '_instance'):
                    Config._instance = object.__new__(cls)
        return Config._instance

    def set(self, section, **kwargs):
        for args in kwargs:
            self.__conf.set(section, args, kwargs[args])
        self.write()

    def write(self):
        with open(self.__conf_file, 'w', encoding='gbk') as fp:
            self.__conf.write(fp)

    def get(self, section, option):
        try:
            return self.__conf[section][option]
        except KeyError:
            logger.debug(f'No section:{section} or option:{option} get')
            return ''


# class DataBase(sqlite3):
#     def __init__(self):
#         super(sqlite3, self).__init__()


class Thread(threading.Thread):
    def __init__(self, time_label):
        super(Thread, self).__init__()
        self.label = time_label
        self.cancelled = False

    def run(self):
        while True:
            if self.cancelled:
                return
            time.sleep(1)
            now = datetime.datetime.now()
            self.label.setText(str(now.strftime("%Y-%m-%d %H:%M:%S")))

    def cancel(self):
        self.cancelled = not self.cancelled


def get_date_range(start, end):
    dates = []
    dt = datetime.datetime.strptime(start, "%Y-%m-%d")
    date = start[:]
    while date <= end:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    return dates
