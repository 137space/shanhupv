import json
import os
import subprocess
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox, QListWidget, QListWidgetItem)

class TaskButtonClickHandler:
    def __init__(self, parent_widget):
        self.parent_widget = parent_widget
        self.current_task_process = None
        self.status_label = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_task_status)

    def set_status_label(self, label):
        self.status_label = label

    def run_task(self, task_file):
        if self.current_task_process and self.current_task_process.poll() is None:
            QMessageBox.warning(self.parent_widget, '警告', '已有任务在运行中，请先停止当前任务。')
            return

        try:
            with open(task_file, 'r') as f:
                task_details = json.load(f)

            command = task_details.get("指令", "")
            if not command:
                raise ValueError("指令属性缺失")

            command_list = command.split()
            if command_list[0] != "-u":
                raise ValueError("指令格式错误")

            command_list = ['python', 'tasks.py'] + command_list
            work_dir = os.path.dirname(os.path.dirname(__file__))

            self.current_task_process = subprocess.Popen(
                command_list, cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            print(f"Running task with command: {' '.join(command_list)}")

            if self.status_label:
                self.status_label.setStyleSheet("background-color: green; border-radius: 8px;")

            self.timer.start(1000)
        except Exception as e:
            QMessageBox.critical(self.parent_widget, '错误', f'无法运行任务：{e}')

    def stop_task(self, task_file, show_warning=True):
        if self.current_task_process and self.current_task_process.poll() is None:
            try:
                self.current_task_process.terminate()
                self.current_task_process = None
                self.timer.stop()

                if self.status_label:
                    self.status_label.setStyleSheet("background-color: red; border-radius: 8px;")

                print(f"Task stopped: {task_file}")
            except Exception as e:
                QMessageBox.critical(self.parent_widget, '错误', f'无法停止任务：{e}')
        else:
            if show_warning:
                QMessageBox.warning(self.parent_widget, '警告', '任务未在运行中或已停止。')

    def delete_task(self, task_file, item_widget):
        reply = QMessageBox.question(self.parent_widget, '确认删除', '确定要删除此任务吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.current_task_process and self.current_task_process.poll() is None:
                self.stop_task(task_file)
            if os.path.exists(task_file):
                os.remove(task_file)
            self.parent_widget.update_task_list()

    def show_task_info(self, task_file):
        with open(task_file, 'r') as f:
            task_details = json.load(f)
        details = '\n'.join(f"{key}: {value}" for key, value in task_details.items())
        QMessageBox.information(self.parent_widget, '任务信息', details)

    def check_task_status(self):
        if self.current_task_process and self.current_task_process.poll() is not None:
            self.current_task_process = None
            self.timer.stop()

            if self.status_label:
                self.status_label.setStyleSheet("background-color: red; border-radius: 8px;")

            print("Task completed.")

class TaskListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
        self.task_handlers = {}
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.task_list_widget = QListWidget()
        self.layout.addWidget(self.task_list_widget)
        self.setLayout(self.layout)

    def add_task(self, task_name, task_file):
        handler = TaskButtonClickHandler(self)
        item_widget = QWidget()
        item_layout = QHBoxLayout()

        status_label = QLabel()
        status_label.setFixedSize(16, 16)
        status_label.setStyleSheet("background-color: red; border-radius: 8px;")
        item_layout.addWidget(status_label)

        task_label = QLabel(task_name)
        item_layout.addWidget(task_label)

        run_button = QPushButton("运行")
        run_button.setFixedSize(60, 30)
        run_button.clicked.connect(lambda: handler.run_task(task_file))
        item_layout.addWidget(run_button)

        stop_button = QPushButton("停止")
        stop_button.setFixedSize(60, 30)
        stop_button.clicked.connect(lambda: handler.stop_task(task_file))
        item_layout.addWidget(stop_button)

        delete_button = QPushButton("删除")
        delete_button.setFixedSize(60, 30)
        delete_button.clicked.connect(lambda: handler.delete_task(task_file, item_widget))
        item_layout.addWidget(delete_button)

        info_button = QPushButton("详细信息")
        info_button.setFixedSize(100, 30)
        info_button.clicked.connect(lambda: handler.show_task_info(task_file))
        item_layout.addWidget(info_button)

        item_widget.setLayout(item_layout)
        list_item = QListWidgetItem(self.task_list_widget)
        list_item.setSizeHint(item_widget.sizeHint())
        self.task_list_widget.setItemWidget(list_item, item_widget)

        handler.set_status_label(status_label)
        self.tasks.append((task_name, task_file))
        self.task_handlers[task_name] = handler

    def remove_task(self, item_widget):
        row = self.task_list_widget.indexFromItem(self.task_list_widget.itemWidget(item_widget)).row()
        self.task_list_widget.takeItem(row)

    def update_task_list(self):
        self.task_list_widget.clear()
        tasks = load_tasks_from_file()
        for task_name, task_file in tasks:
            self.add_task(task_name, task_file)

    def run_all_tasks(self):
        for task_name, handler in self.task_handlers.items():
            task_file = self.find_task_file(task_name)
            if task_file and os.path.exists(task_file):  # 确保任务文件存在
                handler.run_task(task_file)

    def stop_all_tasks(self):
        for task_name, handler in self.task_handlers.items():
            task_file = self.find_task_file(task_name)
            if task_file:
                handler.stop_task(task_file, show_warning=False)
        QMessageBox.information(self, '提示', '已停止全部任务。')

    def find_task_file(self, task_name):
        for name, file in self.tasks:
            if name == task_name:
                return file
        return None

def save_task_to_file(task_details):
    task_dir = os.path.join(os.path.dirname(__file__), 'listconfig')
    os.makedirs(task_dir, exist_ok=True)
    task_file = os.path.join(task_dir, f'task_{os.urandom(6).hex()}.json')
    with open(task_file, 'w') as f:
        json.dump(task_details, f, ensure_ascii=False, indent=4)
    return task_file

def load_tasks_from_file():
    task_dir = os.path.join(os.path.dirname(__file__), 'listconfig')
    tasks = []
    for file_name in os.listdir(task_dir):
        if file_name.endswith('.json'):
            task_file = os.path.join(task_dir, file_name)
            if os.path.exists(task_file):
                with open(task_file, 'r') as f:
                    task_details = json.load(f)
                task_name = task_details.get('任务名', '无名称任务')
                tasks.append((task_name, task_file))
    return tasks
