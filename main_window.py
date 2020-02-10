# -*- encoding=utf-8 -*-
"""
main window
create: 2020/02/03 18:00
author: zhenchao
"""
import json
import copy
from utils import *
from collections import namedtuple
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSplitter, \
    QLineEdit, QComboBox, QTextEdit, QMessageBox, QDateTimeEdit, QDialog


class MainWindow(QWidget):
    _warehouse_template = namedtuple('Warehouse', 'num name quantity')
    _detail_template = namedtuple('Detail', 'num date operate name quantity picker')
    _materiel_template = namedtuple('Materiel', 'num name')

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.__type = []
        self.__username_entry = None
        self.__password_entry = None
        self.__text_edit_label = None
        self.__method_combobox = None
        self.__num_edit = None
        self.__combobox = None
        self.__thread = None
        self.__new_type_edit = None
        self.__to_edit = None
        self.__to_label = None
        self.__new_num_add = None
        self.__start_calendar_widget = None
        self.__end_calendar_widget = None
        self.__conf = Config()
        self.__db = DataBase()
        self.__cache_list = []
        self.__last_typo = ''
        self.__last_num = 0
        self.__last_method = ''
        self.__last_op_date = ''
        self.__total_text_edit = None
        self.get_conf_list()
        self.init_ui()
        self.update_total_data()
        self.change_to_widget_status()

    def get_conf_list(self):
        # database
        _typo_list = self.__db.query(MATERIEL_TB)
        for _typo in _typo_list:
            self.__type.append(_typo[1])
        self.__type.extend(['--新增--'])

        # conf file
        # _typos_str = self.__conf.get('List', 'typo')
        # if _typos_str == '':
        #     self.__type.extend(['--新增--'])
        #     return
        # _typos_list = _typos_str.split(':')
        # self.__type.extend(_typos_list)

    def set_conf_list(self, new_type):
        # self.__conf.set('List', typo=':'.join(self.__type))
        self.__db.insert_materiel(new_type)

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle(title)

        # top left widget
        v_box = QVBoxLayout(self)
        top_left = QFrame(self)
        time_label = QLabel()
        self.__thread = Thread(time_label)
        self.__thread.start()
        ok_btn = QPushButton('确定')
        cancel_btn = QPushButton('撤销')
        cancel_btn.setToolTip('撤销最后一次操作')
        ok_btn.clicked.connect(lambda: self.btn_cb('ok'))
        cancel_btn.clicked.connect(lambda: self.btn_cb('cancel'))
        type_label = QLabel('材料')
        num_label = QLabel('数量')
        method_label = QLabel('类型')
        self.__to_label = QLabel('去向')
        self.__method_combobox = QComboBox(self)
        self.__method_combobox.addItems(['进货', '出货'])
        self.__method_combobox.activated.connect(self.change_to_widget_status)
        self.__num_edit = QLineEdit()
        self.__to_edit = QLineEdit()
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

        # to
        h_box = QHBoxLayout(self)
        h_box.addWidget(self.__to_label)
        h_box.addWidget(self.__to_edit)
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
        self.__total_text_edit.setReadOnly(True)
        self.__total_text_edit.setFontPointSize(13)
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
        self.__text_edit_label.setReadOnly(True)
        self.__text_edit_label.setFontPointSize(12)
        v_box.addWidget(self.__text_edit_label)
        bottom = QFrame(self)
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

    def change_to_widget_status(self):
        if self.__method_combobox.currentText() == '进货':
            self.__to_label.hide()
            self.__to_edit.hide()
        else:
            self.__to_label.show()
            self.__to_edit.show()

    def update_total_data(self):
        _type_list = []
        result_list = self.__db.query(WAREHOUSE_TB)
        if not result_list:
            # self.show_warning_dialog(f'查询失败!')
            logger.error(f'current warehouse is empty')
            return
        for result in result_list:
            warehouse_info = MainWindow._warehouse_template._make(result)
            _type_list.append(f'{warehouse_info.name}:{warehouse_info.quantity}')

        self.__total_text_edit.setText('当前仓库物料清单:\n'+'\n'.join(_type_list))
        cursor = self.__total_text_edit.textCursor()
        pos = len(self.__total_text_edit.toPlainText())
        cursor.setPosition(pos-1)
        self.__total_text_edit.setTextCursor(cursor)

    def init_total_data(self):
        pass

    def run(self):
        self.show()

    def fill_data(self, method, typo, num, picker):

        current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.__last_op_date = current_date
        picker_str = ''
        if picker:
            picker_str = f'提货人:{picker}'

        # update warehouse db
        res = self.__db.query(WAREHOUSE_TB, NAME=typo)
        if not res:
            self.__db.insert_warehouse(typo, num)
        else:
            try:
                old_num = int(res[0][2])
                if method == '出货':
                    new_num = old_num - int(num)
                    if new_num < 0:
                        self.show_warning_dialog(f'{typo}出货失败:库存不足')
                        return
                else:
                    new_num = old_num + int(num)
                self.__db.update(WAREHOUSE_TB, 'NAME', typo, 'QUANTITY', new_num)
            except Exception as e:
                logger.error(f'update warehouse failed:{e}')
                self.show_warning_dialog(f'数据更新失败')

        # update detail db
        self.__db.insert_detail(current_date, typo, method, num, picker)

        self.__text_edit_label.append(f'【{method}】:{typo}*{num} {picker_str}')

    def revert_detail_data(self):
        res = self.__db.revert(DETAIL_TB)
        if not res:
            return

        try:
            detail_info = MainWindow._detail_template ._make(res[0])
            picker = detail_info.picker
            if picker:
                picker = f'提货人:{picker}'
            content = f"""
是否要撤销最后一次操作？
【{detail_info.operate}】: {detail_info.name}*{detail_info.quantity} {picker}
            """
            reply = QMessageBox.question(self, title, content.strip(), QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
            res = self.__db.query(WAREHOUSE_TB, NAME=detail_info.name)
            warehouse_info = MainWindow._warehouse_template._make(res[0])
            current_quantity = int(warehouse_info.quantity)
            revert_quantity = int(detail_info.quantity)
            if detail_info.operate == '出货':
                new_quantity = current_quantity + revert_quantity
            else:
                new_quantity = current_quantity - revert_quantity

            self.__db.update(WAREHOUSE_TB, 'NAME', detail_info.name, 'QUANTITY', new_quantity)
            self.__db.delete(DETAIL_TB, 'NUM', detail_info.num)
            self.__text_edit_label.append('---------撤销详情---------')
            self.__text_edit_label.append(f'【{detail_info.operate}】: '
                                          f'{detail_info.name}*{detail_info.quantity} {picker}')

        except Exception as e:
            logger.error(f'revert detail failed:{e}')
            return

    def deal_with_json_data(self, res, js_data):
        for key in js_data.keys():
            for typo in js_data[key]:
                if typo in res[key]:
                    res[key][typo] = str(int(js_data[key][typo]) + int(res[key][typo]))
                else:
                    res[key][typo] = js_data[key][typo]

    def search(self, start, end):
        dates = get_date_range(start, end)
        res = copy.deepcopy(config_json)
        database_dir = os.path.join(pathlib.Path('.').absolute(), 'database')
        for date in dates:
            try:
                with open(os.path.join(database_dir, date)) as fp:
                    js_data = json.load(fp)
                    self.deal_with_json_data(res, js_data)
            except FileNotFoundError:
                logger.debug(f'file {date} not fond')
            except json.decoder.JSONDecodeError as e:
                logger.debug(f'JSONDecodeError {e}')

        self.show_search_result(res)

    def show_search_result(self, res):
        _cache_list = []
        for typo in res['IN']:
            _in = res['IN'][typo]
            try:
                _out = res['OUT'][typo]
            except KeyError:
                _out = '0'
            _template = f'{typo}：进货量{_in} 出货量{_out}'
            _cache_list.append(_template)

        self.__text_edit_label.append('\n'.join(_cache_list))

    def _check_num(self, num):
        try:
            num = int(num)
        except ValueError:
            self.show_warning_dialog("数量必须是数字")
            return False
        return True

    def btn_cb(self, text):
        if text == "ok":
            typo = self.__combobox.currentText()
            method = self.__method_combobox.currentText()
            num = self.__num_edit.text()
            picker = self.__to_edit.text()
            if not self._check_num(num):
                return

            if method == '出货' and self.__to_edit.text() == '':
                self.show_warning_dialog('提货人不能为空')
                return

            self.fill_data(method, typo, num, picker)
            self.update_total_data()
            self.__num_edit.clear()
            self.__to_edit.clear()
        elif text == "cancel":
            self.revert_detail_data()
            self.update_total_data()

        elif text == "add":
            new_type = self.__new_type_edit.text()
            if new_type in self.__type:
                self.show_warning_dialog(f'物料{new_type}已存在!')
                return

            if new_type == '':
                self.show_warning_dialog(f'物料不能为空!')
                return

            self.__type.insert(-1, new_type)
            self.__type = list({}.fromkeys(self.__type).keys())
            self.__combobox.clear()
            self.__combobox.addItems(self.__type)
            self.__combobox.setCurrentText(new_type)
            self.__text_edit_label.append(f'【新增】:{new_type}')
            self.__new_type_edit.clear()
            self.set_conf_list(new_type)
        elif text == "search":
            start_date = self.__start_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]
            end_date = self.__end_calendar_widget.dateTime().toString(Qt.ISODate).split('T')[0]

            # self.__text_edit_label.clear()
            self.__cache_list.append(f'======{start_date}至{end_date}材料统计情况======')
            self.search(start_date, end_date)

        cursor = self.__text_edit_label.textCursor()
        pos = len(self.__text_edit_label.toPlainText())
        cursor.setPosition(pos - 1)
        self.__text_edit_label.setTextCursor(cursor)

    def cancel_thread(self):
        if self.__thread:
            self.__thread.cancel()

    def close_db(self):
        if self.__db:
            self.__db.close()

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QMessageBox.question(self, title, "是否要退出程序？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.__thread:
                self.__thread.cancel()
            if self.__db:
                self.__db.close()
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
