# -*- coding: utf-8 -*-

'''
    【简介】
	PyQT5中气泡提示
   
'''

import sys

from PyQt5.QtCore import QPropertyAnimation, QPoint, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QLabel


class MessageTip(QWidget):
	def __init__(self,msg:str):
		super().__init__()
		self.initUI(msg)

	def initUI(self,msg:str):
		self.setGeometry(300, 300, 350, 120)
		self.setStyleSheet("background-color: blue")
		self.setWindowFlags(Qt.FramelessWindowHint)
		layout = QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		label=QLabel()
		label.setText(msg)
		layout.addWidget(label)
		self.setLayout(layout)
		self.desktop=QDesktopWidget()
		self.move((self.desktop.availableGeometry().width()-self.width()),self.desktop.availableGeometry().height()) #初始化位置到右下角
		self.showAnimation()

	def showAnimation(self):
		#显示弹出框动画
		self.animation=QPropertyAnimation(self,b'pos')
		self.animation.setDuration(500)
		self.animation.setStartValue(QPoint(self.x(),self.y()))
		self.animation.setEndValue(QPoint((self.desktop.availableGeometry().width()-self.width()),(self.desktop.availableGeometry().height()-self.height())))
		self.animation.start()
		#设置弹出框1秒弹出，然后渐隐
		self.remainTimer=QTimer()
		self.remainTimer.timeout.connect(self.closeAnimation)
		self.remainTimer.start(1000) #定时器3秒

	def closeAnimation(self):
		#清除Timer和信号槽
		self.remainTimer.stop()
		#self.disconnect(self.remainTimer,SLOT("closeAnimation()"))
		self.remainTimer.timeout.disconnect(self.closeAnimation)
		self.remainTimer.deleteLater()
		self.remainTimer=None
		#弹出框渐隐
		self.animation =QPropertyAnimation(self,b"windowOpacity")
		self.animation.setDuration(1000)
		self.animation.setStartValue(1)
		self.animation.setEndValue(0)
		self.animation.start()
		#动画完成后清理
		#self.connect(self.animation,SIGNAL("finished()"),SLOT("clearAll()"))
		self.animation.finished.connect(self.clearAll)

	def clearAll(self):
		self.close()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	win = MessageTip("hahaha")
	win.show()
	sys.exit(app.exec_())
