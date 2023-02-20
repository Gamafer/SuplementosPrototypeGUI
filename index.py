from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import MySQLdb
from PyQt5.uic import loadUiType
import datetime
from xlrd import *
from xlsxwriter import *
import bcrypt
import qdarkstyle
#from login import Ui_Form
#from library import Ui_MainWindow

login,_ = loadUiType('ingreso.ui')
ui,_ = loadUiType('suplementos.ui')

class Login(QWidget, login):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.Handle_Login)

    def Connect_DB(self):
        self.db = MySQLdb.connect(host='localhost', user='adminmanejoinventario', password='adminmanejoinventario', db='ManejoInventario')
        self.cur = self.db.cursor()

    def Handle_Login(self):
        self.Connect_DB()

        username = self.lineEdit.text()
        password = self.lineEdit_2.text()

        sql = '''SELECT * FROM users'''
        self.cur.execute(sql)
        data = self.cur.fetchall()

        for row in data:
            if username == row[0] and bcrypt.checkpw(password.encode('utf8'), row[3].encode('utf8')):
                self.window2 = MainApp(row[4])
                self.window2.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                self.close()
                self.window2.show()
            else:
                self.label_3.setText('*Asegurese que insertó sus datos de manera correcta*')
                self.lineEdit_2.setText('')

