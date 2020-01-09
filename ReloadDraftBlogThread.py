# coding=utf-8
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup

from Article import Blog
from BlogCache import BlogCache
from CSDNService import IService

'''
    【简介】
	后台加载文章的线程  
  
'''

class ReloadDraftBlogThread(QThread):
    # 通过类成员对象定义信号对象
    trigger = pyqtSignal(object)
    def __init__(self,service:IService=None,parent=None):
        super(ReloadDraftBlogThread,self).__init__(parent)
        self.url='https://mp.csdn.net/postlist/list/draft'
        self.service=service
        self.cache = BlogCache()

    # 处理要做的业务逻辑
    # while的逻辑是由于草稿有分页，要判断是否是最后一页
    def run(self):
       result=[]
       url=self.url
       while url!=None:
           page=self.service.load(url)
           bs = BeautifulSoup(page,features="lxml")
           list=bs.select('div.article-list-item')
           for l in list:
                blog=Blog()
                blog.category='draft'
                blog.categoryUrl='none'
                blog.title=l.select_one("a").get_text().strip()
                blog.url=l.select_one("a").get("href").strip()
                blog.lastUpdateTime=l.select_one("div.item-info-left").select("span")[1].get_text().strip()
                result.append(blog)
           pageLink=bs.select("a.page-link")
           lastLink=pageLink[len(pageLink)-1]
           if lastLink.get("rel")!=None:
               url=lastLink.get("href")
           else:
               url=None
       self.trigger.emit(result)

       # 文章进行加载
       for blog in result:
           result=self.cache.searchArticle(**{'lastUpdateTime':blog.lastUpdateTime,'url': blog.url})
           if len(result)==0:
               self.trigger.emit(str("开始加载草稿文章 : %s "%(blog.title)))
               self.service.loadArticle(blog)
               self.trigger.emit(blog)
               self.trigger.emit(str("加载草稿文章 : %s 完毕"%(blog.title)))
           self.trigger.emit("加载完毕")


