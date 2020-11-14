from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
import sys
import shutil
import re
import os
from subprocess import  Popen,PIPE
import function as fc
import threading
import gol

gol._init()

gol.set_value('WORKPATH',None)
MATSTARTCOL=3
EXT_LIST =['.step','.sldprt','.stp','.sldasm']#
PARTEXT =['.step','.sldprt']
WORKDIR = os.getcwd()
MATDIROOT = os.path.expanduser('~') + "\\Documents\\KeyShot 9\\Materials"

class ComboBox(QComboBox):
    comboboxchange = pyqtSignal(int, int, str)
    def __init__(self,parent):
        super(ComboBox, self).__init__(parent=parent)

class MainWindow(QMainWindow):
    #主窗口类

    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.startwpos=QPoint(0,0)
        self.mdict = None
        self.InitFlag=True

        wid = QWidget(self)
        layout = QGridLayout(wid)
        self.setCentralWidget(wid)
        wid.setLayout(layout)

        closeButton = QPushButton(wid)
        closeButton.setObjectName("closebutton")
        closeButton.setMaximumSize(20, 20)
        closeButton.setMinimumSize(20, 20)

        maxButton = QPushButton(wid)
        maxButton.setObjectName("maxbutton")
        maxButton.setMaximumSize(20, 20)
        maxButton.setMinimumSize(20, 20)

        minButton = QPushButton(wid)
        minButton.setObjectName("minbutton")
        minButton.setMaximumSize(20, 20)
        minButton.setMinimumSize(20, 20)

        closeButton.clicked.connect(self.close)
        minButton.clicked.connect(self.showMinimized)
        maxButton.clicked.connect(self.slotShowMax)

        base_button_layout = QHBoxLayout(wid)
        base_button_layout.addStretch(0)
        base_button_layout.addWidget(minButton)
        base_button_layout.addWidget(maxButton)
        base_button_layout.addWidget(closeButton)
        ##########################################################
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(1200,800)
        ################################################
        layout_workDir = QHBoxLayout(wid)
        self.Label_workDir = QLabel(wid)#标签
        self.Button_workDir = QPushButton(wid) #打开工作目录按钮
        self.LineEdit_workDir = QLineEdit(wid)#当前工作目录显示
        self.Label_workDir.setText("工作目录")
        self.Button_workDir.setText("打开")
        self.LineEdit_workDir.setText(WORKDIR)
        self.LineEdit_workDir.setReadOnly(True)
        layout_workDir.addWidget(self.Label_workDir)
        layout_workDir.addWidget(self.LineEdit_workDir)
        layout_workDir.addWidget(self.Button_workDir)
        self.Button_workDir.clicked.connect(self.setWorkDir)
        self.LineEdit_workDir.textChanged.connect(self.tableInit)

        layout_main = QVBoxLayout(wid)
        layout_main.addLayout(base_button_layout)
        layout_main.addLayout(layout_workDir)
        layout.addLayout(layout_main,0,0,1,3)
        #########################################################
        self.Table_widget = QTableWidget(wid)
        self.Table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.Table_widget,1,0,5,3)
        self.Table_widget.setColumnCount(4)
        self.Table_widget.setHorizontalHeaderLabels(["序号","PATH","EXTENSION","MATERIALS"])
        self.Table_widget.verticalHeader().setVisible(False)
        # self.Table_widget.resizeColumnsToContents()
        # self.Table_widget.resizeRowsToContents()
        self.flushtable()
        #self.addRowContent(["1","./asd/dd"])
        ##############################################################
        self.reset_button = QPushButton(wid)
        self.reset_button.setText("重置")
        self.writeConfig_button = QPushButton(wid)
        self.writeConfig_button.setText("写入")
        self.reng = QPushButton(wid)
        self.reng.setText("渲染")
        self.clPic_button = QPushButton(wid)
        self.clPic_button.setText("清空")
        layout_bottom = QHBoxLayout(wid)
        layout_bottom.addWidget(self.clPic_button)
        layout_bottom.addWidget(self.reset_button)
        layout_bottom.addWidget(self.writeConfig_button)
        layout_bottom.addWidget(self.reng)
        layout.addLayout(layout_bottom,6,1,1,2)

        self.reng.clicked.connect(self.slot_rengbutton)
        self.writeConfig_button.clicked.connect(self.slot_writeconfig)
        self.reset_button.clicked.connect(self.slot_reset)
        self.clPic_button.clicked.connect(self.slot_clPic)

    def addRowContent(self,content):
        rowcount=self.Table_widget.rowCount()
        self.Table_widget.insertRow(rowcount)
        content.insert(0, str(rowcount))
        for i in range(len(content)):
            self.Table_widget.setItem(rowcount, i, QTableWidgetItem(content[i]))
            self.Table_widget.resizeColumnsToContents()
            self.Table_widget.resizeRowsToContents()
        cbox = ComboBox(parent=self.Table_widget)
        itemdist = fc.retmatdiv(MATDIROOT)
        for k,v in itemdist.items():
            if v=="dir":
                k = k+"\tD"
            elif v=="mtl":
                k = k+"\tM"
            cbox.addItem(k)
            self.flushtable()
        ####################################################
        indextext=''
        if os.path.exists(gol.get_value('WORKPATH')+"/"+"config"):
            configpath = gol.get_value('WORKPATH')+"\\config"
            objson = fc.loadJson(configpath)
            try:
                context = objson[content[1]]
            except KeyError:
                context=''
            if not context=='':
                if  self.mdict==None:
                    self.mdict = self.getAllMaterials()
                indextext=str(self.mdict[context]).split('\\')[0]
                #print(indextext)
            else:
                indextext=''
        else:
            if os.path.exists(gol.get_value('WORKPATH')+"/"+"config"):
                pass
            else:
                if not self.mdict == None:
                    self.mdict.clear()
                self.mdict=None
        if indextext=='':
            cbox.setCurrentIndex(-1)
        else:
            cbox.setCurrentText(indextext+'\t'+'D')
        ########################################################
        self.Table_widget.setCellWidget(rowcount,MATSTARTCOL,cbox)
        self.Table_widget.viewport().update()
        def emit_Signal_comboboxchange(msg):
            cbox.comboboxchange.emit(rowcount,MATSTARTCOL,MATDIROOT+"\\"+msg)
        cbox.currentTextChanged.connect(self.flushtable)
        cbox.comboboxchange.connect(self.slotCombobox)
        cbox.currentTextChanged.connect(emit_Signal_comboboxchange)
        QApplication.processEvents()
        if not indextext=='':
            cbox.currentTextChanged.emit(cbox.currentText())

    def addColComBox(self,row,col,path):
        if not self.Table_widget.columnCount()>col:
            self.Table_widget.insertColumn(col)
        combox = ComboBox(self.Table_widget)
        itemdist = fc.retmatdiv(path)
        for k,v in itemdist.items():
            if v=="dir":
                k = k+"\tD"
            elif v=="mtl":
                k = k+"\tM"
            combox.addItem(k)

        indextext = ''
        if os.path.exists(gol.get_value('WORKPATH') + "\\" + "config") and self.InitFlag:
            #self.InitFlag=False
            configpath = gol.get_value('WORKPATH') + "\\config"
            objson = fc.loadJson(configpath)
            context = objson[self.Table_widget.item(row,1).text()]
            if not context == '':
                if not self.mdict == None:
                    self.mdict = self.getAllMaterials()
                l  = self.mdict[context]
                indextext = l.split('\\')[col-3]
                #print(indextext)
            else:
                indextext = ''
        else:
            if os.path.exists(gol.get_value('WORKPATH') + "/" + "config"):
                pass
            else:
                if not self.mdict == None:
                    self.mdict.clear()
                self.mdict = None
        if indextext=='':
            combox.setCurrentIndex(-1)
        elif re.search('.*\.mtl$',indextext)==None:
            combox.setCurrentText(indextext+"\tD")
        else:
            combox.setCurrentText(context + "\tM")

        self.Table_widget.setCellWidget(row,col,combox)
        self.Table_widget.viewport().update()
        def emit_Signal_comboboxchange(msg):
            combox.comboboxchange.emit(row,col,path+"\\"+msg)
        combox.currentTextChanged.connect(self.flushtable)
        combox.comboboxchange.connect(self.slotCombobox)
        combox.currentTextChanged.connect(emit_Signal_comboboxchange)
        if re.search('.*\.mtl$',indextext)==None:
            #self.InitFlag=True
            combox.currentTextChanged.emit(combox.currentText())

    def flushtable(self):
        self.Table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.Table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def slot_clPic(self):
        if os.path.exists(gol.get_value('WORKPATH')+"\\"+"screen"):
            shutil.rmtree(gol.get_value('WORKPATH')+"\\"+"screen")
        if os.path.exists(gol.get_value('WORKPATH')+"\\"+"config"):
            os.remove(gol.get_value('WORKPATH')+"\\"+"config")

    def slotCombobox(self,row,col,msg):
        if msg[-1:]=='D':
            colun = self.Table_widget.columnCount()
            if col + 1 < colun:
                for i in range(col + 1, colun):
                    self.Table_widget.removeCellWidget(row, i)
            self.addColComBox(row,col+1,msg[:-2])
        elif msg[-1:]=='M':
            colun = self.Table_widget.columnCount()
            if col + 1 < colun:
                for i in range(col + 1, colun):
                    self.Table_widget.removeCellWidget(row, i)

    def slot_reset(self):
        print("重置")
        self.reset_button.setEnabled(False)
        self.tableInit()
        self.reset_button.setEnabled(True)


    def slot_rengbutton(self):
        self.reng.setEnabled(False)
        def thr():
            shutil.copyfile("./startkeyshot.py", gol.get_value('WORKPATH') + "\\startkeyshot.py")
            print("开始渲染", gol.get_value('WORKPATH'))
            process = Popen(['keyshot', '-script', gol.get_value('WORKPATH') + "\\startkeyshot.py",'>','log.txt'], shell=True,
                            cwd=gol.get_value('WORKPATH'), encoding="utf-8")
            path = gol.get_value('WORKPATH')
            process.wait()
            os.remove(path+"\\startkeyshot.py")
            self.reng.setEnabled(True)

        p = threading.Thread(target=thr)
        p.start()

        pass

    def slot_writeconfig(self):
        print("写入配置。。。")
        rengdict = {}
        rownum = self.Table_widget.rowCount()
        colnum = self.Table_widget.columnCount()
        for row in range(rownum):
            #print(self.Table_widget.item(row,2).text())
            if self.Table_widget.item(row,2).text() in EXT_LIST:
                for col in range(int(MATSTARTCOL),colnum):
                    cel = self.Table_widget.cellWidget(row,col).currentText()
                    if cel =='':
                        modelpath = self.Table_widget.item(row, 1).text()
                        rengdict[modelpath] = ''
                        break
                    elif cel[-1:] == "M":
                        #print(cel[:-2])
                        modelpath = self.Table_widget.item(row,1).text()
                        rengdict[modelpath] = cel[:-2]
                        break
                    else:
                        pass
            else:
                continue
        #print(rengdict)
        jsonstr = json.dumps(rengdict)
        with open(self.LineEdit_workDir.text()+"\\"+"config",'w',encoding="utf-8") as f:
            f.write(jsonstr)
        print("写入成功")

    def tableInit(self):
        self.InitFlag = True
        self.Table_widget.setRowCount(0)
        dir = self.LineEdit_workDir.text()
        gol.set_value('WORKPATH',dir)

        for f in fc.filterFileList(fc.getModelFile(dir),EXT_LIST):
            QApplication.processEvents()
            ext = os.path.splitext(f)[1].lower()
            self.addRowContent([f,ext])
        self.InitFlag = False

    def getAllMaterials(self):
        matdict = {}
        flist = fc.filterFileList(fc.getModelFile(MATDIROOT),['.mtl'])
        for f in flist:
            m = fc.getMaterialName(f)
            if not m==False:
                matdict[m[0]]=os.path.relpath(m[1],MATDIROOT)
        #print(matdict)
        return matdict

    def setWorkDir(self):
        work_dir = QFileDialog.getExistingDirectory(self,"TDYWA——选择工作目录",".")
        self.LineEdit_workDir.setText(work_dir)
        pass

    def slotShowMax(self):
        if self.isFullScreen():
            self.resize(1200,800)
            self.move(int(QApplication.desktop().width()/2-self.width()/2),\
                      int(QApplication.desktop().height()/2-self.height()/2))
        else:
            self.showFullScreen()


    def mousePressEvent(self, event):
        # print(event.pos())
        # print(event.globalPos())
        self.startwpos = event.pos()
        pass

    def mouseMoveEvent(self, event):
        self.move(QPoint(event.globalPos())-self.startwpos)
        pass

    def mouseReleaseEvent(self, event):
        pass

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    app.setStyleSheet('''MainWindow{border-image:url(./image/background.png);}
                            QPushButton{background-color:rgba(255,255,255,200);
                                        width:80px;
                                        height:30px;
                                        border-radius:5px;}
                            QPushButton:hover{background-color:rgba(125,125,125,255);
                                        width:80px;
                                        height:30px;
                                        border-radius:5px;}
                            #closebutton{width:10px;height:10px;border-radius:10px;background-color:rgb(188,0,0);}
                            #closebutton:hover{width:10px;height:10px;border-radius:10px;background-color:rgb(255,0,0);}
                            #maxbutton{width:10px;height:10px;border-radius:10px;background-color:rgb(0,188,0);}
                            #maxbutton:hover{width:10px;height:10px;border-radius:10px;background-color:rgb(0,255,0);}
                            #minbutton{width:10px;height:10px;border-radius:10px;background-color:rgb(0,0,188);}
                            #minbutton:hover{width:10px;height:10px;border-radius:10px;background-color:rgb(0,0,255);}
                            QTableWidget,QLineEdit,QComboBox{background-color:rgba(255,255,255,150);}''')
    win.show()
    win.tableInit()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()