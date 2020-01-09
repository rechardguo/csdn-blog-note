# coding=utf-8
import base64
import logging
import sqlite3
from pathlib import Path

import os

from Article import Blog
from RequestCSDNService import CSDNService


class BlogCache:
    def __init__(self) -> None:
         path=Path()
         conn = self.connection()
         c = conn.cursor()
         cursor=c.execute("select count(1) from sqlite_master where type = 'table' and name = 'blog'")
         row=cursor.fetchone()
         if row==None or row[0]==0:
             c.execute('''create table blog(id INTEGER primary key, title varchar(100),url varchar(200),category varchar(200),
                     categoryUrl varchar(200),mdText LONGTEXT,content LONGTEXT,
                     lastUpdateTime DATETIME)''')
             conn.commit()
         conn.close()

    def connection(self):
        dbDataFile='c:/notemain/data.db'
        if not os.path.exists(dbDataFile):
            if not os.path.exists('c:/notemain'):
                os.makedirs('c:/notemain')
            f = open(dbDataFile,'w+')
            f.close()
        return  sqlite3.connect('c:/notemain/data.db')

    def saveArticlies(self,blogList:[]):
        conn =  self.connection()
        c = conn.cursor()
        for item in blogList:
            if item.mdText==None:
                continue
            logging.info("save blog title:%s"%item.url)

            deleteSql="delete from blog where url='%s'"%item.url

            sql="insert into blog(id,title,url,category,categoryUrl,mdText,content,lastUpdateTime)values((select max(id)+1 from blog),'%s','%s','%s','%s','%s','%s','%s')" \
                 %(item.title,item.url,item.category,item.categoryUrl,base64.b64encode(item.mdText.encode()).decode(),base64.b64encode(item.content.encode()).decode(),item.lastUpdateTime)

            #sql="insert into blog(id,title,url,category,categoryUrl,mdText,content,lastUpdateTime)values((select max(id)+1 from blog),'%s','%s','%s','%s','%s','%s','%s')" \
            #    %(item.title,item.url,item.category,item.categoryUrl,item.mdText,item.content,item.lastUpdateTime)
            c = conn.cursor()
            c.execute(deleteSql)
            c.execute(sql)
        conn.commit()
        conn.close()

    def searchAllDraft(self):
        return self.searchArticle(**{"category":"draft"})

    def searchAllPublished(self):
        '''
        :return:
         {
          category:{
            "category":category,
            "categoryUrl":categoryUrl,
            "blogs":[blog1,blog2]
          }
         }
        '''
        map={}
        blogs=self.searchArticle(all=True)
        for blog in list(blogs):
            if blog.category=='draft':
                continue
            cateMap=map.get(blog.category)
            if cateMap==None:
                cateMap={}
                cateMap.update({'categoryUrl':blog.categoryUrl,'category':blog.category,'blogs':[]})
                map.update({blog.category:cateMap})
            catBlogs=cateMap.get('blogs')
            catBlogs.append(blog)
        return map

    # def dict_factory(cursor, row):
    #    d = {}
    #    for idx, col in enumerate(cursor.description):
    #     d[col[0]] = row[idx]
    #    return d

    #模糊查找
    def fuzzySearch(self,data:str):
        sql="select title,content from blog"
        if not data or len(data.strip())==0:
            return
        conn =  self.connection()
        cur = conn.cursor()
        cursor = cur.execute(sql)
        res = cursor.fetchall()
        result=[]
        for line in res:
            title=str(line[0])
            content=str(base64.b64decode(line[1].encode()).decode("utf-8"))
            if content.find(data)!=-1 or title.find(data)!=-1:
                result.append(title)
        return result

    def searchArticle(self,all=False,**kwargs):
        condition=""
        sql="select * from blog"
        for (k,v) in kwargs.items():
            if condition!="":
                condition=condition+" and "
            condition=condition+k+"='"+v+"'"
        if condition=="":
            if not all:
                return
        else:
            sql=sql+" where "+condition
        conn =  self.connection()
        #conn.row_factory=self.dict_factory
        cur = conn.cursor()
        cursor = cur.execute(sql)
        res = cursor.fetchall()
        result=[]
        for line in res:
            b=Blog() #id,title,url,category,categoryUrl,mdText,content,lastUpdateTime
            b.title=line[1]
            b.url=line[2]
            b.category=line[3]
            b.categoryUrl=line[4]
            b.mdText=base64.b64decode(line[5].encode()).decode("utf-8")
            b.content=base64.b64decode(line[6].encode()).decode("utf-8")
            #b.mdText=line[5]
            #b.content=line[6]
            b.lastUpdateTime=line[7]
            result.append(b)
        return result
#
# if __name__ == '__main__':
#     cache=BlogCache()
#     blog=Blog()
#     blog.categoryUrl="test"
#     blog.category="test2"
#     blog.title="123"
#     blog.url="https://blog.csdn.net/guo_xl/article/details/82388273"
#     blog.lastUpdateTime='2019-11-17 14:44:35'
#     mdText=CSDNService().loadArticle(blog.url)
#     blog.mdText=mdText
#     cache.saveArticlies([blog])
#     criteria={'lastUpdateTime':'2018-10-25 19:18:09','url':'https://blog.csdn.net/guo_xl/article/details/83384755'}
#     result=cache.searchArticle(all=True)
#     for i in list(result):
#      print(i)
