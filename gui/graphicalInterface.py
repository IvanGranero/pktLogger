
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTableWidgetItem, QListWidgetItem, QFileDialog
#from PyQt5 import QtWidgets
from PyQt5.uic import loadUi
import logThread

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.w = None        
        loadUi("gui/mainWindow.ui", self)
        for word in ['eth', 'can']:
            list_item = QListWidgetItem(str(word), self.network_list)
        self.btn_start_logger.clicked.connect(self.start_stop_logger)
        self.inline_search.returnPressed.connect(self.btn_run_filter.click)
        self.btn_run_filter.clicked.connect(self.run_filter)
        self.btn_refresh.clicked.connect(self.show_data)
        self.filter_list.itemPressed.connect(self.update_filters)
        self.filter_view.itemPressed.connect(self.select_filter)
        self.actionOpen.triggered.connect(self.open_file)     
        self.start_stop = 0

    def set_status(self, status, warning_or_success='none'):
        self.display_status.setText(status)
        if (warning_or_success == 'warning'):
            self.display_status.setStyleSheet(
                "QLabel { color : red; background-color: transparent; }")
        elif (warning_or_success == 'success'):
            self.display_status.setStyleSheet(
                "QLabel { color : lightgreen; background-color: transparent; }")        

    def open_file(self):
        filepath, dummy = QFileDialog.getOpenFileName(self, 'Open File')
        if len(filepath) > 0:
            logThread.readPackets(filepath)
            self.show_data()

    def show_data(self):
        self.inline_search.setText("index==index")
        self.run_filter()

    def update_filters(self):
        column_name = self.filter_list.currentItem().text()
        list = logThread.evalFilter('alldata.'+column_name+'.sort_values().unique()')
        self.filter_view.clear() 
        for word in list:
            list_item = QListWidgetItem(str(word), self.filter_view)

    def select_filter(self):
        column_name = self.filter_list.currentItem().text()
        argument = self.filter_view.currentItem().text()
        filter_argument = column_name +' == ' + argument
        self.inline_search.setText(filter_argument)
        self.run_filter()

    def run_filter(self):        
        filter_argument = self.inline_search.text()
        if len(filter_argument) > 0:
            try:
                self.set_status('Busy... Please wait!')

                if self.ai_checkBox.isChecked():
                    response = logThread.askopenAI(filter_argument)
                    self.set_status(response)
                    filter_argument = response
                
                data = logThread.runFilter(filter_argument)
                self.tableview.clearContents()
                self.tableview.setRowCount(len(data.index))
                len_columns = len(data.columns)
                list_columns = data.columns
                self.tableview.setColumnCount(len_columns)
                self.tableview.setHorizontalHeaderLabels(list_columns)
                self.tableview.verticalHeader().setVisible(False)
                self.tableview.setSortingEnabled(True)        
                num_rows = len(data.index)
                for i in range(num_rows):
                    for j in range(len_columns):
                        self.tableview.setItem(i, j, QTableWidgetItem(str(data.iat[i, j])))
                self.tableview.resizeColumnsToContents()
                self.tableview.resizeRowsToContents()
                self.filter_list.clear() 
                for word in list_columns:
                    list_item = QListWidgetItem(str(word), self.filter_list)
                self.set_status('Ready.')
            except Exception as e:
                print (e)
                self.set_status('There was a problem with the calculation','warning')
        else:
            self.set_status("Input a query e.g. identifier == 310 or check the AI box and use natural language.")
    
    def start_stop_logger(self):
        if (self.start_stop):
            logThread.stopLogger()
            self.show_data()
            self.btn_start_logger.setText("Start LoggerThread")
            self.start_stop = 0            
        else:
            self.btn_start_logger.setText("Stop LoggerThread")
            logThread.startLogger(self.network_list.currentItem().text())
            self.start_stop = 1

def openMainWindow(argv):
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec()