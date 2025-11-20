import os
import json
import subprocess
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

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
        if not os.path.exists(task_file):
            # 不提示用户，仅跳过无效任务
            return

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

    def stop_task(self, task_file):
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
            QMessageBox.warning(self.parent_widget, '警告', '任务未在运行中或已停止。')

    def delete_task(self, task_file, item_widget):
        reply = QMessageBox.question(self.parent_widget, '确认删除', '确定要删除此任务吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if self.current_task_process and self.current_task_process.poll() is None:
                    self.stop_task(task_file)

                if os.path.exists(task_file):
                    os.remove(task_file)
                else:
                    QMessageBox.warning(self.parent_widget, '警告', '任务文件不存在。')

                item_widget.setParent(None)
                print(f"Task deleted: {task_file}")
            except Exception as e:
                QMessageBox.critical(self.parent_widget, '错误', f'删除任务失败：{e}')

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
    
    def open_terminal(self):
        cmd = "start cmd /k python shanhupv.py"
        subprocess.Popen(cmd, shell=True)