from PyQt5.Qsci import QsciScintilla
from PyQt5.QtWidgets import QDialog, QTextEdit
from PyQt5.QtGui import QTextDocument, QTextCursor, QTextCharFormat, QColor, QSyntaxHighlighter
import PyQt5.QtWidgets
from .myCustomLexer import CustomLexer
from ui.findWidget import Ui_findDialog


class FindForm(QDialog, Ui_findDialog):
    def __init__(self, parent = None):
        super(FindForm, self).__init__(parent)
        self.setupUi(self)
        self.master = parent
        self.pushButton.clicked.connect(self.find_btn)
        self.pushButton_3.clicked.connect(self.replace_btn)
        self.pushButton_4.clicked.connect(self.replaceall_btn)
        # 保存原来的lexer
        self.previousLexer = self.master.tabWidget.currentWidget().lexer()
        self.prompt = ['XXXXX']

    def find_btn(self):
        self.label.clear()
        text = self.lineEdit.text()

        if self.prompt[-1] != text:
            flag = 1
            if self.prompt[-1] == 'XXXXX':
                flag = 0
            self.prompt.append(text)
        else:
            flag = 0

        textEdit = self.master.tabWidget.currentWidget()

        if flag:
            textEdit.setLexer(self.previousLexer)

        # 高亮搜索字符串
        count = textEdit.highlight_string(text)
        print("count:", count)

        founded = textEdit.findFirst(text, self.checkBox.isChecked(), True, True, True)
        print("founded:", founded)

        if count:
            self.label.setStyleSheet("QLabel {color: green;}")
            self.label.setText(
                "找到 \"{}\" {} 次".format(
                    self.lineEdit.text(),
                    count
                )
            )

        if not founded:
            # 如果没有找到，那么重置光标到文本框的开始，然后再次查找
            textEdit.setCursorPosition(0, 0)
            founded = textEdit.findFirst(text, self.checkBox.isChecked(), True, True, True)
            if not founded and not count:
                # 如果仍然没有找到，那么显示没有找到的信息
                self.label.setStyleSheet("QLabel {color: red;}")
                self.label.setText(
                    "没有找到 \"{}\"".format(
                        self.lineEdit.text()
                    )
                )

    def replace_btn(self):
        self.label.setText('')
        self.master.tabWidget.currentWidget().replace(self.lineEdit_2.text())

    def replaceall_btn(self):
        self.label.setText('')
        textEdit = self.master.tabWidget.currentWidget()
        replaced = 0
        text = self.lineEdit.text()
        founded = textEdit.findFirst(text, self.checkBox.isChecked(), True, True, True)
        while founded:
            textEdit.replace(self.lineEdit_2.text())
            founded = textEdit.findNext()
            replaced += 1

        self.label.setStyleSheet("QLabel {color: red;}")
        self.label.setText(f"{replaced}处被替换")

    # 重写closeEvent方法
    def closeEvent(self, event):
        # 在关闭窗口时恢复原来的lexer
        textEdit = self.master.tabWidget.currentWidget()
        textEdit.setLexer(self.previousLexer)
        event.accept()
