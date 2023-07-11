import os.path
import re
from PyQt5 import QtCore
from config.config import Config


class Function:
    def __init__(self, filepath='', name='', val_type='', type="", line=""):
        self.filepath = filepath
        self.name = name
        self.val_type = val_type
        self.type = type
        self.line = line
        self.list = []
        self.father = ""
        self.flag = 0

    def add(self, value):
        self.list.append(value)


class Analysis(QtCore.QObject):
    stop_signal = QtCore.pyqtSignal(str)

    def __init__(self, filename, config_ini, parent=None):
        super(Analysis, self).__init__(parent)
        self.master = parent
        self.filename = filename
        self.filelist = []
        self.vallist = []
        self.funlist = []
        self.config_ini = config_ini
        self.token_func = []
        self.token_val = []
        self.danger = []
        self.invalid_func = []
        self.invalid_val = []

    def run(self):
        self.get_function()
        self.show_token()

        return self.token_func, self.token_val, self.danger, self.invalid_func, self.invalid_val

    def get_function(self):
        path, name = os.path.split(self.filename)
        self.get_file(path)
        cpath = self.config_ini['main_project']['project_path'] + self.config_ini['scanner']['ctags']
        print(cpath)
        cmd = cpath + " --languages=c -R -I argv --kinds-c=+defglmpstuvx --fields=+n"
        # cmd = "D:\AAtestplaceforcode\CodeAudit\\tools\scanner\ctags.exe --languages=c -R -I argv --kinds-c=+defglmpstuvx --fields=+n"
        for file in self.filelist:
            cmd += " " + file
        os.system(cmd)
        f = open("tags", "r")
        code = f.readlines()
        f.close()

        for line in code:
            if line.startswith("!_TAG"):
                continue
            split_line = line.split('\t')
            func = Function(name=split_line[0], filepath=split_line[1])
            if len(split_line) == 8 or len(split_line) == 6:
                func.line = split_line[4]
                func.type = split_line[3]

                if func.type == 'l':
                    func.val_type = split_line[6].split(":")[-1]
                    func.father = split_line[5].split(":")[-1]
                    self.vallist.append(func)
                else:
                    func.val_type = split_line[5].strip("\n").split(":")[-1]
                    if func.type == 'f':
                        self.funlist.append(func)
                    else:
                        if func.type == 's':
                            func.val_type = "struct"
                        self.vallist.append(func)
            elif len(split_line) == 9:
                func.line = split_line[5]
                func.type = split_line[4]
                if func.type == 'm':
                    func.val_type = split_line[7].split(":")[-1]
                    func.father = split_line[6]
                    self.vallist.append(func)
                if func.type == 'l':
                    func.val_type = split_line[7].split(":")[-2]+" "+split_line[7].split(":")[-1]# TODO:可优化，代改
                    func.father = split_line[6].split(":")[-1]
                    self.vallist.append(func)
        for i in self.vallist:
            if i.type == 'm':
                for v in self.vallist:
                    if v.type == 's':
                        self.vallist[self.vallist.index(v)].add(i)
            elif i.type == 'l':
                for f in self.funlist:
                    if i.filepath == f.filepath and i.father == f.name:
                        self.funlist[self.funlist.index(f)].add(i)

    def get_file(self, path):
        list = []
        files = os.listdir(path)
        for file in files:
            if re.match("(\w*)\.c$", file) is not None:
                f = path + '/' + file
                if not os.path.isdir(f):
                    list.append(f)
        self.filelist = list

    def show_token(self):
        # TODO: show in tree
        pass


# if __name__ == '__main__':
#     con = Config()
#     ini = con.read_config()
#     a = Analysis("D:\AAtestplaceforcode\code_aduit\\",ini)
#     a.run()
#     print(a.filelist)
