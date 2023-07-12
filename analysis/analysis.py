import os.path
import re
from PyQt5 import QtCore
import pymysql
from config.config import Config

db = pymysql.connect(
    host="localhost",
    port=3306,
    user='root',
    password='',
    charset='utf8mb4',
    database='code_audit'
)
cursor = db.cursor()

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

        self.validfun = []
        self.validval = []

    def run(self):
        self.get_function()
        self.gen_token()
        self.gen_danger()
        self.gen_invalid()
        return self.token_func, self.token_val, self.danger, self.invalid_func, self.invalid_val

    def get_function(self):
        path, name = os.path.split(self.filename)
        self.get_file(path)
        cpath = self.config_ini['main_project']['project_path'] + self.config_ini['scanner']['ctags']
        # print(cpath)
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
            if re.match("(\w*)\.c", file) is not None:
                f = path + '/' + file
                if not os.path.isdir(f):
                    list.append(f)
        self.filelist = list

    def gen_token(self):
        for func in self.funlist:
            if func.filepath == self.filename:
                f = [func.name, func.line, func.val_type, []]
                if func.list:
                    for val in func.list:
                        ll = [val.name, val.line, val.val_type]
                        f[-1].append(ll)
                self.token_func.append(f)

        for val in self.vallist:
            if val.type != 's' and val.type != 'v':
                continue
            if val.filepath == self.filename:
                v = [val.name, val.line, val.val_type, []]
                if val.list:
                    for i in val.list:
                        ii = [i.name, i.line, i.val_type]
                        v[-1].append(ii)
                self.token_val.append(v)

    def gen_danger(self):
        try:
            sql = "SELECT * FROM functions"
            cursor.execute(sql)
            # results = cursor.fetchall()
            for row in cursor:
                # self.table_add(row[0], row[1], row[2])
                # print(row)
                for file in self.filelist:
                    f = open(file, 'r')
                    s = f.readlines()
                    f.close()
                    pattern = re.compile("\W"+row[0]+"[(]")
                    for ss in s:
                        if re.search(pattern, ss) is not None:
                            line = s.index(ss)+1
                            d = [file, "line:"+str(line), row[0], row[1], row[2]]
                            self.danger.append(d)
        except Exception as e:
            print(e)
            db.rollback()  # 回滚事务

    def gen_invalid(self):
        for f in self.funlist:
            if f.name =='main':
                main = f
                # break
        self.validfun.append(main)
        self.find_valid(main, [])
        for f in list(set(self.funlist) - set(self.validfun)):
            ff = [f.filepath, f.line, f.name]
            self.invalid_func.append(ff)

        for v in list(set(self.vallist) - set(self.validval)):
            vv = [v.filepath, v.line, v.name]
            self.invalid_val.append(vv)

    def find_valid(self, fun, l):
        code = self.scanner(fun.filepath)
        print(code)
        flag = 0
        first = True
        l.append(fun)
        fline = fun.line.split(":")[-1]
        for line in code[int(fline):]:
            if len(line) > 1:
                if line[1] == '{' or line[-1] == '{':
                    flag += 1
                    first = False
                if line[1] == '}' or line[-1] == '}':
                    flag -= 1
            if flag == 0 and first == False:
                break
            for v in self.vallist:
                if v.name in line:
                    index = line.index(v.name)
                    if len(line) > index + 1:
                        if line[index + 1] != "(" and v.line != "line:" + self.get_linenum(line[0]) and v in fun.list:
                            self.validval.append(v)
                    else:
                        if v.line != "line:" + self.get_linenum(line[0]) and v in fun.list:
                            self.validval.append(v)
            for v in self.vallist:
                if v.name in line and v not in self.validval and v.filepath == fun.filepath:
                    index = line.index(v.name)
                    if len(line) > index + 1:
                        if line[index + 1] != "(" and v.line != "line:" + self.get_linenum(line[0]):
                            print(line)
                            self.validval.append(v)
                    else:
                        if v.line != "line:" + self.get_linenum(line[0]):
                            self.validval.append(v)
            for f in self.funlist:
                if f.name in line and f not in self.validfun:
                    index = line.index(f.name)
                    if line[index + 1] == '(' and f.line != "line:" + self.get_linenum(line[0]):
                        self.validfun.append(f)
        if self.validfun != l:
            for f in list(set(self.validfun) - set(l)):
                self.find_valid(f, l)

    def scanner(self, fileName):
        path = self.config_ini['main_project']['project_path'] + self.config_ini['result']['demo']
        f = open(path, "w")
        text = "0$" + fileName + "$\n"
        f.write(text)
        f.close()
        cmd = self.config_ini['main_project']['project_path'] + self.config_ini['scanner']['lex'] + " < " + fileName
        os.system(cmd)
        f = open(path, "r")
        list = f.readlines()
        code = []
        for s in list:
            s.rstrip()
            str = s.split("$")
            result = [x.strip() for x in str if x.strip() != '']
            code.append(result)
        print(code)
        return code

    def get_linenum(self, line):
        pattern = re.compile("[0-9]+")
        m = re.search(pattern, line)
        return m.group(0)


if __name__ == '__main__':
    con = Config()
    ini = con.read_config()
    a = Analysis("D:/AAtestplaceforcode/code_aduit/", ini)
    func, val, d, vf, vv = a.run()
    # print(a.filelist)
    # for f in a.funlist:
    #     print(f.list[0].name)
    # print(a.filename)
    # print(d)
    # a.gen_report()
    # print(vv)
