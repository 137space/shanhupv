from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel, QSpacerItem, QSizePolicy, QFrame, QDialog
import sys
from gui.list import TaskListWidget, save_task_to_file, load_tasks_from_file
from gui.input import AddTaskDialog
from gui.info import InfoWidget
from gui.click import TaskButtonClickHandler
import psutil

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShanHuPV GUI")
        self.setGeometry(100, 100, 850, 600)

        self.setWindowIcon(QIcon('src/logo.png'))

        self.task_list = TaskListWidget()
        self.info_widget = InfoWidget()
        self.task_handler = TaskButtonClickHandler(self)
        self.init_ui()
        self.load_tasks()

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_system_info)
        self.update_timer.start(1000)

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        
        button_add_task = QPushButton("添加任务")
        button_add_task.setFixedSize(120, 50)
        button_add_task.clicked.connect(self.add_task)
        header_layout.addWidget(button_add_task)
        
        title_label = QLabel("珊瑚PV v1.0.240805 GUI")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(line)
        
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.info_widget)
        
        task_list_layout = QHBoxLayout()
        task_list_layout.addWidget(self.task_list)
        
        control_buttons_layout = QVBoxLayout()
        control_buttons_layout.setContentsMargins(0, 8, 0, 0)
        button_start_all = QPushButton("全部运行")
        button_stop_all = QPushButton("全部停止")
        button_open_terminal = QPushButton("打开终端")
        
        button_start_all.clicked.connect(self.task_list.run_all_tasks)
        button_stop_all.clicked.connect(self.task_list.stop_all_tasks)
        button_open_terminal.clicked.connect(self.task_handler.open_terminal)
        
        control_buttons_layout.addWidget(button_start_all)
        control_buttons_layout.addWidget(button_stop_all)
        control_buttons_layout.addWidget(button_open_terminal)
        
        button_start_all.setStyleSheet("height: 30px;")
        button_stop_all.setStyleSheet("height: 30px;")
        button_open_terminal.setStyleSheet("height: 30px;")
        
        control_buttons_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        help_info = QLabel("注意：\n运行任务时,请注意cpu和ram\n占用率,过高将引发程序崩溃\n\n国内代理IP购买联系WX：\nsupotka51(说明来意)\n\n公众号：栈链宇创02")
        help_info.setWordWrap(True)
        control_buttons_layout.addWidget(help_info)
        
        task_list_layout.addLayout(control_buttons_layout)
        
        info_task_layout = QVBoxLayout()
        info_task_layout.addLayout(info_layout)
        info_task_layout.addLayout(task_list_layout)
        
        main_layout.addLayout(info_task_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_name = dialog.task_name.text()
            url = dialog.url.text()
            proxy_ip = dialog.proxy_ip_file
            proxy_ua = dialog.proxy_ua_file
            threads = dialog.threads.value()
            access_time = dialog.access_time.value()
            refresh_count = dialog.refresh_count.value()
            click_count = dialog.click_count.value()

            command = dialog.generate_command()

            task_details = {
                '任务名': task_name,
                'url链接-u': url,
                'ip代理文件': proxy_ip,
                'ip代理类型': dialog.proxy_ip_type,
                'ua代理文件': proxy_ua,
                '线程数-t': threads,
                '访问时间-s': access_time,
                '刷新次数-r': refresh_count,
                '点击a标签次数-a': click_count,
                '指令': command
            }
            task_file = save_task_to_file(task_details)
            self.task_list.add_task(task_name, task_file)

    def load_tasks(self):
        tasks = load_tasks_from_file()
        for task_name, task_file in tasks:
            self.task_list.add_task(task_name, task_file)

    def update_system_info(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        self.info_widget.update_cpu_usage(cpu_usage)
        self.info_widget.update_memory_usage(memory_usage)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
