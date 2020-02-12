# -*- encoding=utf-8 -*-
import os
import time
import pathlib
import logging
import sqlite3
import win32api
import win32con
import datetime
import threading
import configparser


logger_level = logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(logger_level)
log_path = os.path.join(pathlib.Path('.').absolute(), 'log.txt')
handler = logging.FileHandler(log_path)
handler.setLevel(logger_level)
formatter = logging.Formatter('%(asctime)s - %(filename)s - %(funcName)s[%(lineno)d]:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

title = '仓库货物管理系统'
DB_NAME = 'good.db'
DETAIL_TB = 'goods_detail'
WAREHOUSE_TB = 'warehouse'
USER_TB = 'user'
MATERIEL_TB = 'materiel'
database_dir = pathlib.Path.joinpath(pathlib.Path('.').absolute(), 'database').__str__()
if not os.path.exists(database_dir):
    os.mkdir(database_dir)
    win32api.SetFileAttributes(database_dir, win32con.FILE_ATTRIBUTE_HIDDEN)


config_json = {
    "IN": {

    },
    "OUT": {

    }
}


class Config(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.__conf_file = pathlib.Path.joinpath(pathlib.Path('.').absolute(), 'database', 'conf.ini')
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


class DataBase(object):
    _instance_lock = threading.Lock()

    def __init__(self):
        self.__db_path = os.path.join(pathlib.Path().absolute(), 'database', DB_NAME)
        self.__conn = sqlite3.connect(self.__db_path)
        try:
            self.__cursor = self.__conn.cursor()
        except Exception as e:
            logger.debug(f'create db failed {e}')
            self.__conn.rollback()
            self.close()
        self.init()

    def __new__(cls, *args, **kwargs):
        if not hasattr(DataBase, '_instance'):
            with DataBase._instance_lock:
                if not hasattr(DataBase, '_instance'):
                    DataBase._instance = object.__new__(cls)
        return DataBase._instance

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def init(self):
        detail_tb_sentences = f"""
            CREATE TABLE IF NOT EXISTS {DETAIL_TB} (
                NUM INTEGER PRIMARY KEY,
                DATE CHAR(64) NOT NULL,
                OPERATE CHAR(8) NOT NULL,
                NAME CHAR(128) NOT NULL,
                QUANTITY INTEGER,
                PICKER CHAR(128)
            )
        """
        warehouse_tb_sentences = f"""
            CREATE TABLE IF NOT EXISTS {WAREHOUSE_TB} (
                NUM INTEGER PRIMARY KEY,
                NAME CHAR(128) NOT NULL,
                QUANTITY INTEGER
            )
        """
        materiel_tb_sentences = f"""
            CREATE TABLE IF NOT EXISTS {MATERIEL_TB} (
                NUM INTEGER PRIMARY KEY,
                NAME CHAR(128) NOT NULL
            )
        """
        self.create_tb(detail_tb_sentences)
        self.create_tb(warehouse_tb_sentences)
        self.create_tb(materiel_tb_sentences)

    def close(self):
        self.__conn.close()

    def insert_column(self, tb_name, column_name, data_type):
        """
        insert a column to tb.
        if called, all operation related to db must be fitted.
        :param tb_name:
        :param column_name:
        :param data_type:
        :return:
        """
        sentences = f"""
            ALTER TABLE {tb_name} ADD COLUMN {column_name} {data_type};
        """
        print(sentences)
        self.commit(sentences)

    def insert_detail(self, date, name, operate, quantity, picker):
        sentences = f"""
            INSERT INTO {DETAIL_TB} VALUES(NULL, '{date}', '{operate}', '{name}', '{quantity}', '{picker}');
        """
        self.commit(sentences)

    def insert_warehouse(self, name, quantity):
        sentences = f"""
             INSERT INTO {WAREHOUSE_TB} VALUES(NULL, '{name}', '{quantity}');
        """
        self.commit(sentences)

    def update(self, tb_name, condition_key, condition_value, new_key, new_value):
        sentences = f"""
            UPDATE {tb_name} SET {new_key}='{new_value}' WHERE {condition_key}='{condition_value}';
        """
        self.commit(sentences)

    def revert(self, tb_name):
        sentences = f"""
            SELECT * FROM {tb_name} order by NUM desc limit 0,1;
        """
        self.__cursor.execute(sentences)
        result = self.__cursor.fetchall()
        return result

    def delete(self, tb_name, key, value):
        sentences = f"""
            DELETE FROM {tb_name} WHERE {key}='{value}';
        """
        self.commit(sentences)

    def insert_materiel(self, name):
        sentences = f"""
             INSERT INTO {MATERIEL_TB} VALUES(NULL, '{name}');
        """
        self.commit(sentences)

    def query(self, tb_name, vague=False, **kwargs):
        if not vague:
            options = ["WHERE"]
            for key in kwargs:
                options.append(f"{key}='{kwargs[key]}'")
                options.append('and')

            options.pop()
            sentences = f"""
                SELECT * FROM {tb_name} {' '.join(options)};
            """
        else:
            key = list(kwargs.keys()).pop()
            value = list(kwargs.values()).pop()
            sentences = f"""
                SELECT * FROM {tb_name} WHERE {key} LIKE '%{value}%';
            """
        self.__cursor.execute(sentences)
        result = self.__cursor.fetchall()
        logger.debug(f'{sentences}::query result:{result}')
        return result

    def create_tb(self, sql_sentences):
        self.commit(sql_sentences)

    def commit(self, sentences):
        try:
            self.__cursor.execute(sentences)
            self.__conn.commit()
        except Exception as e:
            logger.error(f'execute {sentences} error:{e}')
        finally:
            logger.debug(f'execute sqlite sentences:{sentences}')


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
