import base64
import secrets

import pymysql
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.config import Config


class DB():
    def __init__(self,filepath):
        self.key=filepath
        self.config=Config()
        self.config_ini=self.config.read_config()
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
        table_name='func'
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

    def table_clear(self,table_name):
        table_name = table_name
        truncate_query = f"TRUNCATE TABLE {table_name};"
        self.cursor.execute(truncate_query)
        self.conn.commit()

    def insert_table(self,choose):
        table_name='func'
        self.table_clear(table_name)
        if choose==1:
            f=self.config_ini['main_project']['project_path']+self.config_ini['db']['danger_funcs']
        if choose==2:
            f = self.config_ini['main_project']['project_path'] + self.config_ini['db']['back_up']
        with open(f, 'r') as encrypted_file:
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
                sql = f"INSERT INTO {table_name} (name,level,description) VALUES (%s,%s,%s)"
                self.cursor.execute(sql, data)
                self.conn.commit()


