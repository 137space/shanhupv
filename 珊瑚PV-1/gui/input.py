from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QFileDialog,
    QDialogButtonBox, QRadioButton, QButtonGroup, QPushButton, QGroupBox, 
    QGridLayout, QHBoxLayout, QMessageBox
)
import os

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加任务")
        self.setGeometry(200, 200, 400, 400)

        self.proxy_ip_file = ''
        self.proxy_ua_file = ''
        self.proxy_ip_type = 'http'  # 默认值 'http'

        main_layout = QVBoxLayout(self)

        # 任务名称和URL输入区域
        task_layout = QGridLayout()
        task_layout.addWidget(QLabel("任务命名:"), 0, 0)
        self.task_name = QLineEdit()
        task_layout.addWidget(self.task_name, 0, 1)

        task_layout.addWidget(QLabel("输入网址:"), 1, 0)
        self.url = QLineEdit()
        task_layout.addWidget(self.url, 1, 1)
        
        main_layout.addLayout(task_layout)

        # IP代理选择区域
        ip_proxy_group = QGroupBox("IP代理设置")
        ip_layout = QVBoxLayout()

        self.proxy_ip_button = QPushButton("选择IP代理文件")
        self.proxy_ip_button.clicked.connect(self.select_proxy_ip_file)
        ip_layout.addWidget(self.proxy_ip_button)

        ip_type_layout = QHBoxLayout()
        self.proxy_ip_type_group = QButtonGroup()
        self.http_radio = QRadioButton("HTTP")
        self.socks5_radio = QRadioButton("SOCKS5")
        self.http_radio.setChecked(True)
        self.proxy_ip_type_group.addButton(self.http_radio)
        self.proxy_ip_type_group.addButton(self.socks5_radio)
        self.proxy_ip_type_group.buttonClicked.connect(self.update_proxy_ip_type)
        ip_type_layout.addWidget(self.http_radio)
        ip_type_layout.addWidget(self.socks5_radio)
        ip_layout.addLayout(ip_type_layout)

        ip_layout.addWidget(QLabel("选择的IP代理文件:"))
        self.proxy_ip_file_label = QLabel()
        ip_layout.addWidget(self.proxy_ip_file_label)

        ip_proxy_group.setLayout(ip_layout)
        main_layout.addWidget(ip_proxy_group)

        # UA选择区域
        ua_proxy_group = QGroupBox("UA设置")
        ua_layout = QVBoxLayout()

        self.proxy_ua_button = QPushButton("选择UA文件")
        self.proxy_ua_button.clicked.connect(self.select_proxy_ua_file)
        ua_layout.addWidget(self.proxy_ua_button)

        ua_layout.addWidget(QLabel("选择的UA文件:"))
        self.proxy_ua_file_label = QLabel()
        ua_layout.addWidget(self.proxy_ua_file_label)

        ua_proxy_group.setLayout(ua_layout)
        main_layout.addWidget(ua_proxy_group)

        # 线程和时间设置区域
        task_settings_group = QGroupBox("任务设置")
        settings_layout = QGridLayout()

        settings_layout.addWidget(QLabel("线程数:"), 0, 0)
        self.threads = QSpinBox()
        self.threads.setRange(1, 999)
        self.threads.setValue(1)  # 默认值为1
        settings_layout.addWidget(self.threads, 0, 1)

        settings_layout.addWidget(QLabel("访问时间 (秒):"), 1, 0)
        self.access_time = QSpinBox()
        self.access_time.setRange(1, 999)
        self.access_time.setValue(10)  # 默认值为10
        settings_layout.addWidget(self.access_time, 1, 1)

        settings_layout.addWidget(QLabel("每个网页刷新次数:"), 2, 0)
        self.refresh_count = QSpinBox()
        self.refresh_count.setRange(0, 999)
        self.refresh_count.setValue(3)  # 默认值为3
        settings_layout.addWidget(self.refresh_count, 2, 1)

        settings_layout.addWidget(QLabel("每个网页点击链接数:"), 3, 0)
        self.click_count = QSpinBox()
        self.click_count.setRange(0, 999)
        self.click_count.setValue(1)  # 默认值为1
        settings_layout.addWidget(self.click_count, 3, 1)

        task_settings_group.setLayout(settings_layout)
        main_layout.addWidget(task_settings_group)

        # 确认和取消按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def select_proxy_ip_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择IP代理文件", "", "IP代理文件 Files (*.*);;All Files (*)")
        if file_name:
            self.proxy_ip_file = file_name
            self.proxy_ip_file_label.setText(file_name)

    def select_proxy_ua_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择UA文件", "", "UA代理文件 (*.json);;All Files (*)")
        if file_name:
            self.proxy_ua_file = file_name
            self.proxy_ua_file_label.setText(file_name)

    def update_proxy_ip_type(self, button):
        self.proxy_ip_type = button.text()

    def validate_and_accept(self):
        # 验证输入是否为空
        if not self.task_name.text().strip():
            self.show_warning("任务命名不能为空")
            return
        if not self.url.text().strip():
            self.show_warning("网址不能为空")
            return
        if not self.proxy_ip_file:
            self.show_warning("请选择IP代理文件")
            return
        if not self.proxy_ua_file:
            self.show_warning("请选择UA文件")
            return
        self.accept()

    def show_warning(self, message):
        QMessageBox.warning(self, "输入错误", message)

    def generate_command(self):
        command = f"-u {self.url.text()} -t {self.threads.value()} -s {self.access_time.value()} " \
                  f"-r {self.refresh_count.value()} -a {self.click_count.value()} " \
                  f"--{self.proxy_ip_type.lower()}={self.proxy_ip_file} --ua={self.proxy_ua_file}"
        return command
