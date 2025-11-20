from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QTime

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_run_time)
        self.timer.start(1000)  # 每秒更新一次

        self.start_time = QTime.currentTime()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 0, 0, 0)

        self.run_time_label = QLabel("已运行时间：")
        self.cpu_usage_label = QLabel("CPU占用率：")
        self.memory_usage_label = QLabel("内存占用率：")

        layout.addWidget(self.run_time_label)
        layout.addWidget(self.cpu_usage_label)
        layout.addWidget(self.memory_usage_label)

        self.setLayout(layout)

    def update_run_time(self):
        elapsed = self.start_time.secsTo(QTime.currentTime())
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.run_time_label.setText(f"已运行时间：{hours:02}:{minutes:02}:{seconds:02}")

    def update_cpu_usage(self, usage):
        self.cpu_usage_label.setText(f"CPU占用率：{usage}%")

    def update_memory_usage(self, usage):
        self.memory_usage_label.setText(f"内存占用率：{usage}%")
