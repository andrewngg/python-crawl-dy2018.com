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

def handle(html):
    tree = etree.HTML(html)
    nodes = tree.xpath("//table/tr[2]/td[2]/b/a[2]")
    links = tree.xpath("//table/tr[2]/td[2]/b/a[2]/@href")
    categories = tree.xpath("//table/tr[4]/td/p[2]/text()")
    location = None
    year = None
    for i, each in enumerate(nodes):
        movie = each.text
        try:
            m = re.match(r'\s*(\d+)?年?(\D+)?([\d\.]+分?)?([^《]+)《([^》]+)》(.*)', movie, re.M | re.I)
            if location is None:
                year = 0
            else:
                year = m[1]

            if location is None:
                location = ''
            else:
                location = m[2]
            if m[3] is None:
                rating = 0
            else:
                rating = m[3].replace('分', '')
            types = m[4]
            title = m[5].replace("'", "\'")
            suffix = m[6]
            link = links[i]
            category = categories[i].replace("\r\n", "").replace("  ", "").replace(" ", "").replace("◎标签:", "").replace("◎类型:", "").replace("/", ",")

            sql = "INSERT INTO dy " \
                  "SET year=%s, title='%s', location='%s', rating='%s', types='%s', suffix='%s', link='%s', category='%s', cat_id='%s'" \
                  % (year, title, location, rating, types, suffix, link, category, str(cat))
            print(sql)
            insert_data(sql)
        except:
            pass


# 伪装我们的报文头，加上Use-Agent 伪装成浏览器
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # 如果要带着cookie 可以传入cookie，也可以放在报文头当中
    #'Cookie':'这里放入cookie'
}

for cat in range(0, 21):
    cat_page = 'https://www.dy2018.com/' + str(cat) + '/'
    response = requests.get(url=cat_page, headers=headers)

    cat_html = response.content.decode('gbk')
    handle(cat_html)
    tree = etree.HTML(cat_html)

    pages = tree.xpath("//*[@id=\"header\"]/div/div[3]/div[5]/div[2]/div[2]/div[2]/div/p/text()")[0].replace("\r\n", "")
    total_page = re.match(r'页次：\d+\s*\/\s*(\d+)', pages, re.M | re.I)[1]
    print("Cat %s have %s pages" % (str(cat), str(total_page)))
    start_with = 2
    for page in range(start_with, int(total_page)):
        print("Handling cat %s page %s" % (str(cat), str(page)))
        url = "https://www.dy2018.com/%s/index_%s.html" % (str(cat), str(page))
        print(url)
        response = requests.get(url=url, headers=headers)
        try:
            html = response.content.decode('gbk')
        except:
            html = response.content
        handle(html)

