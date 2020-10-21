import sys 
from PyQt5 import QtGui,QtCore 
import matplotlib 
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar 
from matplotlib.figure import Figure 
import numpy as np 

class MyWindow(QtGui.QMainWindow): 
    def __init__(self): 
        super(MyWindow, self).__init__() 
        self.initUI() 
        self.initCanvas() 
    
    def initUI(self):
        #action 
        openAction = QtGui.QAction(QtGui.QIcon('icon_open.png'), 'Open', self) 
        openAction.setShortcut('Ctrl+O') 
        openAction.setStatusTip('Open Arcinfo Shape') 
        openAction.triggered.connect(self.on_opendialog) 
        saveAction = QtGui.QAction(QtGui.QIcon('icon_save.png'), '&Save', self) 
        saveAction.setShortcut('Ctrl+S') 

        saveAction.setStatusTip('Save Plot') 
        saveAction.triggered.connect(self.on_savedialog) 
        exitAction = QtGui.QAction('&Exit', self) 
        exitAction.setShortcut('Ctrl+Q') 
        exitAction.setStatusTip('Exit application') 
        exitAction.triggered.connect(QtGui.qApp.quit) 
        aboutAction = QtGui.QAction('&About', self) 
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
        self.show()

    def initCanvas(self): 
        self.fig = Figure((5.0, 4.0), dpi=100) 
        self.axes = self.fig.add_subplot(111) 
        self.qwidget = QtGui.QWidget() 
        self.canvas = FigureCanvas(self.fig) 
        self.canvas.setParent(self.qwidget) 

        # Other GUI controls 
        self.label = QtGui.QLabel('Point Number:') 
        self.textbox = QtGui.QLineEdit() 
        self.textbox.setMinimumWidth(20) 
        self.textbox.editingFinished.connect(self.on_draw) #editingFinished 

        self.grid_cb = QtGui.QCheckBox("Show &Grid") 
        self.grid_cb.setChecked(False) 
        self.grid_cb.stateChanged.connect(self.on_draw) 

        # Layout with box sizers 
        hbox = QtGui.QHBoxLayout() 
        hbox.addWidget(self.label) 
        hbox.addWidget(self.textbox) 
        hbox.addWidget(self.grid_cb) 
        # hbox.setAlignment(self.grid_cb, QtCore.Qt.AlignVCenter) 

        vbox = QtGui.QVBoxLayout() 
        vbox.addWidget(self.canvas) 
        vbox.addLayout(hbox) 
        self.qwidget.setLayout(vbox) 
        self.setCentralWidget(self.qwidget) 
        self.textbox.setText('12') 
        self.on_draw()

    def on_opendialog(self): 
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', 'Users/',"All files (*);;shape file (*.shp)") 
        self.statusBar().showMessage('openned %s' % fname, 2000) 

    def on_savedialog(self): 
        path = unicode(QtGui.QFileDialog.getSaveFileName(self, 'Save file', 'Users/', "PNG (*.png)|*.png")) 
        if path: 
            self.fig.savefig(path) 
            self.statusBar().showMessage('Saved to %s' % path, 2000)

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
        QtGui.QMessageBox.about(self, "About", msg)

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
    app = QtGui.QApplication(sys.argv) 
    ex = MyWindow() 
    sys.exit(app.exec_())