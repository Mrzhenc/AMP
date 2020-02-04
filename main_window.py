# -*- encoding=utf-8 -*-
"""
main window
create: 2020/02/03 18:00
author: zhenchao
"""
import os
import sys
import json
import PyQt5
import pathlib
import datetime
import threading
from utils import Config
from utils import Thread
from utils import config_json
from PyQt5.QtCore import Qt, QTime, QDate, QDateTime
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, \
    QLineEdit, QComboBox, QTextEdit, QMessageBox, QCalendarWidget, QDateTimeEdit


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__type = ['Type1', 'Type2', 'Type3', 'Type4']
        self.__username_entry = None
        self.__password_entry = None
        self.__text_edit_label = None
        self.__method_combobox = None
        self.__num_edit = None
        self.__combobox = None
        self.__thread = None
        self.__new_type_edit = None
        self.__new_num_add = None
        self.__start_calendar_widget = None
        self.__end_calendar_widget = None
        self.__conf = Config()
        self.__cache_list = []
        self.init_ui()

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle('AMP')

        # top left widget
        v_box = QVBoxLayout(self)
        top_left = QFrame(self)
        time_label = QLabel()
        self.__thread = Thread(time_label)
        self.__thread.start()
        ok_btn = QPushButton('确定')
        cancel_btn = QPushButton('消除')
        ok_btn.clicked.connect(lambda: self.btn_cb('ok'))
        cancel_btn.clicked.connect(lambda: self.btn_cb('cancel'))
        type_label = QLabel('材料')
        num_label = QLabel('数量')
        method_label = QLabel('类型')
        self.__method_combobox = QComboBox(self)
        self.__method_combobox.addItems(['进货', '出货'])
        self.__num_edit = QLineEdit()
        self.__combobox = QComboBox(self)
        self.__combobox.addItems(self.__type)

        top_left_v_box = QVBoxLayout()
        # time
        top_left_v_box.addWidget(time_label)

        # method
        h_box = QHBoxLayout(self)
        h_box.addWidget(method_label)
        h_box.addWidget(self.__method_combobox)
        h_box.addStretch(1)
        top_left_v_box.addLayout(h_box)

        # type
        h_box = QHBoxLayout(self)
        h_box.addWidget(type_label)
        h_box.addWidget(self.__combobox)
        h_box.addStretch(1)
        top_left_v_box.addLayout(h_box)

        # num
        h_box = QHBoxLayout(self)
        h_box.addWidget(num_label)
        h_box.addWidget(self.__num_edit)
        h_box.addStretch(1)
        top_left_v_box.addLayout(h_box)
        top_left_v_box.addStretch(1)

        # btn
        h_box = QHBoxLayout(self)
        h_box.addStretch(1)
        h_box.addWidget(cancel_btn)
        h_box.addWidget(ok_btn)

        v_box.addLayout(top_left_v_box)
        v_box.addLayout(h_box)
        top_left.setFrameShape(QFrame.StyledPanel)
        top_left.setLayout(v_box)

        # top middle widget
        top_mid_v_box = QVBoxLayout(self)
        top_mid = QFrame(self)
        type_label = QLabel('新增类型')
        self.__new_type_edit = QLineEdit()
        num_label = QLabel('新增数量')
        self.__new_num_add = QLineEdit()
        add_btn = QPushButton('新增')
        add_btn.clicked.connect(lambda: self.btn_cb('add'))

        # new type
        h_box = QHBoxLayout(self)
        h_box.addWidget(type_label)
        h_box.addWidget(self.__new_type_edit)
        h_box.addStretch(1)
        top_mid_v_box.addLayout(h_box)

        # new num
        h_box = QHBoxLayout(self)
        h_box.addWidget(num_label)
        h_box.addWidget(self.__new_num_add)
        h_box.addStretch(1)
        top_mid_v_box.addLayout(h_box)
        top_mid_v_box.addStretch(1)

        # add btn
        mid_h_box = QHBoxLayout(self)
        mid_h_box.addStretch(1)
        mid_h_box.addWidget(add_btn)
        top_mid_v_box.addLayout(mid_h_box)

        top_mid.setFrameShape(QFrame.StyledPanel)
        top_mid.setLayout(top_mid_v_box)

        # top right widget
        top_right = QFrame(self)
        _label = QLabel('月度统计')
        search_btn = QPushButton('开始统计')
        search_btn.clicked.connect(lambda: self.btn_cb('search'))
        self.__start_calendar_widget = QDateTimeEdit(QDate.currentDate(), self)
        self.__start_calendar_widget.setCalendarPopup(True)
        self.__start_calendar_widget.setDisplayFormat("yyyy-MM-dd")
        self.__end_calendar_widget = QDateTimeEdit(QDate.currentDate(), self)
        self.__end_calendar_widget.setCalendarPopup(True)
        self.__end_calendar_widget.setDisplayFormat("yyyy-MM-dd")
        start_date_label = QLabel('起始日期')
        end_date_label = QLabel('结束日期')

        v_box = QVBoxLayout(self)
        v_box.addWidget(_label)

        h_box = QHBoxLayout(self)
        h_box.addWidget(start_date_label)
        h_box.addWidget(self.__start_calendar_widget)
        h_box.addStretch(1)
        v_box.addLayout(h_box)

        h_box = QHBoxLayout(self)
        h_box.addWidget(end_date_label)
        h_box.addWidget(self.__end_calendar_widget)
        h_box.addStretch(1)
        v_box.addLayout(h_box)
        v_box.addStretch(1)

        h_box = QHBoxLayout(self)
        h_box.addStretch(1)
        h_box.addWidget(search_btn)
        v_box.addLayout(h_box)

        top_right.setFrameShape(QFrame.StyledPanel)
        top_right.setLayout(v_box)

        # bottom widget
        v_box = QVBoxLayout(self)
        self.__text_edit_label = QTextEdit(self)
        self.__text_edit_label.setEnabled(False)
        v_box.addWidget(self.__text_edit_label)
        bottom = QFrame(self)
        # bottom.resize(300, 200)
        bottom.setFrameShape(QFrame.StyledPanel)
        bottom.setLayout(v_box)

        h_splitter = QSplitter(Qt.Horizontal)
        h_splitter.addWidget(top_left)
        h_splitter.addWidget(top_mid)
        h_splitter.addWidget(top_right)

        v_splitter = QSplitter(Qt.Vertical)
        v_splitter.addWidget(h_splitter)
        v_splitter.addWidget(bottom)

        h_box = QHBoxLayout(self)
        h_box.addWidget(v_splitter)
        self.setLayout(h_box)
        # self.setGeometry(300, 300, 300, 200)

    def run(self):
        self.show()

    def load_json_file(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        datebase_dir = os.path.join(pathlib.Path('.').absolute(), 'datebase')
        if not os.path.exists(datebase_dir):
            os.mkdir(datebase_dir)
        json_file = os.path.join(datebase_dir, now)
        if not os.path.exists(json_file):
            with open(json_file, 'w+', encoding='gbk'):
                return config_json
        with open(json_file, 'r', encoding='gbk') as fp:
            try:
                return json.load(fp)
            except json.decoder.JSONDecodeError as e:
                print(f'load {json_file} Error:{e}')
                return config_json

    def dump_json_file(self, json_data):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        datebase_dir = os.path.join(pathlib.Path('.').absolute(), 'datebase')
        json_file = os.path.join(datebase_dir, now)
        with open(json_file, 'w+', encoding='gbk') as fp:
            json.dump(json_data, fp)

    def fill_data(self, method, typo, num, json_data):
        if method == "进货":
            method = 'IN'
        elif method == "出货":
            method = "OUT"
        try:
            old_num = int(json_data[method][typo])
        except KeyError:
            old_num = 0
        except ValueError:
            old_num = 0

        new_num = old_num + int(num)
        json_data[method][typo] = str(new_num)
        self.dump_json_file(json_data)

    def btn_cb(self, text):
        json_data = self.load_json_file()
        if text == "ok":
            typo = self.__combobox.currentText()
            method = self.__method_combobox.currentText()
            num = self.__num_edit.text()
            self.__cache_list.append(f'【{method}】:{typo}:{num}')
            self.__text_edit_label.setText('\n'.join(self.__cache_list))
            self.fill_data(method, typo, num, json_data)
        elif text == "cancel":
            try:
                self.__cache_list.pop()
            except IndexError:
                pass
            self.__text_edit_label.setText('\n'.join(self.__cache_list))

        elif text == "add":
            new_type = self.__new_type_edit.text()
            self.__type.append(new_type)
            self.__type = list({}.fromkeys(self.__type).keys())
            self.__combobox.clear()
            self.__combobox.addItems(self.__type)
            typo = self.__new_type_edit.text()
            num = self.__new_num_add.text()
            self.__cache_list.append(f'【新增】:{typo}:{num}')
            self.__text_edit_label.setText('\n'.join(self.__cache_list))
        elif text == "search":
            start_date = self.__start_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]
            end_date = self.__end_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]
            print(start_date, end_date)

            self.__text_edit_label.clear()
            self.__text_edit_label.setText(f'{start_date}至{end_date}材料统计情况')

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QMessageBox.question(self, '本程序', "是否要退出程序？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.__thread:
                self.__thread.cancel()
            event.accept()

        else:
            event.ignore()
