import sqlite3
import sys

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QDialog


class AddEditDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.OKButton.clicked.connect(self.OKButtonClicked)
        self.CancelButton.clicked.connect(self.CancelButtonClicked)

    def OKButtonClicked(self):
        if self.Name.text() and self.Weight.value() != 0 and (
                self.Arabica.isChecked() or self.Robusta.isChecked()):
            self.accept()
        else:
            self.label_8.setText("Не все обязательные поля заполнены!")

    def CancelButtonClicked(self):
        self.reject()


class CoffeeGuru(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.loadTable()

    def loadTable(self):
        query = "SELECT * FROM coffee_info"
        res = self.con.cursor().execute(query).fetchall()
        if not res:
            return
        self.con.row_factory = sqlite3.Row
        colnames = self.con.cursor().execute(query).fetchone().keys()
        self.CoffeeTable.setColumnCount(len(res[0]))
        self.CoffeeTable.setRowCount(0)
        self.CoffeeTable.setHorizontalHeaderLabels(list(colnames))
        for i, row in enumerate(res):
            self.CoffeeTable.setRowCount(self.CoffeeTable.rowCount() + 1)
            for j, elem in enumerate(row):
                item = QTableWidgetItem(str(elem))
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.CoffeeTable.setItem(i, j, item)
        self.ChangeRecord.clicked.connect(self.ChangeRecordButtonClicked)
        self.AddRecord.clicked.connect(self.AddRecordButtonClicked)
        self.con.row_factory = None

    @staticmethod
    def SetValuesToDialog(dial, name, variety, roasting, grinding, taste, price, weight):
        dial.Name.setText(name)
        dial.Grinding.setCurrentText(grinding)
        dial.Arabica.setChecked('Арабика' in variety)
        dial.Robusta.setChecked('Робуста' in variety)
        dial.Roasting.setCurrentText(roasting)
        dial.TasteDesc.setPlainText(taste)
        dial.Price.setValue(price)
        dial.Weight.setValue(weight)

    @staticmethod
    def GetValuesFromDialog(dial):
        name = dial.Name.text()
        grinding = dial.Grinding.currentText()
        variety = ''
        if dial.Arabica.isChecked():
            variety = 'Арабика'
        elif dial.Robusta.isChecked():
            variety = 'Робуста'
        if dial.Arabica.isChecked() and dial.Robusta.isChecked():
            variety = 'Арабика & Робуста'
        roasting = dial.Roasting.currentText()
        taste = dial.TasteDesc.toPlainText()
        price, weight = dial.Price.value(), dial.Weight.value()
        return name, variety, roasting, grinding, taste, price, weight

    def AddRecordButtonClicked(self):
        try:
            dial = AddEditDialog(self)
            code = dial.exec()
            if code == QDialog.Accepted:
                self.con.cursor().execute('''INSERT INTO coffee_info(Название, Сорт, Обжарка, Помол, 
                [Вкусовые качества], Цена, [Вес упаковки]) VALUES(''' + ', '.join('?' * 7) + ')',
                                          self.GetValuesFromDialog(dial))
                self.con.commit()
                self.loadTable()
            dial.close()
        except Exception as e:
            print(type(e), e)

    def ChangeRecordButtonClicked(self):
        try:
            fields = ('Название', 'Сорт', 'Обжарка', 'Помол', '[Вкусовые качества]', 'Цена', '[Вес упаковки]')
            row = self.CoffeeTable.currentRow()
            data = []
            for col in range(self.CoffeeTable.columnCount()):
                data.append(self.CoffeeTable.item(row, col).text())
            data[-1], data[-2] = int(data[-1]), int(data[-2])
            _id, data = data[0], data[1:]
            dial = AddEditDialog(self)
            self.SetValuesToDialog(dial, *data)
            code = dial.exec()
            if code == QDialog.Accepted:
                self.con.cursor().execute('''UPDATE coffee_info SET ''' +
                                          ', '.join('='.join((elem, '?')) for elem in fields) +
                                          'WHERE ID=?', self.GetValuesFromDialog(dial) + (_id, ))
                self.con.commit()
                self.loadTable()
            dial.close()
        except Exception as e:
            print(type(e), e)

    def closeEvent(self, event):
        self.connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Выглядит лучше, чем стиль по умолчанию
    ex = CoffeeGuru()
    ex.show()
    sys.exit(app.exec())
