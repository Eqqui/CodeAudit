from PyQt5 import QtGui
from PyQt5.Qsci import QsciScintilla, \
    QsciLexerMakefile,\
    QsciLexerBash, \
    QsciLexerCPP, \
    QsciLexerCSS, \
    QsciLexerCSharp, \
    QsciLexerD, \
    QsciLexerFortran, \
    QsciLexerHTML, \
    QsciLexerJava, \
    QsciLexerJavaScript, \
    QsciLexerLua, \
    QsciLexerPO, \
    QsciLexerPOV, \
    QsciLexerPascal, \
    QsciLexerPerl, \
    QsciLexerPostScript, \
    QsciLexerProperties, \
    QsciLexerPython, \
    QsciLexerRuby, \
    QsciLexerSQL, \
    QsciLexerTCL, \
    QsciLexerTeX, \
    QsciLexerXML, \
    QsciLexerYAML,QsciDocument
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QMenu, QAction

from config.settings import Settings as S


class TextArea(QsciScintilla):

    extension_to_lang = {
        'sh': "Bash",
        'bash': "Bash",
        'zsh': "Bash",
        'bat': "Bash",
        'cmd': "Bash",
        'c': "CPP",
        'cc': "CPP",
        'cpp': "CPP",
        'cxx': "CPP",
        'h': "CPP",
        'hh': "CPP",
        'hpp': "CPP",
        'hxx': "CPP",
        'cs': "CSharp",
        'java': "Java",
        'js': "JavaScript",
        'json': "JavaScript",
        'css': "CSS",
        'd': "D",
        'f': "Fortran",
        'html': "HTML",
        'htm': "HTML",
        'xml': "XML",
        'lua': "Lua",
        'Makefile': "Makefile",
        'pas': "Pascal",
        'pl': "Perl",
        'pm': "Perl",
        'po': "PO",
        'pot': "PO",
        'ps': "PostScript",
        'pov': "POV",
        'inc': "POV",
        'properties': "Properties",
        'ini': "Properties",
        'py': "Python",
        'rb': "Ruby",
        'sql': "SQL",
        'tcl': "TCL",
        'tex': "TeX",
        'yaml': "YAML",
        'yml': "YAML"
    }
    lang_lexer = {
        'Bash': QsciLexerBash,
        'CPP': QsciLexerCPP,
        'CSharp': QsciLexerCSharp,
        'Java': QsciLexerJava,
        'JavaScript': QsciLexerJavaScript,
        'CSS': QsciLexerCSS,
        'D': QsciLexerD,
        'Fortran': QsciLexerFortran,
        'HTML': QsciLexerHTML,
        'XML': QsciLexerXML,
        'Lua': QsciLexerLua,
        'Makefile': QsciLexerMakefile,
        'Pascal': QsciLexerPascal,
        'Perl': QsciLexerPerl,
        'PO': QsciLexerPO,
        'Postscript': QsciLexerPostScript,
        'POV': QsciLexerPOV,
        'Properties': QsciLexerProperties,
        'Python': QsciLexerPython,
        'Ruby': QsciLexerRuby,
        'SQL': QsciLexerSQL,
        'TCL': QsciLexerTCL,
        'TeX': QsciLexerTeX,
        'YAML': QsciLexerYAML
    }

    def __init__(self,
                 name: str = "Untilted",
                 data: str = "",
                 path: str = None,
                 parent = None,):
        super().__init__()
        self.super = super()
        self.__path = path
        self.__name = name
        self.setText(data)
        self.extension = self.__get_extension(name)
        self.current_lang = None
        self.__font = QFont(S.FONT_FAMILY, S.FONT_SIZE)
        self.setup_editor()
        self.doc = QsciDocument()
        self.modified = False
        self.textChanged.connect(self.text_modified)
        self.parent = parent

    def get_name(self):
        return self.__name

    def text_modified(self):
        self.modified = True

    def get_path(self):
        return self.__path

    @staticmethod
    def __get_extension(name):
        tmp = name.split(".")
        if len(tmp) > 1:
            return tmp[-1]
        return None

    @classmethod
    def get_language(cls, extension: str):
        if extension not in cls.extension_to_lang:
            return None

        return cls.extension_to_lang[extension]

    def get_lexer(self, language: str):
        if language not in self.lang_lexer:
            return None
        return self.lang_lexer[language](self)

    def setup_editor(self):
        # FONT #
        self.setUtf8(S.UTF8)
        lang = self.get_language(self.extension)
        self.set_lexer(lang)

        # Tab
        self.setIndentationGuides(S.INDENTATION_GUIDES)
        self.setIndentationsUseTabs(S.INDENTATIONS_USE_TABS)
        self.setTabWidth(S.TAB_WIDTH)
        self.setAutoIndent(S.AUTO_INDENT)
        self.setScrollWidth(S.SCROLL_WIDTH)

        # WarpMode
        self.setWrapMode(S.WRAP_MODE)

        # Cursor
        self.setCaretLineVisible(S.CARET_LINE_VISIBLE)
        self.setCaretLineBackgroundColor(S.CARET_LINE_BG_COLOR)

        # MARGIN #
        self.setMarginType(0, self.NumberMargin)
        self.set_margin_num_width()
        self.setMarginsBackgroundColor(S.MARGINS_BG_COLOR)

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

    def set_lexer(self, lang: str):
        new_lexer = self.get_lexer(lang)
        self.setLexer(new_lexer)

        self.current_lang = lang if lang in self.lang_lexer else None
        self.__update_font()

    def __update_font(self):
        if self.current_lang is None:
            self.setFont(self.__font)
        else:
            self.lexer().setFont(self.__font)

    def set_margin_num_width(self):
        size = len(str(self.lines()))
        size = len(str(size)) * 3 + 30
        self.setMarginWidth(0, size)

    def change_name(self, name: str):
        self.__name = name
        self.extension = self.__get_extension(name)
        lang = self.get_language(self.extension)
        self.set_lexer(lang)

    def change_path(self, path: str):
        self.__path = path

    def count(self, string: str, *, case: bool=False) -> int:
        if case:
            counter = self.text().count(string)
        else:
            counter = self.text().lower().count(string.lower())
        return counter

    def highlight_string(self, key_str):
        editor_text = self.text()

        self.indicatorDefine(QsciScintilla.RoundBoxIndicator, 0)
        self.setIndicatorForegroundColor(QColor(255,255,0, 70), 0)

        start_index = 0
        count = 0
        while start_index != -1:
            start_index = editor_text.find(key_str, start_index)
            if start_index != -1:
                self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 0)
                self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_index, len(key_str))
                start_index += len(key_str)
                count += 1
        return count

    def clear_highlight(self):
        self.SendScintilla(QsciScintilla.SCI_STARTSTYLING, 0, 0x1f)
        self.SendScintilla(QsciScintilla.SCI_SETSTYLING, self.length(), 0)

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent) -> None:
        ori = self.createStandardContextMenu()
        go_defi = QAction("go to the definition")
        ori.addAction(go_defi)
        go_defi.triggered.connect(self.go_to_definition)

        if not self.hasSelectedText():
            go_defi.setEnabled(False)
        # 显示右键菜单
        ori.exec_(event.globalPos())

    def go_to_definition(self):
        str = self.selectedText()
        func_name = [row[1] for row in self.parent.token_fun]
        val_name = [row[1] for row in self.parent.token_val]
        if str in val_name:
            index = val_name.index(str)
            filename = self.parent.token_val[index][0]
            current_file = self.get_path()+ "/" + self.get_name()
            print()
            print(filename)
            print(current_file)
            if current_file!= filename:
                self.parent.file_display(filename)
                line = int(self.parent.token_val[index][2].split(":")[-1])
                text = self.parent.tabWidget.currentWidget()
                text.setSelection(line, 0, line-1, 0)
            else:
                line = int(self.parent.token_val[index][2].split(":")[-1])
                self.setSelection(line, 0, line - 1, 0)

        elif str in func_name:
            index = func_name.index(str)
            filename = self.parent.token_fun[index][0]
            current_file = self.get_path()+ "/" + self.get_name()
            print()
            print(filename)
            print(current_file)
            if current_file != filename:
                self.parent.file_display(filename)
                line = int(self.parent.token_fun[index][2].split(":")[-1])
                text = self.parent.tabWidget.currentWidget()
                text.setSelection(line, 0, line-1, 0)
            else:
                line = int(self.parent.token_fun[index][2].split(":")[-1])
                self.setSelection(line, 0, line - 1, 0)

        else:
            for item in self.parent.token_fun:
                if item[-1]:
                    filename = item[0]
                    current_file = self.get_path()+ "/" + self.get_name()
                    for val in item[-1]:
                        if str == val[0]:
                            line = int(val[1].split(":")[-1])
                            if current_file != filename:
                                self.parent.file_display(filename)
                                text = self.parent.tabWidget.currentWidget()
                                text.setSelection(line, 0, line-1, 0)
                            else:
                                self.setSelection(line, 0, line - 1, 0)
                            break
