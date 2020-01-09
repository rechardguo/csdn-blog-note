# coding=utf-8
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QTreeWidgetItem

from Article import Blog

class ArticleItem():
    def __init__(self,blog:Blog, *__args):
        self.__blog=blog

    def getBlog(self):
        return self.__blog

class ListWidgetItem(QListWidgetItem,ArticleItem):
    def __init__(self,blog:Blog, *__args):
        QListWidgetItem.__init__(self,blog=Blog,*__args)
        ArticleItem.__init__(self,blog=blog,*__args)


class TreeWidgetItem(QTreeWidgetItem,ArticleItem):
    def __init__(self,blog:Blog, *__args):
     QTreeWidgetItem.__init__(self,blog=Blog,*__args)
     ArticleItem.__init__(self,blog=blog,*__args)


class ArticleList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def addItem(self, item:ListWidgetItem):
        if len(self.findItems(item.getBlog().title, Qt.MatchContains))==0:
            super().addItem(item)
