# -*- coding: utf-8 -*-
import logging
import sys
import time
from typing import List
import os


if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + "" + os.environ['PATH']
from PyQt5.QtCore import Qt, QSize, QModelIndex
from PyQt5.QtGui import QIcon, QMovie, QPixmap
from PyQt5.QtWidgets import QMainWindow, QTreeWidgetItem, QTreeWidget, QApplication, QStatusBar, QLabel, \
    QAction, QVBoxLayout, QLineEdit, QSplitter, QDesktopWidget, QListWidget, QWidget, QToolBar, QMessageBox, QMenu, \
    QSplashScreen

from Article import Blog
from BlogItemCore import TreeWidgetItem, ArticleItem, ListWidgetItem, ArticleList
from LoadArticleThread import LoadArticleThread
from BlogCache import BlogCache
from Broswer import BrowserWidget
from MessageToolTip import MessageTip
from ReloadBlogThread import BlogLoadType, ReloadBlogThread
from ReloadDraftBlogThread import ReloadDraftBlogThread
from RequestCSDNService import CSDNService
from md import MDToolBarWidget
from upload2CSDNThread import UpdateThread

logging.basicConfig(level=logging.INFO,filename="./log.log",
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

class NoteMain(QMainWindow):
    def __init__(self, parent=None):
        super(NoteMain, self).__init__(parent)
        self.setWindowTitle("CSDN 同步笔记(author:rechard)")
        #os.path.dirname(os.path.realpath(__file__) 获取到当前文件的路径
        #self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon.png" )))
        self.setWindowIcon(QIcon("./images/icon.png"))
        self.blogCache=BlogCache()
        self.browser=BrowserWidget()
        self.browser.cookieAdd.connect(self.on_browser_cookieAdd)
        self.split = QSplitter()
        self.articleList = ArticleList()
        self.articleList.itemClicked.connect(self.articleItemClick)
        self.initCategory()
        self.split.addWidget(self.articleList)
        self.split.addWidget(self.browser)
        self.toolbar = MDToolBarWidget(self.browser)
        self.split.addWidget(self.toolbar)
        self.split.setSizes([0,0,900,0])
        self.setCentralWidget(self.split)
        self.showMaximized()
        #self.setGeometry(200, 200, 800, 500)
        self.cookies = {}  # 存放domain的key-value
        self.loginDone=False
        #self.loginSuccessInit()

    #点击article list里的选项
    def articleItemClick(self,clickItem:ArticleItem):
        self.showArticleInLeftFrame(clickItem.getBlog())

    def on_browser_cookieAdd(self,cookie):  # 处理cookie添加的事件
        name = cookie.name().data().decode('utf-8')     # 先获取cookie的名字，再把编码处理一下
        value = cookie.value().data().decode('utf-8')   # 先获取cookie值，再把编码处理一下
        self.cookies[name] = value
        if self.cookies.get('UserToken') and not self.loginDone:
            self.loginSuccessInit()

    def onLoadFinished(self,finished):
       if finished and self.cookies.get('UserToken') and not self.loginDone:
            self.loginSuccessInit()

    def loginSuccessInit(self):
        self.initMenu()
        self.loadAllBlogsCategories()
        self.loadAllDraftBlogCategories()
        self.statusBar= QStatusBar()
        self.setStatusBar(self.statusBar)
        self.loginDone=True
        self.browser.setHtml('welcome!')
        self.split.setSizes([250,250,900,50])

    # 显示文章到左边的显示框里
    def showArticleInLeftFrame(self, blog:Blog=None):
        if blog!=None:
            self.browser.setBlog(blog)
            self.browser.setTitle(blog.title)
            if blog.url=='draft':
                self.showHtml(blog)
            else:
                self.backend=LoadArticleThread(blog,CSDNService(self.cookies))
                self.backend.trigger.connect(self.showHtml)
                self.backend.start()

    def showHtml(self,data:Blog):
        searchTxt=self.searchTxt.text()
        html=data.content
        if len(searchTxt.strip())>0:
          html=html.replace(searchTxt,'<font style=\'background-color:yellow\'>'+searchTxt+'</font>')
        self.browser.setHtml(html)
        self.browser.setMD(data.mdText)

    # 加载loading 条
    def startloading(self):
        self.imageLabel=QLabel()
        self.movie =  QMovie("./images/loading.gif")
        self.imageLabel.setMovie(self.movie)
        self.movie.start()
        self.setCentralWidget(self.imageLabel)

    def stopLoading(self):
        self.setCentralWidget(self.browser)

    def initMenu(self):
        tb:QToolBar = self.addToolBar("toolbar")
        add = QAction(QIcon('./images/add.png'), '&新建草稿', self)
        add.setStatusTip('新建文章')
        tb.addAction(add)

        refreshAct = QAction(QIcon('./images/refresh.png'), '&同步文章', self)
        refreshAct.setShortcut('Ctrl+R')
        refreshAct.setStatusTip('从csdn同步文章...')
        tb.addAction(refreshAct)

        personal = QAction(QIcon('./images/personal.png'), '&个人信息', self)
        personal.setStatusTip('个人信息')
        tb.addAction(personal)

        help = QAction(QIcon('./images/help.png'), '&帮助', self)
        help.setStatusTip('帮助说明')
        tb.addAction(help)

        tb.actionTriggered[QAction].connect(self.windowaction)
        tb.setFloatable(False)
        logging.info("menu ini success")

    def windowaction(self, q):
        if q.text()=="&新建草稿":
            self.createDraft()
        elif q.text()=="&同步文章":
            self.reloadArticles()
        elif q.text()=="&个人信息":
            QMessageBox.about(self,"个人信息","用户名:%s"%self.cookies['UN'])
        elif q.text()=="&帮助":
            QMessageBox.about(self,"帮助说明",'''
             同步csdn文章的一个笔记工具，模仿有道笔记的界面，使用到了python，pyqt5, sqllite等
            ''')

    def createDraft(self):
       blog=Blog()
       blog.title='无标题笔记'
       blog.category='draft'
       blog.categoryUrl='none'
       blog.content=''
       blog.mdText=''
       blog.url='draft'
       c=TreeWidgetItem(blog=blog)
       c.setText(0,blog.title)
       c.setIcon(0,QIcon("./images/draft.png"))
       self.draftArticles.addChild(c)
       # todo: how to focus on new created item
       BlogCache().saveArticlies([blog])
       item=ListWidgetItem(blog=blog)
       item.setSizeHint(QSize(100,80))
       item.setIcon(QIcon("./images/draft.png"))
       item.setText(blog.title)
       self.articleList.addItem(item)

    def reloadArticles(self):
        service=CSDNService(self.cookies)
        #self.reloadPublish=ReloadBlogThread(url='https://blog.csdn.net/guo_xl',service=service,parent=self)
        self.reloadPublish=ReloadBlogThread(url='https://blog.csdn.net/'+self.cookies['UN'],service=service,parent=self)
        self.reloadPublish.start()
        self.reloadPublish.trigger.connect(self.handleReloadMessage)
        self.reloadDraft=ReloadDraftBlogThread(service=service)
        self.reloadDraft.start()
        self.reloadDraft.trigger.connect(self.handleDraftReloadMessage)
        self.statusBar.showMessage("博客加载中...")
        MessageTip("开始同步").show()

    #返回的data是个[],里面装了Blog对象
    def handleDraftReloadMessage(self,data):
        if isinstance(data,str):
            self.statusBar.showMessage(data)
            if data=="加载完毕":
                self.loadAllDraftBlogCategories()
        elif isinstance(data,List):
          self.draftArticles.takeChildren()
          for blog in data:
            c=TreeWidgetItem(blog=blog)
            c.setText(0,blog.title)
            c.setIcon(0,QIcon("./images/draft.png"))
            self.draftArticles.addChild(c)
        elif isinstance(data,Blog):
            self.blogCache.saveArticlies([data])

    def handleReloadMessage(self,data):
        if isinstance(data,str):
            self.statusBar.showMessage(data)
            if data=="加载完毕":
              self.loadAllBlogsCategories()
        elif isinstance(data,dict):
            list = data["data"]
            type = data["type"]
            if type==BlogLoadType.categories:
                self.handleDisplayCategories(list)
            elif type==BlogLoadType.subCategories:
                categoryName=data["categoryName"]
                logging.info("处理%s"%categoryName)
                #找到categoryName对应的menu item
                #坑爹，不要用publishArticlesCategory.takeChildren()移除所有的item
                count=self.publishArticlesCategory.childCount()
                i=0
                while i<count :
                    c=self.publishArticlesCategory.child(i)
                    i+=1
                    if categoryName==c.text(0):
                        self.handleDisplaySubCategories(list,c)
                        logging.info("处理完%s"%categoryName)
                        return
        elif isinstance(data,Blog):
              self.blogCache.saveArticlies([data])

    #记载草稿
    def loadAllDraftBlogCategories(self):
        data=self.blogCache.searchAllDraft()
        self.draftArticles.takeChildren()
        for blog in data:
            c=TreeWidgetItem(blog=blog)
            c.setText(0,blog.title)
            c.setIcon(0,QIcon("./images/draft.png"))
            self.draftArticles.addChild(c)
            item=ListWidgetItem(blog=blog)
            item.setSizeHint(QSize(100,80))
            item.setIcon(QIcon("./images/draft.png"))
            item.setText(blog.title)
            self.articleList.addItem(item)

    #加载blog's all categories
    def loadAllBlogsCategories(self):
        # 注意这里写法
        # 这样是错误的，为什么?
        # backend=BackendThread()
        # backend.start()
        # backend.articleCategory.connect(self.handleDisplay)
        data=self.blogCache.searchAllPublished()
        publicCategory=self.publishArticlesCategory
        publicCategory.takeChildren()
        for k,v in data.items():
            child=QTreeWidgetItem()
            child.setText(0,v.get("category")) # title
            child.setText(1,v.get("categoryUrl")) # url
            child.setText(2,'category')
            child.setIcon(0,QIcon("./images/folder_close.png"))
            publicCategory.addChild(child)
            for blog in v.get("blogs"):
                c=TreeWidgetItem(blog=blog)
                c.setText(0,blog.title)
                c.setIcon(0,QIcon("./images/blog_normal.png"))
                child.addChild(c)
                item=ListWidgetItem(blog=blog)
                item.setSizeHint(QSize(100,80))
                item.setIcon(QIcon("./images/blog_normal.png"))
                item.setText(blog.title)
                self.articleList.addItem(item)
        self.publishArticlesCategory.setDisabled(False)

    def handleDisplayCategories(self,data):
        publicCategory=self.publishArticlesCategory
        for item in data:
            if self.findCategoryByUrl(item["url"],publicCategory)==None:
                child=QTreeWidgetItem()
                child.setText(0,item["title"]) # title
                child.setText(1,item["url"]) # url
                child.setText(2,'category')
                child.setIcon(0,QIcon("./images/folder_close.png"))
                publicCategory.addChild(child)

    def findCategoryByUrl(self,url,widget):
        total=widget.childCount()
        i=0
        while i<total:
            if widget.child(i).text(1)==url:
              return  widget.child(i)
            i=i+1
        return None


    def initCategory(self):
         self.container = QWidget(self)
         layout=QVBoxLayout(self.container)
         self.tree = QTreeWidget()
         # 设置列数
         self.tree.setColumnCount(3)
         self.tree.setColumnHidden(1,True)
         self.tree.setColumnHidden(2,True)
         # 设置头的标题
         self.tree.setHeaderLabels(['title','url','category'])
         self.tree.setHeaderHidden(True)
         # 设置列宽
         self.tree.setColumnWidth(0, 320)
         self.searchTxt=QLineEdit()
         self.searchTxt.setPlaceholderText("关键字查询")
         self.searchTxt.textChanged.connect(self.search)
         layout.addWidget(self.searchTxt)
         layout.addWidget(self.tree)
         self.initPublishArticle()
         self.initDraftArticle()
         self.tree.itemClicked.connect(self.onClicked)
         self.tree.itemCollapsed.connect(self.onCollapsed)
         self.tree.itemExpanded.connect(self.onExpended)
         self.split.addWidget(self.container)

         self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
         self.tree.customContextMenuRequested.connect(self.onCustomContextMenu)

    def onCustomContextMenu(self,point):
        i=self.tree.indexAt(point)
        menu = QMenu()
        upload = QAction("上传到CSDN",self)
        menu.addAction(upload)
        t = time.time()
        k =menu.exec_(self.tree.mapToGlobal(point))
        #If the menu hasn't been open for more than 0.6s,
        #assume user did not have time to properly react to it opening
        if time.time()-t<0.6:
           return
        if k == upload:
            msg =QMessageBox()
            msg.setText("同步到csdn")
            msg.setStandardButtons(QMessageBox.Yes| QMessageBox.Cancel)
            r=msg.exec_()
            if r== QMessageBox.Yes:
                MessageTip("开始同步到csdn").show()
                item = self.tree.currentItem()
                ut=UpdateThread(item.getBlog(),CSDNService(self.cookies))
                ut.update_proess_signal.connect(self.onUploaded)
                ut.start()

    def onUploaded(self,code:int):
        if(code==200):
            win = MessageTip("发布到csdn成功")
            win.show()

    def onCollapsed(self,index:QModelIndex):
        index.setIcon(0,QIcon("./images/folder_open.png")) if index.isExpanded() else index.setIcon(0,QIcon("./images/folder_close.png"))

    def onExpended(self,index:QModelIndex):
        index.setIcon(0,QIcon("./images/folder_open.png")) if index.isExpanded() else index.setIcon(0,QIcon("./images/folder_close.png"))

    def search(self,data):
        result=self.blogCache.fuzzySearch(data)
        #public:QTreeWidgetItem=self.publishArticlesCategory # public
        # total=public.childCount()
        # i=0
        # while i<total:
        #   c=public.child(i)
        #   ctotal=c.childCount()
        #   j=0
        #   while j<ctotal:
        #       if len(data)>0 and (not result or c.child(j).text(0) not in result):
        #           c.child(j).setHidden(True)
        #       else:
        #           c.child(j).setHidden(False)
        #       j=j+1
        #   i=i+1
        i=0
        articleList:QListWidget=self.articleList
        total=articleList.count()
        while i<total:
            if len(data)>0 and (not result or articleList.item(i).text() not in result):
                articleList.item(i).setHidden(True)
            else:
                articleList.item(i).setHidden(False)
            i=i+1

    def onClicked(self):
        try:
         item = self.tree.currentItem()
         if item!=None:
            #None是root节点
            if isinstance(item,TreeWidgetItem):
                self.showArticleInLeftFrame(item.getBlog())
        except Exception as ex:
            logging.exception(ex)


    #加载category下的子category
    # def loadSubCategories(self, item:QTreeWidgetItem):
    #     list=item.takeChildren()
    #     list.clear()
    #     #改成异步加载
    #     logging.info("loading sub category start")
    #     self.backend=BackendThread(url=item.text(1),type=BlogLoadType.subCategories)
    #     self.backend.trigger.connect(lambda data:self.handleDisplaySubCategories(data, item))
    #     self.backend.start()

    def handleDisplaySubCategories(self, articles, item):
        logging.info("loading %s subcategory"%item.text(0))
        for i in articles:
          if self.findCategoryByUrl(i["url"],item)==None:
            c=QTreeWidgetItem()
            c.setText(0,i['title']) # title
            c.setText(1,i['url']) # url
            c.setText(2,'article')
            c.setText(3,i['updateTime'])
            item.addChild(c)


    def initDraftArticle(self):
        self.draftArticles = QTreeWidgetItem(self.tree)
        self.draftArticles.setText(0, '草稿箱')
        self.draftArticles.setIcon(0, QIcon("./images/folder_close.png"))
        self.tree.addTopLevelItem(self.draftArticles)


    def initPublishArticle(self):
        self.publishArticlesCategory = QTreeWidgetItem(self.tree)
        self.publishArticlesCategory.setText(0, '公开文章')
        self.publishArticlesCategory.setIcon(0, QIcon("./images/folder_close.png"))
        self.publishArticlesCategory.setDisabled(True)
        # self.label =  QLabel('', self)
        # self.movie =  QMovie("./images/loading.gif")
        # self.label.setMovie(self.movie)
        # self.movie.start()


        ### 设置节点的背景颜色
        #brush_red = QBrush(Qt.red)
        #self.publishArticles.setBackground(0, brush_red)
        #brush_green = QBrush(Qt.green)
        #self.publishArticlesCategories.setBackground(1, brush_green)
        self.tree.addTopLevelItem(self.publishArticlesCategory)
        #异步加载文章
        #self.statusBar.showMessage("博客加载中...")

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    def my_exception_hook(exctype, value, traceback):
        # Print the error and traceback
        print(exctype, value, traceback)
        # Call the normal Exception hook after
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    app = QApplication(sys.argv)
    # 创建启动界面，支持png透明图片
    splash = QSplashScreen(QPixmap('splash.png'))
    splash.show()
    # 可以显示启动信息
    splash.showMessage('正在加载……')
    # 关闭启动画面
    demo = NoteMain()
    #demo.center()
    demo.showMaximized()
    demo.show()
    splash.close()
    try:
        sys.exit(app.exec_())
    except:
     print("Exiting")
