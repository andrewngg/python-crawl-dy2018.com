import requests, re
import pymysql
from lxml import etree

db = None
def connect_db():
    global db
    # 打开数据库连接
    db = pymysql.connect("localhost", "root", "root", "movies")

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    return cursor

def insert_data(sql=None):

    global db
    cursor = connect_db()
    if sql is None:
        return None

    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except:
        db.rollback()
    # 关闭数据库连接
    db.close()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # 如果要带着cookie 可以传入cookie，也可以放在报文头当中
    #'Cookie':'这里放入cookie'
}
with open(r'C:\Users\Administrator.USER-20181205XU\Desktop\china_fun_movie.txt', 'r') as f:
    for line in f.readlines():
        url = line.strip()  # 把末尾的'\n'删掉
        response = requests.get(url=url, headers=headers)
        try:
            html = response.content.decode('gbk')
        except:
            html = response.content
        #print(html)
        sub_url = url.replace("https://www.dy2018.com", "")
        tree = etree.HTML(html)
        separator = "|"
        links = tree.xpath("//table/tbody/tr/td/a/@href")
        final_links = separator.join(links)
        print(final_links)
        insert_data("UPDATE dy SET torrent_link='%s' WHERE link='%s'" % (final_links, sub_url))

