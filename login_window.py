# -*- encoding=utf-8 -*-

"""

"""
import sys
import PyQt5
from utils import *
from main_window import MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMessageBox


class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.__username_entry = None
        self.__password_entry = None
        self.__tips_label = None
        self.__conf = Config()
        self.init_ui()

    def init_ui(self):
        self.resize(400, 260)
        self.setWindowTitle(title)

        ok_btn = QPushButton('登录', self)
        # ok_btn.setEnabled(True)
        ok_btn.clicked.connect(self.login_cb)
        ok_btn.resize(20, 20)

        label_vbox = QVBoxLayout()

        tips_hbox = QHBoxLayout()
        self.__tips_label = QLabel()
        tips_hbox.addStretch(1)
        tips_hbox.addWidget(self.__tips_label)
        tips_hbox.addStretch(1)

        user_hbox = QHBoxLayout()
        user_hbox.addStretch(1)
        user_label = QLabel('用户名')
        user_hbox.addWidget(user_label)
        user_name = self.__conf.get('User', 'name')
        self.__username_entry = PyQt5.QtWidgets.QLineEdit()
        self.__username_entry.setText(user_name)
        user_hbox.addWidget(self.__username_entry)
        user_hbox.addStretch(1)

        label_hbox = QHBoxLayout()
        label_hbox.addStretch(1)
        user_label = QLabel('密  码')
        label_hbox.addWidget(user_label)
        self.__password_entry = PyQt5.QtWidgets.QLineEdit()
        self.__password_entry.setEchoMode(PyQt5.QtWidgets.QLineEdit.Password)
        label_hbox.addWidget(self.__password_entry)
        label_hbox.addStretch(1)

        label_vbox.addLayout(tips_hbox)
        label_vbox.addLayout(user_hbox)
        label_vbox.addLayout(label_hbox)
        label_vbox.addWidget(ok_btn)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(label_vbox)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def run(self):
        self.show()

    def login_cb(self):
        user_name = self.__username_entry.text()
        password = self.__password_entry.text()
        if user_name != "admin":
            self.__tips_label.setText('账户为admin')
            return
        if not self.__password_entry.text():
            self.__tips_label.setText('密码不能为空')
            return
        if password != "123456":
            self.__tips_label.setText('密码错误')
            return
        self.__conf.set('User', name=user_name, password=password)
        self.hide()
        m.run()

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QMessageBox.question(self, title, "是否要退出程序？", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            m.cancel_thread()
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = LoginWindow()
    m = MainWindow()
    w.run()
    m.hide()
    sys.exit(app.exec_())
