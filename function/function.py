from PyQt5.QtWidgets import *
from ui.functionWidget import Ui_functionDialog
import pymysql

db = pymysql.connect(
    host="localhost",
    port=3306,
    user='root',
    password='',
    charset='utf8mb4',
    database='code_audit'
    )

cursor = db.cursor()

class functionForm(QDialog, Ui_functionDialog):
    def __init__(self, parent=None):
        super(functionForm, self).__init__(parent)
        self.setupUi(self)
        self.context_show()
        self.pushButton.clicked.connect(self.add)
        self.pushButton_2.clicked.connect(self.delete)

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
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                self.table_add(row[0], row[1], row[2])
        except Exception as e:
            print(e)
            db.rollback()  # 回滚事务


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
                sql = "DELETE FROM functions WHERE name = %s"
                cursor.execute(sql,name_text)
                db.commit()
            except Exception as e:
                print(e)
                db.rollback()  # 回滚事务
        else:
            print("delete null")

    def db_add(self,fun_name,fun_level,fun_solution):

        data=(fun_name,fun_level,fun_solution)
        sql = "INSERT INTO functions (name,level,description) VALUES (%s,%s,%s)"
        cursor.execute(sql, data)
        db.commit()








