# coding=utf-8
import json
import logging

import requests
from bs4 import BeautifulSoup

from Article import Blog
from CSDNService import IService


class CSDNService(IService):


    def __init__(self,cookies:dict) -> None:
        post_header = {
            "accept": "text/html,application/xhtml+xml,application/xmlq=0.9,image/webp,image/apng,*/*q=0.8,application/signed-exchangev=b3q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zhq=0.9,enq=0.8",
            #"cookie": "uuid_tt_dd=10_18821971020-1569334939868-533618 dc_session_id=10_1569334939868.103325 UN=guo_xl Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_18821971020-1569334939868-533618!5744*1*guo_xl!1788*1*PC_VC smidV2=2019092622122737b855cd059f0b72550ccadc1b1434ec00800fed10b0c5a10 __gads=Test UserName=guo_xl UserInfo=c034cdcd8bbc4d12816a9f2dcbf10ca2 UserToken=c034cdcd8bbc4d12816a9f2dcbf10ca2 UserNick=xiao_long_guo AU=D81 BT=1577347324550 p_uid=U000000 Hm_lvt_e5ef47b9f471504959267fd614d579cd=1577349355 Hm_ct_e5ef47b9f471504959267fd614d579cd=5744*1*guo_xl!6525*1*10_18821971020-1569334939868-533618 __yadk_uid=8bxS6jAfNBt8X3djdmXpWNaEBN5Uq5oI Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1577342435,1577346722,1577347623,1577605477 announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Fblog.csdn.net%252Fblogdevteam%252Farticle%252Fdetails%252F103603408%2522%252C%2522announcementCount%2522%253A0%252C%2522announcementExpire%2522%253A3600000%257D TY_SESSION_ID=c50881b3-fc2b-4430-93e1-aabf101f8fa6 dc_tos=q39m27 Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1577607919",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0 Win64 x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
        cookieval=""
        for key, value in cookies.items():
            cookieval=cookieval+""+key+"="+value
        post_header["cookie"]=cookieval
        self.post_header=post_header


    def updateCSDNDraftArticle(self,blog:Blog):
        data=self._toData(blog)
        r=requests.post('https://mp.csdn.net/mdeditor/saveArticle',data=data,headers=self.post_header)
        return r.status_code

    def _toData(self,blog:Blog):
        data={}
        data["title"]=blog.title
        data["markdowncontent"]=blog.mdText
        if blog.url!='draft':
            data["status"]=0   # 正式的文章的时候为0，草稿:2
            data["id"]=blog.url[blog.url.rindex('/')+1:]
            data["type"]=0
        else:
            data["status"]=2
            data["type"]='original' # original:原创   草稿:0
            data["categories"]=blog.category
            
        data["content"]=blog.content
        data["readType"]='public'
        data["source"]='pc_mdeditor'
        #data["tags"]=

        # 文章标签 例如 tags: git,github  表示文章的标签是什么
        # 文章专栏 例如 categories: git  表示是发布在哪个下专栏，专栏没有的话会建立
        # 发布形式：例如 readType:public 表示发布形式，值有 public，private，needfans(粉丝可见)，needvip（vip可见）


        return data

    def loadCategoryArticles(self,url):
        #访问category page
        # r=requests.get(url=url,headers=self.post_header)
        # page=r.content.decode("utf-8")
        page=self.load(url)
        bs = BeautifulSoup(page,features="lxml")
        list=bs.select('ul.column_article_list li a')
        return [{"url":l.get("href"),"title":l.select_one("h2").get_text().strip(),"updateTime":l.select_one('div.column_article_data span').get_text()} for l in list]


    def loadCategories(self, url):
        # r=requests.get(url=url,headers=self.post_header)
        # page=r.content.decode("utf-8")
        page=self.load(url)
        bs = BeautifulSoup(page,features="lxml")
        list=bs.select('div#asideCategory a.clearfix')
        return [{"url":l.get("href"),"title":l.select_one("span").get_text().strip()} for l in list]

    # def loadCategories(self, url):
    #     result=[]
    #     while url!=None:
    #         r=requests.get(url=url,headers=self.post_header)
    #         page=r.content.decode("utf-8")
    #         bs = BeautifulSoup(page,features="lxml")
    #         list=bs.select('div.article-list-item')
    #         for l in list:
    #             result.append({"url":l.get("href"),"title":l.select_one("span").get_text().strip()})

    def loadArticle(self,blog:Blog):
        logging.info("加载文章url:%s"%blog.url)
        id=blog.url[blog.url.rindex('/')+1:]
        #r=requests.get("https://mp.csdn.net/mdeditor/getArticle?id="+id,headers=self.post_header)
        #page=r.content.decode("utf-8")
        page=self.load("https://mp.csdn.net/mdeditor/getArticle?id="+id)
        j=json.loads(page)
        try:
            blog.content=j['data']['content']
            blog.mdText=j['data']['markdowncontent']
        except TypeError as e:
            print(e)

    def load(self, url):
        r=requests.get(url,headers=self.post_header)
        page=r.content.decode("utf-8")
        return page

