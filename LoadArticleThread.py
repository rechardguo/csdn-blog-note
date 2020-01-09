# coding=utf-8
import logging

from PyQt5.QtCore import QThread, pyqtSignal

from Article import Blog
from BlogCache import BlogCache
from CSDNService import IService


class LoadArticleThread(QThread):
    trigger = pyqtSignal(Blog)
    def __init__(self, blog:Blog,service:IService,parent=None):
        super(LoadArticleThread, self).__init__(parent)
        self.blog=blog
        self.service=service
        self.cache=BlogCache()

    # 处理要做的业务逻辑
    def run(self):
        try:
            logging.info("begin to load blog %s"%self.blog.title)
            result=self.cache.searchArticle(url=self.blog.url)
            if len(result)==0:
              _blog=self.service.loadArticle(self.blog)
              self.cache.saveArticlies([_blog])
            else:
                _blog=result[0]
            self.trigger.emit(_blog)
        except Exception as ex:
            logging.error("error happen when load article")
            logging.exception(ex)