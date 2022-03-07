import sqlite3
import sys

from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem


class CoffeeGuru(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.con = sqlite3.connect("coffee.sqlite")
        self.loadTable()

    def loadTable(self):
        query = "SELECT * FROM coffee_info"
        res = self.con.cursor().execute(query).fetchall()
        print(self.con.row_factory)
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


    def closeEvent(self, event):
        self.connection.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    # Выглядит лучше, чем стиль по умолчанию
    ex = CoffeeGuru()
    ex.show()
    sys.exit(app.exec())
