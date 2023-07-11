from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtGui import QColor, QFont


class CustomLexer(QsciLexerCustom):
    def __init__(self, parent, originalLexer, key_str=''):
        super(CustomLexer, self).__init__(parent)
        # 设置默认字体样式
        self.key_str = key_str
        # self.setDefaultColor(QColor("#000000"))
        # self.setDefaultPaper(QColor("#ffffff"))
        # 设置要高亮的字体样式
        # self.setColor(QColor("#ff0000"), 1)
        self.setPaper(QColor("#fdf7d3"), 1)
        # self.copy_attributes_from(originalLexer)
        self.originalLexer = originalLexer

    # 必须重写的方法
    def language(self):
        return 'Custom'

    def description(self, style):
        if style == 1:
            return 'highlight'
        return ''

    def styleText(self, start, end):
        self.originalLexer.styleText(start, end)  # 使用原始的 lexer 对代码进行着色
        # 然后再进行自定义的字符串高亮处理
        # 获取编辑器的内容
        editor = self.editor()
        if editor is None:
            return
        # 要高亮的字符串
        text = self.key_str
        # 获取要处理的文本
        source = editor.text()[start:end]
        # 在文本中搜索要高亮的字符串
        index = source.lower().find(text)
        while index >= 0:
            # 找到字符串，应用样式
            length = len(text)
            editor.SendScintilla(QsciScintilla.SCI_STARTSTYLING, start + index, 0x1f)
            editor.SendScintilla(QsciScintilla.SCI_SETSTYLING, length, 1)
            index = source.find(text, index + length)

    def copy_attributes_from(self, originalLexer):
        attrs = dir(originalLexer)
        for attr in attrs:
            if not attr.startswith('_'):
                original_value = getattr(originalLexer, attr)
                try:
                    setattr(self, attr, original_value)
                except AttributeError:
                    # 捕获只读属性错误
                    pass