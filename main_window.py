# -*- encoding=utf-8 -*-
"""
main window
create: 2020/02/03 18:00
author: zhenchao
"""
import os
import json
import pathlib
import datetime
from utils import Config
from utils import Thread
from utils import config_json
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, \
    QLineEdit, QComboBox, QTextEdit, QMessageBox, QDateTimeEdit, QDialog


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__type = ['--新增--']
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
        self.__last_typo = ''
        self.__last_num = 0
        self.__last_method = ''
        self.__total_text_edit = None
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
        self.__combobox.setCurrentIndex(0)
        self.__combobox.activated.connect(self.show_dialog)
        # self.__combobox.highlighted.connect(self.show_dialog)

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
        self.__total_text_edit = QTextEdit(self)
        self.__total_text_edit.setFontPointSize(15)
        self.update_total_data()
        top_mid_v_box.addWidget(self.__total_text_edit)

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
        # self.__text_edit_label.setEnabled(False)
        self.__text_edit_label.setFontPointSize(20)
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

    def update_total_data(self):
        json_data = self.load_json_file(total=True)
        _type_list = []
        for typo in json_data['IN'].keys():
            _type_list.append(f'{typo}:{json_data["IN"][typo]}')

        self.__total_text_edit.setText('当前仓库物料清单:\n'+'\n'.join(_type_list))
        cursor = self.__total_text_edit.textCursor()
        pos = len(self.__total_text_edit.toPlainText())
        cursor.setPosition(pos-1)
        self.__total_text_edit.setTextCursor(cursor)

    def init_total_data(self):
        pass

    def run(self):
        self.show()

    def load_json_file(self, total=False):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        datebase_dir = os.path.join(pathlib.Path('.').absolute(), 'datebase')
        if not os.path.exists(datebase_dir):
            os.mkdir(datebase_dir)
        if total:
            json_file = os.path.join(datebase_dir, 'total')
        else:
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

    def dump_json_file(self, json_data, total=False):
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        datebase_dir = os.path.join(pathlib.Path('.').absolute(), 'datebase')
        if total:
            json_file = os.path.join(datebase_dir, "total")
        else:
            json_file = os.path.join(datebase_dir, now)
        with open(json_file, 'w+', encoding='gbk') as fp:
            json.dump(json_data, fp)

    def fill_data(self, method, typo, num, json_data, total=False):
        if method == "进货":
            method = 'IN'
        elif method == "出货":
            method = "OUT"
        else:
            return
        try:
            old_num = int(json_data[method][typo])
        except KeyError:
            old_num = 0
        except ValueError:
            old_num = 0

        # current day
        new_num = old_num + int(num)
        json_data[method][typo] = str(new_num)
        self.dump_json_file(json_data)

        # total
        json_data = self.load_json_file(total=True)
        try:
            old_num = int(json_data['IN'][typo])
        except KeyError:
            old_num = 0
        except ValueError:
            old_num = 0
        if method == 'OUT':
            new_num = old_num - int(num)
            if new_num < 0:
                self.show_warning_dialog(f'当前操作导致{typo}物料数量小于0')
                return
        else:
            new_num = old_num + int(num)
        json_data['IN'][typo] = str(new_num)
        self.dump_json_file(json_data, total=True)
        self.update_total_data()

    def _check_num(self, num):
        try:
            num = int(num)
        except ValueError:
            self.show_warning_dialog("数量必须是数字")
            return False
        return True

    def btn_cb(self, text):
        json_data = self.load_json_file()
        if text == "ok":
            typo = self.__combobox.currentText()
            method = self.__method_combobox.currentText()
            num = self.__num_edit.text()
            if not self._check_num(num):
                return
            self.__last_typo = typo
            self.__last_method = method
            self.__last_num = int(num)
            self.__cache_list.append(f'【{method}】:{typo}:{num}')
            self.__text_edit_label.setPlainText('\n'.join(self.__cache_list))
            self.fill_data(method, typo, num, json_data)
        elif text == "cancel":
            if self.__last_num == '0':
                return
            self.__cache_list.append(f'【消除】:{self.__last_typo}:{self.__last_num}')
            self.__text_edit_label.setText('\n'.join(self.__cache_list))
            self.fill_data(self.__last_method, self.__last_typo, str(0-int(self.__last_num)), json_data)

            self.__last_num = '0'
            self.__last_typo = self.__last_method = ''

        elif text == "add":
            new_type = self.__new_type_edit.text()
            # num = self.__new_num_add.text()
            # if not self._check_num(num):
            #     return
            self.__type.insert(-1, new_type)
            self.__type = list({}.fromkeys(self.__type).keys())
            self.__combobox.clear()
            self.__combobox.addItems(self.__type)
            self.__combobox.setCurrentText(new_type)
            # self.__last_num = int(num)
            self.__cache_list.append(f'【新增】:{new_type}')
            self.__text_edit_label.setText('\n'.join(self.__cache_list))
            # self.fill_data('进货', new_type, num, json_data)
        elif text == "search":
            start_date = self.__start_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]
            end_date = self.__end_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]

            self.__text_edit_label.clear()
            self.__text_edit_label.setPlainText(f'{start_date}至{end_date}材料统计情况')

        cursor = self.__text_edit_label.textCursor()
        pos = len(self.__text_edit_label.toPlainText())
        cursor.setPosition(pos - 1)
        self.__text_edit_label.setTextCursor(cursor)

    def cancel_thread(self):
        if self.__thread:
            self.__thread.cancel()

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

    def show_warning_dialog(self, text):
        dialog = QDialog(self)
        v_box = QVBoxLayout(self)

        warning_label = QLabel(text)
        v_box.addWidget(warning_label)
        dialog.setLayout(v_box)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def show_dialog(self):
        if self.__combobox.currentText() != "--新增--":
            return
        dialog = QDialog(self)
        v_box = QVBoxLayout(self)

        add_label = QLabel('新增材料:')
        name_label = QLabel('材料名称')
        ok_btn = QPushButton('新增')
        ok_btn.clicked.connect(lambda: self.btn_cb('add'))

        self.__new_type_edit = QLineEdit()
        h_box = QHBoxLayout(self)
        h_box.addWidget(add_label)
        h_box.addStretch(1)
        v_box.addLayout(h_box)

        h_box = QHBoxLayout(self)
        h_box.addWidget(name_label)
        h_box.addWidget(self.__new_type_edit)
        h_box.addStretch(1)
        v_box.addLayout(h_box)
        v_box.addStretch(1)

        h_box = QHBoxLayout(self)
        h_box.addStretch(1)
        h_box.addWidget(ok_btn)
        v_box.addLayout(h_box)

        dialog.setLayout(v_box)
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()
