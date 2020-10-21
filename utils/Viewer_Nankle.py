import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

class MyWindow(QtWidgets.QMainWindow):
    
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()
        self.initCanvas()
        self.show()
        
    def initUI(self):               
        #action
        openAction = QtWidgets.QAction(QtGui.QIcon('icon_open.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open Arcinfo Shape')
        openAction.triggered.connect(self.on_opendialog)
        
        saveAction = QtWidgets.QAction(QtGui.QIcon('icon_save.png'), '&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save Plot')
        saveAction.triggered.connect(self.on_savedialog)
        
        exitAction = QtWidgets.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(QtWidgets.qApp.quit)
        
        aboutAction = QtWidgets.QAction('&About', self)
        aboutAction.setShortcut('Ctrl+A')
        aboutAction.setStatusTip('About')
        aboutAction.triggered.connect(self.on_about)
        
        #menubar
        menubar = self.menuBar()
        
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction) 
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)
        
        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(aboutAction)
        
        #toolbar
        toolbar = self.addToolBar('Standard')
        toolbar.addAction(openAction)
        toolbar.addAction(saveAction)
        
        #status
        self.statusBar().showMessage('Ready')
        
        #
        self.setGeometry(300, 300, 500, 400)
        self.setWindowTitle('an example of qt plus matplotlib')
    
    def initCanvas(self):
        #Canvas
        self.fig = Figure((5.0, 4.0), dpi=100)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)
 
        # Other GUIs
        self.label = QtWidgets.QLabel('Point Number:')
        
        self.textbox = QtWidgets.QLineEdit()
        self.textbox.setMinimumWidth(20)
        self.textbox.editingFinished.connect(self.on_draw) #editingFinished
        
        self.grid_cb = QtWidgets.QCheckBox("Show &Grid")
        self.grid_cb.setChecked(False)
        self.grid_cb.stateChanged.connect(self.on_draw)
        
        # Layout with box sizers
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.label)
        hbox.addWidget(self.textbox)
        hbox.addWidget(self.grid_cb)
        # hbox.setAlignment(self.grid_cb, QtCore.Qt.AlignVCenter)
        
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)
        
        #
        self.qwidget = QtWidgets.QWidget()
        # self.canvas.setParent(self.qwidget)
        self.qwidget.setLayout(vbox)
        
        self.setCentralWidget(self.qwidget)
        
        self.textbox.setText('12')
        self.on_draw()
    
    def on_opendialog(self):
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', 'C:\\',"All files (*);;shape file (*.shp)")
        print (fname)
        self.statusBar().showMessage('openned %s' % fname[0], 2000)
    
    def on_savedialog(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', 'C:\\', "PNG (*.png)|*.png")
        print (path)
        if path:
            self.fig.savefig(path[0])
            self.statusBar().showMessage('Saved to %s' % path[0], 2000)
    
    def on_about(self):
        msg = """ A demo of using PyQt with matplotlib:
         * menubar
         * toolbar
         * statusbar
         * QFileDialog
         * QMessageBox
         * QWidget
         * FigureCanvas + Figure (matplotlib)
        """
        QtWidgets.QMessageBox.about(self, "About", msg)
    
    def on_draw(self):
        num = int(self.textbox.text()) 
        x = np.arange(num)
        y = np.sin(x)
        
        self.axes.clear()
        self.axes.grid(self.grid_cb.isChecked())
        self.axes.plot(x,y,'--o')
        
        self.canvas.draw()

#
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = MyWindow()
    sys.exit(app.exec_())
