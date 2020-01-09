# coding=utf-8

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QTextCursor
from PyQt5.QtWidgets import QPushButton, QWidget, QVBoxLayout

from Broswer import BrowserWidget
from MessageToolTip import MessageTip


class MDToolBarWidget(QWidget):
    def __init__(self,browser:BrowserWidget):
        super().__init__()
        self.toolbarLayout = QVBoxLayout(self)
        self.toolbarLayout.setContentsMargins(0, 0, 0, 0)
        self.toolbarLayout.setAlignment(Qt.AlignTop)
        self.browser=browser
        self.editBtn = EditBtn(self)
        self.editBtn.minimumSizeHint()
        self.editBtn.modechange.connect(self.editArticle)
        self.toolbarLayout.addWidget(self.editBtn)

        # self.ts = QPushButton("Timestamp")
        # self.ts.clicked.connect(self.Timestamp)
        # self.toolbarLayout.addWidget(self.ts)
        # self.ts.hide()

        self.save = QPushButton("Save")
        self.save.clicked.connect(self.saveBlog)
        self.toolbarLayout.addWidget(self.save)
        self.save.hide()

    def saveBlog(self):
        self.browser.saveBlog()
        MessageTip("保存文章成功").show()

    def Timestamp(self,d):
        #t =datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        #self.browser.insertEdit(t)
        self.browser.edit.verticalScrollBar().valueChanged.connect(self.scrollEvent)
        #self.browser.edit.scrollToAnchor("spring")

    def scrollEvent(self,obj):
        c:QTextCursor=self.browser.edit.textCursor();

        self.browser.edit.verticalScrollBar()
        print("blockNumber:%s"%self.browser.edit.textCursor().blockNumber())
        print("columnNumber:%s"%self.browser.edit.textCursor().columnNumber())
        print(self.browser.edit.textCursor().block().text())
        print(obj)

    #编辑文章
    def editArticle(self,mode):
        if mode==EditBtn.mode_edit:
            self.browser.showEdit()
            self.save.show()
            #self.ts.show()

        elif mode==EditBtn.mode_view:
            self.browser.hideEdit()
            self.save.hide()
            #self.ts.hide()

class EditBtn(QPushButton):

    mode_edit=0
    mode_view=1

    # 发出哪种状态
    modechange=pyqtSignal(int)

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setIcon(QIcon("./images/edit.png"))
        self.minimumSize()
        self.mode=self.mode_view
        self.clicked.connect(self.onclick)

    def onclick(self):
        if self.mode==self.mode_view:
         self.setIcon(QIcon("./images/view.png"))
         self.mode=self.mode_edit
        else:
         self.setIcon(QIcon("./images/edit.png"))
         self.mode=self.mode_view
        self.modechange.emit(self.mode)