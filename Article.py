# coding=utf-8
class Blog():
    #__slots__ = ("cate","categoryUrl","title","lastUpdateTime","mdText");
    def __init__(self) -> None:
        super().__init__()
        self._lastUpdateTime=None
        self._mdText=None

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self,content):
        self._content=content

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self,category):
        self._category=category

    @property
    def categoryUrl(self):
        return self._categoryUrl

    @categoryUrl.setter
    def categoryUrl(self,categoryUrl):
        self._categoryUrl=categoryUrl

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self,url):
        self._url=url

    @property
    def title(self):
      return self._title

    @title.setter
    def title(self,title):
      self._title=title

    @property
    def lastUpdateTime(self):
        return self._lastUpdateTime

    @lastUpdateTime.setter
    def lastUpdateTime(self,lastUpdateTime):
        self._lastUpdateTime=lastUpdateTime

    @property
    def mdText(self):
        return self._mdText

    @mdText.setter
    def mdText(self,mdText):
        self._mdText=mdText

    def __str__(self) -> str:
        return self.mdText


