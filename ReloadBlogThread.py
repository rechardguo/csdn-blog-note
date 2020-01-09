# coding=utf-8
import logging
from enum import unique, Enum

from PyQt5.QtCore import QThread, pyqtSignal

from Article import Blog
from BlogCache import BlogCache
from CSDNService import IService

'''    
 后台线程加载文章
'''

@unique
class BlogLoadType(Enum):
    categories = 0
    subCategories = 1
    article = 2

class ReloadBlogThread(QThread):
    # 通过类成员对象定义信号对象
    trigger = pyqtSignal(object)
    def __init__(self,url,service:IService=None,parent=None):
        super(ReloadBlogThread,self).__init__(parent)
        self.url=url
        self.service=service
        self.cache = BlogCache()
    # 处理要做的业务逻辑
    def run(self):
        self.trigger.emit(str("开始加载URL : %s"%self.url))
        data=self.service.loadCategories(self.url)
        self.trigger.emit({"data":data,"type":BlogLoadType.categories})
        self.trigger.emit(str("加载URL : %s 完毕"%self.url))
        allsubCategories=[]
        for item in data:
            categoryName=item['title']
            categoryUrl=item['url']
            self.trigger.emit(str("开始加载Category : %s ,URL:%s"%(categoryName,categoryUrl)))
            logging.info("===========start to load url:%s==========="%categoryUrl)
            subCategories=self.service.loadCategoryArticles(categoryUrl)
            logging.info("===========end to load url:%s==========="%categoryUrl)
            self.trigger.emit({"data":subCategories,"type":BlogLoadType.subCategories,"categoryName":categoryName})
            self.trigger.emit(str("加载Category : %s ,URL:%s 完毕"%(categoryName,categoryUrl)))
            for c in subCategories:
                c["category"]=categoryName
                c["categoryUrl"]=categoryUrl
            allsubCategories=allsubCategories+subCategories

        for i in allsubCategories:
            blog=Blog()
            blog.categoryUrl=i['categoryUrl'] 
            blog.category=i['category']
            blog.title=i['title']
            blog.url=i['url']
            blog.lastUpdateTime=i['updateTime']
            result=self.cache.searchArticle(**{'lastUpdateTime':blog.lastUpdateTime,'url': blog.url})
            if len(result)==0:
                 self.trigger.emit(str("开始加载文章 : %s ,URL:%s"%(blog.title,blog.url)))
                 self.service.loadArticle(blog)
                 self.trigger.emit(blog)
                 self.trigger.emit(str("加载文章 : %s ,URL:%s 完毕"%(blog.title,blog.url)))
            self.trigger.emit("加载完毕")