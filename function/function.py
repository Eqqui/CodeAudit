from PyQt5.QtWidgets import *
from ui.functionWidget import Ui_functionDialog
import pymysql
from config.config import Config

class functionForm(QDialog, Ui_functionDialog):
    def __init__(self, parent=None):
        super(functionForm, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.delete)
        self.config = Config()
        self.config_ini = self.config.read_config()


        self.db = pymysql.connect(
            host="localhost",
            port=int(self.config_ini['db_set']['port']),
            user=self.config_ini['db_set']['user_name'],
            password=self.config_ini['db_set']['password'],
            charset='utf8mb4',
            database=self.config_ini['db_set']['database_name']
        )
        # self.database_name = self.config_ini['db_set']['database_name']
        # self.cursor = self.db.cursor()
        self.cursor = self.db.cursor()
        self.context_show()


    def add(self):

        if self.lineEdit.text()==""or self.lineEdit_2.text()=="":
            QMessageBox.warning(self, "Alert", "添加函数信息未填完整")
            return
        fun_name = self.lineEdit.text()
        fun_level = self.comboBox.currentText()
        fun_solution = self.lineEdit_2.text()

        # print(fun_name,fun_solution)
        self.table_add(fun_name, fun_level, fun_solution)
        self.db_add(fun_name,fun_level,fun_solution)
        self.lineEdit.clear()
        self.lineEdit_2.clear()

    def context_show(self):
        try:
            sql = "SELECT * FROM functions"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            for row in results:
                self.table_add(row[0], row[1], row[2])
        except Exception as e:
            print(e)
            # self.db.rollback()  # 回滚事务


    def table_add(self, fun_name, fun_level, fun_solution):
        self.tableWidget.insertRow(self.tableWidget.rowCount())
        # print("table:"+self.tableWidget.rowCount)
        newItem = QTableWidgetItem(fun_name)
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, newItem)
        newItem = QTableWidgetItem(fun_level)
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, newItem)
        newItem = QTableWidgetItem(fun_solution)
        self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, newItem)

    def delete(self):
        del_row=self.tableWidget.currentRow()
        print(del_row)
        self.db_delete(del_row)
        self.tableWidget.removeRow(del_row)




    def db_delete(self,del_row):
        name_item=self.tableWidget.item(del_row,0)
        if name_item is not None:
            name_text=name_item.text()
            print("name_text:",name_text)
            try:
                sql = f"DELETE FROM {self.config_ini['db_set']['form_2']}  WHERE name = %s"
                self.cursor.execute(sql,name_text)
                self.db.commit()
            except Exception as e:
                print(e)
                self.db.rollback()  # 回滚事务
        else:
            print("delete null")

    def db_add(self,fun_name,fun_level,fun_solution):

        data=(fun_name,fun_level,fun_solution)
        sql = f"INSERT INTO {self.config_ini['db_set']['form_2']}(name,level,description) VALUES (%s,%s,%s)"
        self.cursor.execute(sql, data)
        self.db.commit()








