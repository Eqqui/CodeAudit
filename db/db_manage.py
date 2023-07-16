import base64
import secrets

import pymysql
from PyQt5.QtCore import pyqtSignal, QObject
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.config import Config


class DB(QObject):
    finished = pyqtSignal()
    def __init__(self,filepath):
        super(DB, self).__init__()
        self.filepath=filepath
        self.key="C:/Users/chickey/Documents/huaxin/CodeAudit/db/danger_funcs.txt"
        self.config=Config()
        self.config_ini=self.config.read_config()
        self.database_name = self.config_ini['db_set']['database_name']
        self.conn = pymysql.connect(
            host="localhost",
            port=int(self.config_ini['db_set']['port']),
            user=self.config_ini['db_set']['user_name'],
            password=self.config_ini['db_set']['password'],
            charset='utf8mb4',
            database=self.config_ini['db_set']['database_name']
        )
        self.cursor = self.conn.cursor
        self.key="C:/Users/chickey/Documents/huaxin/CodeAudit/db/danger_funcs.txt"
        self.config=Config()
        self.config_ini=self.config.read_config()
        self.database_name = self.config_ini['db_set']['database_name']
        self.conn = pymysql.connect(
            host="localhost",
            port=int(self.config_ini['db_set']['port']),
            user=self.config_ini['db_set']['user_name'],
            password=self.config_ini['db_set']['password'],
            charset='utf8mb4',
            database=self.config_ini['db_set']['database_name']
        )
        self.cursor = self.conn.cursor()

    def get_key(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256使用32字节密钥
            salt=self.key.encode(),
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(b'my_password')
        return key

    def decrypt(self,data):
        cipher = Cipher(algorithms.AES(self.get_key()), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()
        ciphertext = base64.b64decode(data)
        decrypted_padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return decrypted_data.decode()

    def encrypt(self,data):
        # 进行加密操作
        cipher = Cipher(algorithms.AES(self.get_key()), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_plaintext = padder.update(data.encode('utf-8')) + padder.finalize()

        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
        encrypted_data = base64.b64encode(ciphertext).decode()
        return encrypted_data

    def table_to_file(self):
        table_name=self.config_ini['db_set']['form_2']
        ff=self.config_ini['main_project']['project_path']+self.config_ini['db']['back_up']
        with open(ff, 'w') as file:
            self.cursor.execute(f'SELECT * FROM {table_name}')
            results=self.cursor.fetchall()
            for row in results:
                # 加密内容
                print(row[0],row[1],row[2])
                name = self.encrypt(row[0])
                level = self.encrypt(row[1])
                solution = self.encrypt(row[2])
                file.write(name + "\t" + level + "\t" + solution + '\n')
        self.finished.emit()

    def table_clear(self,table_name):
        query = f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '{self.database_name}' AND TABLE_NAME = '{table_name}'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        if result:
            truncate_query = f"TRUNCATE TABLE {table_name};"
            self.cursor.execute(truncate_query)
            self.conn.commit()
        else:
            return

    def insert_user(self,table):
        f=self.config_ini['main_project']['project_path']+self.config_ini['db']['user']
        with open(f,'r')as user_file:
            if not bool(user_file.read()):
                for line in user_file:
                    user_info=line.split('\t')
                    data=(user_info[0],user_info[1])
                    sql = f"INSERT INTO {table} (id,pass_word) VALUES (%s,%s)"
                    self.cursor.execute(sql,data)
                    self.conn.commit()


    def insert_func(self,table,file):
        with open(file, 'r') as encrypted_file:
            for line in encrypted_file:
                # 解码加密后的结果
                encrypted_data = line.strip().split('\t')
                name = encrypted_data[0]
                level = encrypted_data[1]
                solution = encrypted_data[2]
                # 解密数据
                decrypted_name = self.decrypt(name)
                decrypted_level = self.decrypt(level)
                decrypted_solution = self.decrypt(solution)

                data = (decrypted_name, decrypted_level, decrypted_solution)
                # print(data)
                sql = f"INSERT INTO {table} (name,level,description) VALUES (%s,%s,%s)"
                self.cursor.execute(sql, data)
                self.conn.commit()
            # self.finished.emit()

    def insert_table(self,choose):
        table_name_1=self.config_ini['db_set']['form_1']
        table_name_2=self.config_ini['db_set']['form_2']
        self.table_clear(table_name_2)
        # print("insert")
        if choose==1:
            f=self.config_ini['main_project']['project_path']+self.config_ini['db']['danger_funcs']
            self.insert_func(table_name_2,f)
            self.finished.emit()
            # print("finish")
        if choose==2:
            f = self.config_ini['main_project']['project_path'] + self.config_ini['db']['back_up']
            self.insert_func(table_name_2,f)
            self.finished.emit()
        if choose==3:
            self.insert_user(table_name_1)
            self.finished.emit()