class MainApp(QMainWindow, ui):
    def __init__(self, session = ''):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self._session = session

        self.Handle_UI_Changes()
        self.Handle_Buttons()
        self.Open_Inventory_Tab()

        self.Handle_Inventory()
        self.Fill_Registered_Sales()

    def Handle_UI_Changes(self):
        self.tabWidget.tabBar().setVisible(False)
        self.tabWidget_2.tabBar().setVisible(False)

        if self._session == 'admin':
            self.pushButton_3.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_5.setEnabled(True)

    def Handle_Buttons(self):
        self.pushButton.clicked.connect(self.Open_Inventory_Tab)
        self.pushButton_2.clicked.connect(self.Open_Sales_Tab)
        self.pushButton_3.clicked.connect(self.Open_Users_Tab)
        self.pushButton_4.clicked.connect(self.Open_Manage_Tab)
        self.pushButton_5.clicked.connect(self.Open_Report_Tab)

        self.pushButton_21.clicked.connect(self.Filter)
        self.pushButton_19.clicked.connect(self.Filter)

        self.radioButton.toggled.connect(self.Handle_Filters)
        self.radioButton_2.toggled.connect(self.Handle_Filters)
        self.radioButton_3.toggled.connect(self.Handle_Filters)
        self.radioButton_4.toggled.connect(self.Handle_Filters)
        self.radioButton_5.toggled.connect(self.Handle_Filters)
        self.radioButton_6.toggled.connect(self.Handle_Filters)
        self.radioButton_7.toggled.connect(self.Handle_Filters)
        self.radioButton_8.toggled.connect(self.Handle_Filters)
        self.radioButton_9.toggled.connect(self.Handle_Filters)
        self.radioButton_10.toggled.connect(self.Handle_Filters)
        self.radioButton_11.toggled.connect(self.Handle_Filters)

        self.pushButton_7.clicked.connect(self.Search_Product)
        self.pushButton_8.clicked.connect(self.Calculate_Product_Total)
        self.pushButton_6.clicked.connect(self.Register_Sale)
        self.pushButton_22.clicked.connect(self.Add_Ticket)

        self.pushButton_9.clicked.connect(self.Create_User)
        self.pushButton_12.clicked.connect(self.Search_User)
        self.pushButton_11.clicked.connect(self.Edit_User)
        self.pushButton_13.clicked.connect(self.Delete_User)

        self.pushButton_14.clicked.connect(self.Add_Product)
        self.pushButton_16.clicked.connect(self.Search_Product)
        self.pushButton_15.clicked.connect(self.Edit_Product)
        self.pushButton_17.clicked.connect(self.Delete_Product)

        self.radioButton_12.toggled.connect(self.Handle_Types)
        self.radioButton_13.toggled.connect(self.Handle_Types)
        self.checkBox.toggled.connect(self.Handle_Types)

        self.pushButton_18.clicked.connect(self.Export_Inventory)
        self.pushButton_20.clicked.connect(self.Export_Sales)

    def Connect_DB(self):
        self.db = MySQLdb.connect(host='localhost', user='adminmanejoinventario', password='adminmanejoinventario', db='ManejoInventario')
        self.cur = self.db.cursor()

    def SetupComboBoxes(self, box, type = ''):
        box.clear()
        if type == 'p':
            box.addItem('user')
            box.addItem('admin')
        elif type == 'm':
            self.Connect_DB()

            sql = '''SELECT typeOfSupplement FROM product'''
            self.cur.execute(sql)
            data = self.cur.fetchall()

            items = []

            box.addItem('----')
            for type in data:
                items.append(type[0])

            items = list(set(items))

            for item in items:
                box.addItem(item)

            self.db.close()
        else:
            pass

    @staticmethod
    def RepresentsInt(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def RepresentsFloat(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def helpComboBox(self, box, text):
        try:
            box.findText(text)
            return True
        except ValueError:
            return False

    ##############################
    ######## open tabs ###########
    ##############################

    def Open_Inventory_Tab(self):
        self.tabWidget.setCurrentIndex(0)

        if self._session == 'admin':
            self.tabWidget_2.setCurrentIndex(1)
        else:
            self.tabWidget_2.setCurrentIndex(0)

        self.SetupComboBoxes(self.comboBox, 'm')
        self.SetupComboBoxes(self.comboBox_4, 'm')

    def Open_Sales_Tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.Fill_From_Selected()

    def Open_Users_Tab(self):
        self.tabWidget.setCurrentIndex(2)
        self.SetupComboBoxes(self.comboBox_2, 'p')

    def Open_Manage_Tab(self):
        self.tabWidget.setCurrentIndex(3)
        self.SetupComboBoxes(self.comboBox_6, 'm')
        self.SetupComboBoxes(self.comboBox_7, 'm')

    def Open_Report_Tab(self):
        self.tabWidget.setCurrentIndex(4)

    ##############################
    ###### inventory tab #########
    ##############################

    def Handle_Inventory(self):
        self.Connect_DB()

        if self._session == 'admin':
            self.cur.execute('''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product''')
            data = self.cur.fetchall()

            self.FillTable(self.tableWidget_2, data)
        elif self._session == 'user':
            self.cur.execute('''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product''')
            data = self.cur.fetchall()

            self.FillTable(self.tableWidget, data)
        else:
            pass

    def Handle_Filters(self):
        if self.radioButton.isChecked() == True:
            self.groupBox.setEnabled(True)
        else:
            self.groupBox.setEnabled(False)
            self.lineEdit.setText('')
        if self.radioButton_2.isChecked() == True:
            self.groupBox_2.setEnabled(True)
        else:
            self.groupBox_2.setEnabled(False)
            self.lineEdit_2.setText('')
        if self.radioButton_3.isChecked() == True:
            self.groupBox_3.setEnabled(True)
        else:
            self.groupBox_3.setEnabled(False)
            self.comboBox.setCurrentIndex(0)
        if self.radioButton_4.isChecked() == True:
            self.groupBox_4.setEnabled(True)
        else:
            self.groupBox_4.setEnabled(False)
            self.lineEdit_3.setText('')
        if self.radioButton_5.isChecked() == True:
            self.groupBox.setEnabled(False)
            self.groupBox_2.setEnabled(False)
            self.groupBox_3.setEnabled(False)
            self.groupBox_4.setEnabled(False)

            self.lineEdit.setText('')
            self.lineEdit_2.setText('')
            self.comboBox.setCurrentIndex(0)
            self.lineEdit_3.setText('')
        else:
            self.pushButton_21.setEnabled(True)

        if self.radioButton_6.isChecked() == True:
            self.groupBox_5.setEnabled(True)
        else:
            self.groupBox_5.setEnabled(False)
            self.lineEdit_10.setText('')
        if self.radioButton_7.isChecked() == True:
            self.groupBox_6.setEnabled(True)
        else:
            self.groupBox_6.setEnabled(False)
            self.lineEdit_11.setText('')
        if self.radioButton_8.isChecked() == True:
            self.groupBox_7.setEnabled(True)
        else:
            self.groupBox_7.setEnabled(False)
            self.comboBox_4.setCurrentIndex(0)
        if self.radioButton_9.isChecked() == True:
            self.groupBox_10.setEnabled(True)
        else:
            self.groupBox_10.setEnabled(False)
            self.lineEdit_14.setText('')
        if self.radioButton_10.isChecked() == True:
            self.groupBox_9.setEnabled(True)
        else:
            self.groupBox_9.setEnabled(False)
            self.lineEdit_12.setText('')
        if self.radioButton_11.isChecked() == True:
            self.groupBox_5.setEnabled(False)
            self.groupBox_6.setEnabled(False)
            self.groupBox_7.setEnabled(False)
            self.groupBox_10.setEnabled(False)
            self.groupBox_9.setEnabled(False)

            self.lineEdit_10.setText('')
            self.lineEdit_11.setText('')
            self.comboBox_4.setCurrentIndex(0)
            self.lineEdit_14.setText('')
            self.lineEdit_12.setText('')
        else:
            self.pushButton_19.setEnabled(True)

    def Filter(self):
        self.Connect_DB()

        if self._session == 'user':
            name = self.lineEdit.text()
            productCode = self.lineEdit_2.text()
            type = self.comboBox.currentText()
            price = self.lineEdit_3.text()

            table = self.tableWidget

            if self.radioButton_5.isChecked() == True:
                self.Handle_Inventory()
            elif self.radioButton.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product WHERE name=%s'''
                self.cur.execute(sql, [(name)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_2.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product WHERE productCode=%s'''
                self.cur.execute(sql, [(productCode)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_3.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product WHERE typeOfSupplement=%s'''
                self.cur.execute(sql, [(type)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_4.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product WHERE salePrice=%s'''
                self.cur.execute(sql, [(price)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
        elif self._session == 'admin':
            name = self.lineEdit_10.text()
            productCode = self.lineEdit_11.text()
            type = self.comboBox_4.currentText()
            profit = self.lineEdit_14.text()
            price = self.lineEdit_12.text()

            table = self.tableWidget_2

            if self.radioButton_11.isChecked() == True:
                self.Handle_Inventory()
            elif self.radioButton_6.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product WHERE name=%s'''
                self.cur.execute(sql, [(name)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_7.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product WHERE productCode=%s'''
                self.cur.execute(sql, [(productCode)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_8.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product WHERE typeOfSupplement=%s'''
                self.cur.execute(sql, [(type)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_9.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product WHERE (salePrice-adquisitionPrice)=%s'''
                self.cur.execute(sql,[(profit)])
                data = self.cur.fetchall()

                self.FillTable(table, data)
            elif self.radioButton_10.isChecked() == True:
                sql = '''SELECT productCode, name, typeOfSupplement, salePrice, adquisitionPrice, stock FROM product WHERE salePrice=%s'''
                self.cur.execute(sql, [(price)])
                data = self.cur.fetchall()

                self.FillTable(table, data)

    def FillTable(self, table, data):
        if self._session == 'user':
            if data:
                table.setRowCount(0)
                table.insertRow(0)
                for row, form in enumerate(data):
                    for column, item in enumerate(form):
                        table.setItem(row, column, QTableWidgetItem(str(item)))
                        column += 1

                    row_position = table.rowCount()
                    table.insertRow(row_position)
        elif self._session == 'admin':
            if data:
                table.setRowCount(0)
                table.insertRow(0)
                for row, form in enumerate(data):
                    for column, item in enumerate(form):
                        table.setItem(row, column, QTableWidgetItem(str(item)))
                        column += 1

                    row_position = table.rowCount()
                    table.insertRow(row_position)

                for row, form in enumerate(data):
                    profit = form[3] - form[4]
                    self.tableWidget_2.setItem(row, 4, QTableWidgetItem(str(profit)))

    ##############################
    ######### sale tab ###########
    ##############################

    def Fill_From_Selected(self):
        if self._session == 'user':
            inventory_table = self.tableWidget

            if not inventory_table.selectedItems():
                pass
            else:
                row = inventory_table.currentRow()
                currentproductid = (inventory_table.item(row, 0).text())
                self.lineEdit_15.setText(currentproductid)
                self.Search_Product()
        elif self._session == 'admin':
            inventory_table = self.tableWidget_2

            if not inventory_table.selectedItems():
                pass
            else:
                row = inventory_table.currentRow()
                currentproductid = (inventory_table.item(row, 0).text())
                self.lineEdit_15.setText(currentproductid)
                self.Search_Product()
        else:
            pass

    def Search_Product(self):
        self.Connect_DB()

        if self.tabWidget.currentIndex() == 1:
            code = self.lineEdit_15.text()

            sql = '''SELECT productCode, name, typeOfSupplement, salePrice, stock FROM product WHERE productCode = %s'''
            self.cur.execute(sql, [(code)])

            data = self.cur.fetchone()


            self.pushButton_6.setEnabled(False)

            self.label_34.setText('')
            self.label_6.setText('')
            self.lineEdit_4.setText('')

            try:
                self.label_30.setText(str(data[0]))
                self.label_28.setText(data[1])
                self.label_31.setText(data[2])
                self.label_29.setText('$' + str(data[3]))
                self.label_27.setText(str(data[4]))

                self.lineEdit_4.setEnabled(True)
                self.pushButton_8.setEnabled(True)
            except TypeError:
                self.label_6.setText('*No existe ese producto, intente de nuevo*')

        elif self.tabWidget.currentIndex() == 3:
            code = self.lineEdit_36.text()

            sql = '''SELECT name, typeOfSupplement, adquisitionPrice, salePrice, stock FROM product WHERE productCode = %s'''
            self.cur.execute(sql, [(code)])

            data = self.cur.fetchone()

            try:
                self.lineEdit_31.setText(data[0])
                self.comboBox_7.setCurrentText(data[1])
                self.lineEdit_34.setText(str(data[2]))
                self.lineEdit_33.setText(str(data[3]))
                self.lineEdit_35.setText(str(data[4]))

                self.ToggleEditSettings(True)
            except TypeError:
                pass
        else:
            pass

    def Calculate_Product_Total(self):
        quantity = self.lineEdit_4.text()
        price = self.label_29.text().split(sep='$')
        price = float(price[1])
        inventory = int(self.label_27.text())
        quantity = 0

        try:
            quantity = int(self.lineEdit_4.text())
        except (ValueError, TypeError):
            self.label_6.setText('*Cantidad inválida, intente de nuevo*')
            #print('Hello')

        #self.lineEdit_4.setEnabled(False)

        ## CLEAN UP ##
        self.label_6.setText('')
        self.label_34.setText('')
        if inventory >= quantity and quantity > 0:
            total = float(int(price * int(quantity)*100)/100)
            self.label_34.setText('$' + str(total))
            self.pushButton_22.setEnabled(True)
            self.lineEdit_4.setEnabled(False)
        elif quantity <= 0:
            self.label_6.setText('*Cantidad inválida, intente de nuevo*')
        else:
            self.label_6.setText('*No hay suficiente inventario*')

    def Add_Ticket(self):
        code = self.label_30.text()
        name = self.label_28.text()
        quantity = self.lineEdit_4.text()
        total = self.label_34.text()

        table = self.tableWidget_3
        table.setEnabled(True)
        self.label_35.setEnabled(True)

        row_count = table.rowCount()
        table.insertRow(row_count)
        row = row_count
        table.setItem(row, 0, QTableWidgetItem(str(code)))
        table.setItem(row, 1, QTableWidgetItem(str(name)))
        table.setItem(row, 2, QTableWidgetItem(str(quantity)))
        table.setItem(row, 3, QTableWidgetItem(str(total)))

        self.pushButton_22.setEnabled(False)

        total = total.split(sep='$')
        total = float(total[1])

        if self.label_38.text() == '':
            totalTicket = 0
        else:
            totalTicket = float(self.label_38.text())

        totalTicket += total
        totalTicket = float(int(totalTicket * 100)/100)

        self.label_38.setText(str(totalTicket))
        self.pushButton_6.setEnabled(True)
        self.label_37.setEnabled(True)
        self.label_68.setEnabled(True)

    def Register_Sale(self):
        self.Connect_DB()
        #self.Calculate_Product_Total()

        ticket = self.tableWidget_3

        count = ticket.rowCount()

        today_datetime = datetime.datetime.today()

        for row in range(0, count):
            data = []
            for column in range(0, 4):
                item = ticket.item(row, column).text()
                data.append(item)

            productCode = str(data[0])
            sql = '''SELECT stock FROM product WHERE productCode=%s'''
            self.cur.execute(sql, [(productCode)])
            stock = self.cur.fetchone()

            inventory = int(stock[0]) - int(data[2])
            total = data[3].split(sep='$')
            data[3] = float(total[1])

            self.cur.execute('''UPDATE product SET stock=%s WHERE productCode = %s''', (str(inventory), (data[0])))

            self.cur.execute('''INSERT INTO sale(productCode, quantity, total, dateTime)
                                VALUES (%s, %s, %s, %s)''', (data[0], data[2], data[3], today_datetime))

            self.db.commit()

        self.statusBar().showMessage('Venta Registrada')

        for row in range(0, count):
            ticket.removeRow(0)

        self.label_30.setText('')
        self.label_28.setText('')
        self.label_31.setText('')
        self.label_29.setText('')
        self.label_27.setText('')
        self.lineEdit_4.setText('')
        self.lineEdit_15.setText('')
        self.label_38.setText('')
        self.label_34.setText('')
        ticket.setEnabled(False)
        self.label_35.setEnabled(False)
        self.label_37.setEnabled(False)
        self.label_68.setEnabled(False)
        self.pushButton_8.setEnabled(False)
        self.pushButton_6.setEnabled(False)
        self.pushButton_22.setEnabled(False)

        self.Fill_Registered_Sales()

    def Fill_Registered_Sales(self):
        self.Connect_DB()

        sql = '''SELECT productCode, name, quantity, total, dateTime FROM sale NATURAL JOIN product'''
        self.cur.execute(sql)
        data = self.cur.fetchall()

        table = self.tableWidget_4

        if data:
            table.setRowCount(0)
            table.insertRow(0)
            for row, form in enumerate(data):
                for column, item in enumerate(form):
                    table.setItem(row, column, QTableWidgetItem(str(item)))
                    column += 1

                row_position = table.rowCount()
                table.insertRow(row_position)



    ##############################
    ######### users tab ##########
    ##############################

    def ToggleEditSettings(self, boolean):
        if self.tabWidget.currentIndex() == 2:
            self.label_39.setEnabled(boolean)
            self.label_40.setEnabled(boolean)
            self.label_41.setEnabled(boolean)
            self.label_42.setEnabled(boolean)
            self.label_43.setEnabled(boolean)
            self.label_44.setEnabled(boolean)
            self.lineEdit_20.setEnabled(boolean)
            self.lineEdit_21.setEnabled(boolean)
            self.lineEdit_22.setEnabled(boolean)
            self.lineEdit_23.setEnabled(boolean)
            self.lineEdit_24.setEnabled(boolean)
            self.comboBox_5.setEnabled(boolean)
            self.pushButton_11.setEnabled(boolean)
            self.pushButton_13.setEnabled(boolean)
        elif self.tabWidget.currentIndex() == 3:
            self.label_55.setEnabled(boolean)
            self.label_54.setEnabled(boolean)
            self.label_53.setEnabled(boolean)
            self.label_56.setEnabled(boolean)
            self.label_52.setEnabled(boolean)
            self.label_62.setEnabled(boolean)
            self.label_61.setEnabled(boolean)
            self.lineEdit_31.setEnabled(boolean)
            self.lineEdit_34.setEnabled(boolean)
            self.lineEdit_33.setEnabled(boolean)
            self.lineEdit_35.setEnabled(boolean)
            self.comboBox_7.setEnabled(boolean)
            self.checkBox.setEnabled(boolean)
            self.pushButton_15.setEnabled(boolean)
            self.pushButton_17.setEnabled(boolean)


    def Create_User(self):
        self.Connect_DB()

        fullName = self.lineEdit_5.text()
        username = self.lineEdit_6.text()
        email = self.lineEdit_7.text()
        type = self.comboBox_2.currentText()
        password = self.lineEdit_9.text()
        confirmPassword = self.lineEdit_13.text()

        self.label_65.setText('')

        if username == '' or fullName == '' or email == '' or password == '':
            self.label_65.setText('*Uno o más campos están vacíos*')
        else:
            if password == confirmPassword:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf8'), salt)

                self.cur.execute('''INSERT INTO users(username, name, email, password, type)
                VALUES(%s, %s, %s, %s,%s)''', (username, fullName, email, hashed, type))

                self.db.commit()
                self.statusBar().showMessage('Usuario Creado')

                self.lineEdit_5.setText('')
                self.lineEdit_6.setText('')
                self.lineEdit_7.setText('')
                self.comboBox_2.setCurrentIndex(0)
                self.lineEdit_9.setText('')
                self.lineEdit_13.setText('')
            else:
                self.label_65.setText('*Las contraseñas ingresadas no coinciden*')

    def Search_User(self):
        self.Connect_DB()

        username = self.lineEdit_25.text()

        sql = '''SELECT name, username, email, type FROM users WHERE username = %s'''
        self.cur.execute(sql, [(username)])

        data = self.cur.fetchone()

        try:
            self.lineEdit_20.setText(data[0])
            self.lineEdit_21.setText(data[1])
            self.lineEdit_22.setText(data[2])
            self.comboBox_5.setCurrentText(data[3])
            self.lineEdit_23.setPlaceholderText('XXXXXXXX')
            self.lineEdit_24.setPlaceholderText('XXXXXXXX')

            self.SetupComboBoxes(self.comboBox_5, 'p')

            self.ToggleEditSettings(True)
        except TypeError:
            pass

    def Edit_User(self):
        self.Connect_DB()

        userSearch = self.lineEdit_25.text()
        username = self.lineEdit_21.text()
        fullName = self.lineEdit_20.text()
        email = self.lineEdit_22.text()
        type = self.comboBox_5.currentText()
        password = self.lineEdit_23.text()
        confirmPassword = self.lineEdit_24.text()

        if password == '':
            self.cur.execute('''UPDATE users SET username=%s, name=%s, email=%s, type=%s 
            WHERE username = %s''', (username, fullName, email, type, userSearch))

            self.db.commit()
            self.statusBar().showMessage('Usuario Actualizado')

            self.lineEdit_20.setText('')
            self.lineEdit_21.setText('')
            self.lineEdit_22.setText('')
            self.comboBox_5.setCurrentIndex(0)
            self.lineEdit_23.setPlaceholderText('')
            self.lineEdit_23.setText('')
            self.lineEdit_24.setPlaceholderText('')
            self.lineEdit_24.setText('')
            self.label_66.setText('')

            self.ToggleEditSettings(False)
        else:
            if password == confirmPassword:
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf8'), salt)

                self.cur.execute('''UPDATE users SET username=%s, name=%s, email=%s, password=%s, type=%s 
                WHERE username = %s''', (username, fullName, email, hashed, type, userSearch))

                self.db.commit()
                self.statusBar().showMessage('Usuario Actualizado')

                self.lineEdit_20.setText('')
                self.lineEdit_21.setText('')
                self.lineEdit_22.setText('')
                self.comboBox_5.setCurrentIndex(0)
                self.lineEdit_23.setPlaceholderText('')
                self.lineEdit_23.setText('')
                self.lineEdit_24.setPlaceholderText('')
                self.lineEdit_24.setText('')
                self.label_66.setText('')

                self.ToggleEditSettings(False)
            else:
                self.label_66.setText('*Las contraseñas ingresadas no coinciden*')
                self.lineEdit_23.setText('')
                self.lineEdit_24.setText('')

    def Delete_User(self):
        self.Connect_DB()

        userSearch = self.lineEdit_25.text()

        warning = QMessageBox.warning(self, 'Borrar Usuario', '¿Estás seguro que quieres borrar este usuario?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            sql = '''DELETE FROM users WHERE username = %s'''
            self.cur.execute(sql, [(userSearch)])

            self.db.commit()
            self.statusBar().showMessage('Usuario Eliminado')

            self.lineEdit_20.setText('')
            self.lineEdit_21.setText('')
            self.lineEdit_22.setText('')
            self.comboBox_5.setCurrentIndex(0)
            self.lineEdit_23.setPlaceholderText('')
            self.lineEdit_23.setText('')
            self.lineEdit_24.setPlaceholderText('')
            self.lineEdit_24.setText('')
            self.label_66.setText('')
            self.lineEdit_25.setText('')

            self.ToggleEditSettings(False)

    ##############################
    ######### manage tab #########
    ##############################

    def Add_Product(self):
        self.Connect_DB()

        self.label_67.setText('')

        invalidException = False
        negativeException = False
        nullException = False

        name = self.lineEdit_26.text()
        type = self.comboBox_6.currentText()
        newType = self.lineEdit_27.text()

        adquisitionPrice = self.lineEdit_28.text()
        if self.RepresentsFloat(adquisitionPrice) == True:
            adquisitionPrice = float(adquisitionPrice)
        else: invalidException = True

        salePrice = self.lineEdit_29.text()
        if self.RepresentsFloat(salePrice) == True:
            salePrice = float(salePrice)
        else: invalidException = True

        stock = self.lineEdit_30.text()
        if self.RepresentsFloat(stock) == True:
            stock = int(stock)
        else: invalidException = True

        if invalidException == False:
            #print('All are numbers')
            if adquisitionPrice >= 0 and salePrice >= 0 and stock >= 0:
                pass#print('All are positive')
            else: negativeException = True #print('>=1 is negative')

            if negativeException == False:
                if name != '':
                    pass
                else:
                    nullException = True
                    #print('Name is null')

                if self.radioButton_12.isChecked() == True and self.comboBox_6.currentIndex() == 0:
                    nullException = True
                    #print('Type is null')
                else: pass

                if self.radioButton_13.isChecked() == True and newType == '':
                    nullException = True
                    #print('New Type is null')
                else: pass

        else: pass#print('>=1 are not numbers')

        if nullException == False and negativeException == False and invalidException == False:
            #print('Proceed')
            if self.radioButton_12.isChecked() == True:
                self.cur.execute('''INSERT INTO product(name, typeOfSupplement, adquisitionPrice, salePrice, stock)
                VALUES (%s, %s, %s, %s, %s)''', (name, type, adquisitionPrice, salePrice, stock))
            elif self.radioButton_13.isChecked() == True:
                self.cur.execute('''INSERT INTO product(name, typeOfSupplement, adquisitionPrice, salePrice, stock)
                VALUES (%s, %s, %s, %s, %s)''', (name, newType, adquisitionPrice, salePrice, stock))
            else:
                pass

            self.db.commit()
            self.statusBar().showMessage('Producto Nuevo Agregado al Inventario')

            self.SetupComboBoxes(self.comboBox_6, 'm')
            self.SetupComboBoxes(self.comboBox_7, 'm')

            self.lineEdit_26.setText('')
            self.comboBox_6.setCurrentIndex(0)
            self.lineEdit_27.setText('')
            self.lineEdit_28.setText('')
            self.lineEdit_29.setText('')
            self.lineEdit_30.setText('')
        else: pass#print('>=1 null')

        self.Handle_Inventory()

    def Edit_Product(self):
        self.Connect_DB()

        code = self.lineEdit_36.text()
        name = self.lineEdit_31.text()
        type = self.comboBox_7.currentText()
        editType = self.lineEdit_32.text()
        adquisitionPrice = self.lineEdit_34.text()
        salePrice = self.lineEdit_33.text()
        stock = self.lineEdit_35.text()

        if self.checkBox.isChecked() == True:
            self.cur.execute('''UPDATE product SET name=%s, typeOfSupplement=%s, adquisitionPrice=%s, salePrice=%s, stock=%s 
            WHERE productCode=%s''', (name, editType, adquisitionPrice, salePrice, stock, code))

            self.cur.execute('''UPDATE product SET typeOfSupplement=%s WHERE typeOfSupplement=%s''', (editType, type))
        else:
            self.cur.execute('''UPDATE product SET name=%s, typeOfSupplement=%s, adquisitionPrice=%s, salePrice=%s, stock=%s 
            WHERE productCode=%s''', (name, type, adquisitionPrice, salePrice, stock, code))

        self.db.commit()
        self.statusBar().showMessage('Inventario Actualizado')

        self.SetupComboBoxes(self.comboBox_6, 'm')
        self.SetupComboBoxes(self.comboBox_7, 'm')

        self.lineEdit_31.setText('')
        self.comboBox_7.setCurrentIndex(0)
        self.lineEdit_32.setText('')
        self.lineEdit_34.setText('')
        self.lineEdit_33.setText('')
        self.lineEdit_35.setText('')
        self.lineEdit_36.setText('')

        self.ToggleEditSettings(False)

        self.Handle_Inventory()

    def Delete_Product(self):
        self.Connect_DB()

        code = self.lineEdit_36.text()

        warning = QMessageBox.warning(self, 'Eliminar Producto', '¿Estás seguro que quieres borrar éste producto del inventario?',
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if warning == QMessageBox.Yes:
            sql = '''DELETE FROM product WHERE productCode = %s'''
            self.cur.execute(sql, [(code)])

            self.db.commit()
            self.statusBar().showMessage('Producto Eliminado')

            self.lineEdit_31.setText('')
            self.comboBox_7.setCurrentIndex(0)
            self.lineEdit_32.setText('')
            self.lineEdit_34.setText('')
            self.lineEdit_33.setText('')
            self.lineEdit_35.setText('')
            self.lineEdit_36.setText('')

            self.ToggleEditSettings(False)

            self.Handle_Inventory()

    def Handle_Types(self):
        if self.radioButton_12.isChecked() == True:
            self.label_47.setEnabled(True)
            self.comboBox_6.setEnabled(True)
        else:
            self.label_47.setEnabled(False)
            self.comboBox_6.setEnabled(False)
        if self.radioButton_13.isChecked() == True:
            self.label_48.setEnabled(True)
            self.lineEdit_27.setEnabled(True)
        else:
            self.label_48.setEnabled(False)
            self.lineEdit_27.setEnabled(False)
        if self.checkBox.isChecked() == True:
            self.label_57.setEnabled(True)
            self.lineEdit_32.setEnabled(True)

            type = self.comboBox_7.currentText()
            self.lineEdit_32.setText(type)
        else:
            self.label_57.setEnabled(False)
            self.lineEdit_32.setEnabled(False)

    ##############################
    ######### export tab #########
    ##############################

    def Export_Inventory(self):
        self.Connect_DB()

        self.cur.execute('''SELECT productCode, name, typeOfSupplement, adquisitionPrice, salePrice, 
        (salePrice-adquisitionPrice) as ganancia, stock FROM product''')
        data = self.cur.fetchall()

        date = datetime.date.today()
        workbookName = 'Inventario ' + str(date) + '.xlsx'

        wb = Workbook(workbookName)
        inventory_sheet = wb.add_worksheet('Inventario')

        inventory_sheet.write(0,0,'Código')
        inventory_sheet.write(0,1,'Nombre')
        inventory_sheet.write(0,2,'Tipo')
        inventory_sheet.write(0,3,'Precio de Adquisición')
        inventory_sheet.write(0,4,'Precio de Venta')
        inventory_sheet.write(0,5,'Ganancia')
        inventory_sheet.write(0,6, 'Inventario')

        self.Fill_Excel(inventory_sheet, data)

        self.cur.execute('''SELECT * FROM users''')
        data = self.cur.fetchall()

        users_sheet = wb.add_worksheet('Usuarios')

        users_sheet.write(0,0, 'Usuario')
        users_sheet.write(0,1, 'Nombre Completo')
        users_sheet.write(0,2, 'Correo')
        users_sheet.write(0,3, 'Contraseña')
        users_sheet.write(0,4, 'Permiso')

        self.Fill_Excel(users_sheet, data)

        wb.close()
        self.statusBar().showMessage('Inventario Exportado a ' + workbookName)

    def Export_Sales(self):
        self.Connect_DB()

        self.cur.execute('''SELECT saleCode, productCode, name, quantity, total, (salePrice-adquisitionPrice) as ganancia, 
        dateTime FROM sale NATURAL JOIN product''')
        data = self.cur.fetchall()

        date = datetime.date.today()
        workbookName = 'Ventas ' + str(date) + '.xlsx'

        wb = Workbook(workbookName)
        sales_sheet = wb.add_worksheet('Ventas')

        sales_sheet.write(0,0, 'Código de Venta')
        sales_sheet.write(0,1, 'Código del Producto')
        sales_sheet.write(0,2, 'Nombre del Producto')
        sales_sheet.write(0,3, 'Cantidad Vendida')
        sales_sheet.write(0,4, 'Total')
        sales_sheet.write(0,5, 'Ganancia')
        sales_sheet.write(0,6, 'Fecha y Hora')

        self.Fill_Excel(sales_sheet, data)

        wb.close()
        self.statusBar().showMessage('Ventas Exportadas a ' + workbookName)

        # calcs_sheet = wb.add_worksheet('Cálculos')
        #
        # self.cur.execute('''SELECT ''')
        #
        # calcs_sheet.write(0, 0, 'Mes')
        # calcs_sheet.write(1, 0, 'Enero')
        # calcs_sheet.write(2, 0, 'Febrero')
        # calcs_sheet.write(3, 0, 'Marzo')
        # calcs_sheet.write(4, 0, 'Abril')
        # calcs_sheet.write(5, 0, 'Mayo')
        # calcs_sheet.write(6, 0, 'Junio')
        # calcs_sheet.write(7, 0, 'Julio')
        # calcs_sheet.write(8, 0, 'Agosto')
        # calcs_sheet.write(9, 0, 'Septiembre')
        # calcs_sheet.write(10, 0, 'Octubre')
        # calcs_sheet.write(11, 0, 'Noviembre')
        # calcs_sheet.write(12, 0, 'Diciembre')
        #
        #
        # calcs_sheet.write(0, 1, 'Total Ganancias')

        #calcs_sheet.write(0,0,'Total Ventas')
        #calcs_sheet.write(0,1,'Total Ganancias')


    def Fill_Excel(self, sheet, data):
        row_number = 1
        for row in data:
            column_number = 0
            for item in row:
                sheet.write(row_number, column_number, str(item))
                column_number += 1
            row_number += 1

def main():
    app = QApplication(sys.argv)
    window = Login()
    window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()