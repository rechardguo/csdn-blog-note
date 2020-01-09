# coding=utf-8
import markdown2
from PyQt5.QtCore import QUrl, pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QLineEdit, QShortcut

from Article import Blog
from BlogCache import BlogCache


class BrowserWidget(QWidget):
    cookieAdd=pyqtSignal(QNetworkCookie)
    _blog=None

    def __init__(self, parent=None):
        super().__init__(parent)
        layout=QVBoxLayout()
        self.setLayout(layout)
        self.profile = QWebEngineProfile()
        self.store=self.profile.cookieStore()
        self.brower=QWebEngineView()
        self.profile.cookieStore().cookieAdded.connect(self.onCookieAdd)
        page = QWebEnginePage(self.profile, self.brower)
        page.setUrl(QUrl("https://passport.csdn.net/login?code=public"))
        self.brower.setPage(page)
        self.title=QLabel()
        self.edit=QTextEdit()
        #self.edit=QCodeEditor()
        layout.addWidget(self.title)
        layout.addWidget(self.brower)
        layout.addWidget(self.edit)
        layout.setStretchFactor(self.title,1)
        layout.setStretchFactor(self.brower,10)
        layout.setStretchFactor(self.edit,10)
        self.title.setHidden(True)
        self.edit.setHidden(True)

        #当edit的内容改动的时候，broswer的内容要同步进行刷新
        self.edit.textChanged.connect(self.refreshBrowser)

        #快捷查找
        self.contentSearch = QLineEdit(returnPressed = lambda: self.brower.findText(self.contentSearch.text()))
        self.contentSearch.setWindowTitle("搜索")
        self.contentSearch.hide()
        self.showSearch = QShortcut("Ctrl+F", self, activated = lambda: (self.contentSearch.show() , self.contentSearch.setFocus()))

    def setBlog(self,blog:Blog):
        self._blog=blog

    def saveBlog(self):
        self.brower.page().toHtml(lambda c:self._setBlogContent(c))
        self._blog.mdText=self.edit.toPlainText()
        extras = ['code-friendly', 'fenced-code-blocks', 'footnotes','tables','code-color','pyshell','nofollow','cuddled-lists','header ids','nofollow']
        self._blog.content=markdown2.markdown(self._blog.mdText, extras=extras)
        BlogCache().saveArticlies([self._blog])

    def _setBlogContent(self,c):
        self._blog.content=c

    def refreshBrowser(self):
        #重新刷新内容
       #md=Markdown()
        extras = ['code-friendly', 'fenced-code-blocks', 'footnotes','tables','code-color','pyshell','nofollow','cuddled-lists','header ids','nofollow']
        mdContent=self.edit.toPlainText()

        html = """
        <html>
        <head>
        <meta content="text/html charset=utf-8" http-equiv="content-type" />
        <style>
            %s
        </style>
        </head>
        <body class="markdown-body">
            %s
        </body>
        </html>
        """
        css=open("./css/md.css",encoding="UTF-8").read()
        ret = markdown2.markdown(mdContent, extras=extras)
        self.brower.setHtml(html%(css,ret))
        #todo:需要将brower的内容移动到对应的地方
        # cursor:QTextCursor=self.edit.textCursor()
        # line=cursor.blockNumber()
        # lineBlock:QTextBlock=self.edit.document().findBlockByNumber(line)
        # #光标所在行的文字
        # lineText=lineBlock.text()
        # browserCursor:QCursor=self.brower.cursor()
        # self.brower.findText(md.convert(lineText),resultCallback=lambda b:print(b))

    def showBlog(self,blog:Blog):
        self.brower.setHtml(blog.content)

    def setHtml(self,html):
        self.brower.setHtml(html)

    def setMD(self,md):
        self.edit.setText(md)

    def showEdit(self):
        self.edit.setHidden(False)

    def insertEdit(self,c):
        self.edit.insertPlainText(c)

    def hideEdit(self):
        self.edit.setHidden(True)

    def setTitle(self,title):
        self.title.setHidden(False)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setText(title)
        self.title.setFont(QFont("Timers", 20, QFont.Bold))

    def onCookieAdd(self,cookie:QNetworkCookie):
        self.cookieAdd.emit(cookie)