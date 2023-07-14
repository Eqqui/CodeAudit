import hashlib
import pymysql
from ui.loginWidget import Ui_loginForm
from PyQt5.QtWidgets import QWidget, QMessageBox
from startWin import MainWindow
from config.config import Config


class logWin(QWidget, Ui_loginForm):
    def __init__(self):
        super(logWin, self).__init__()
        self.setupUi(self)
        self.config = Config()
        self.config_ini = self.config.read_config()
        self.db = pymysql.connect(
            host="localhost",
            port=3306,
            user='root',
            password='',
            charset='utf8mb4',
            database='code_audit'
        )
        self.cursor = self.db.cursor()
        self.connect_db()
        self.Login.clicked.connect(self.login)
        self.Registe.clicked.connect(self.register)

    def login(self):
        if self.Account.text() == '' or self.Password.text() == '':
            QMessageBox.warning(self, "*", "输入不能为空")
        else:
            username = self.Account.text()
            password = self.Password.text()
            if self.check_credentials(username, password):
                # QMessageBox.information(self, "登录成功", "登录成功！")
                self.win = MainWindow()
                self.win.show()
                self.hide()
                # cursor.close()
                # db.close()
            else:
                QMessageBox.warning(self, "登录失败", "不存在此用户")

    def register(self):

        if self.Account.text() == '' or self.Password.text() == '':
            QMessageBox.warning(self, "*", "输入不能为空")
        else:
            username = self.Account.text()
            password = self.Password.text()
            if self.check_username(username):
                QMessageBox.warning(self, "注册失败", "用户名已存在！")
            else:
                encrypted_password = self.sha256_hash(password)
                self.add_user(username, encrypted_password)

    def check_credentials(self, username, password):

        sql = "SELECT * FROM user"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for row in results:
            if username == row[0] and self.sha256_hash(password) != row[1]:
                QMessageBox.warning(self, "登录失败", "密码错误")
                return False
            elif username == row[0] and self.sha256_hash(password) == row[1]:
                return True
        return False

    def check_username(self, username):

        sql = "SELECT id FROM user"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for row in results:
            if (username == row[0]):
                print("ID:", row[0])
                return True

        return False

    def add_user(self, username, password):

        data = (username, password)
        sql = "INSERT INTO user (id,pass_word) VALUES (%s,%s)"
        self.cursor.execute(sql, data)
        self.db.commit()
        QMessageBox.information(self, "注册成功", "注册成功！")

    def sha256_hash(self, message):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(message.encode('utf-8'))
        return sha256_hash.hexdigest()

    def connect_db(self):
        table = ["user", "functions"]
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'code_audit' AND TABLE_NAME = '{table[0]}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            print("表已存在，连接到表")
            pass
        # 连接到表进行后续操作
        else:
            print("表不存在，创建表")
            # 创建数据库
            self.cursor.execute(f"CREATE TABLE {table[0]} (id VARCHAR(20), pass_word VARCHAR(200), PRIMARY KEY (id))")
            file = self.config_ini['main_project']['project_path'] + self.config_ini['db']['user']
            f = open(file, "r")
            lines = f.readlines()
            for s in lines:
                idd = s.split(" ")[0]
                pass_word = s.split(" ")[1]
                print(idd, pass_word)
                data = [idd, pass_word]
                sql = f"INSERT INTO {table[0]} (id, pass_word) VALUES (%s,%s)"
                self.cursor.execute(sql, data)
                self.db.commit()

        # 创建表的代码
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'code_audit' AND TABLE_NAME = '{table[1]}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            print("表已存在，连接到表")
            pass
        # 连接到表进行后续操作
        else:
            print("表不存在，创建表")
            # 创建数据库
            self.cursor.execute(f"CREATE TABLE {table[1]} (name VARCHAR(20), level VARCHAR(20), description VARCHAR(200), PRIMARY KEY (name))")
            file = self.config_ini['main_project']['project_path'] + self.config_ini['db']['functions']
            f = open(file, "r")
            lines = f.readlines()
            for s in lines:
                name = s.split("\t")[0]
                level = s.split("\t")[1]
                description = s.split("\t")[2].replace("\n", "")
                data = [name, level, description]
                print(data)
                sql = f"INSERT INTO {table[1]}(name,level,description) VALUES (%s,%s,%s)"
                self.cursor.execute(sql, data)
                self.db.commit()
