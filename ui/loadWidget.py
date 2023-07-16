from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QProgressDialog, QMessageBox


class LoadingDialog(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.progress_dialog = QProgressDialog()
        self.progress_dialog.setWindowTitle("加载中")
        self.progress_dialog.setLabelText("正在加载，请稍候...")
        self.progress_dialog.setRange(0, 0)  # 无限循环模式
        self.progress_dialog.setModal(True)  # 阻塞其他窗口
        self.progress_dialog.setMinimumWidth(400)

    def show(self):
        self.progress_dialog.show()

    def hide(self):
        self.progress_dialog.hide()

    def close(self):
        self.progress_dialog.close()
        QMessageBox.information(self.parent, "提示", "加载完成")