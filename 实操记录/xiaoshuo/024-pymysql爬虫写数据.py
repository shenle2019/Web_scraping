import requests
import pymysql
head = { #存放需要伪装的头信息
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
}
pram = {
    "type": "13",
    "interval_id": "100:90",
    "action": "",
    "start": "0",
    "limit": "20",
}
url = 'https://movie.douban.com/j/chart/top_list'
response = requests.get(url=url,headers=head,params=pram)
#获取响应数据
#json()可以将获取到的json格式的字符串进行反序列化
page_text = response.json()

#1.创建一个链接对象:决定了要去访问链接哪一个数据库服务器下的哪一个数据仓库
conn = pymysql.Connect(
    host='127.0.0.1',#数据库服务器的ip地址
    port=3306,#mysql的端口
    user='root',#mysql用户名
    password='123456',#mysql的密码
    db='test',#数据库的名字
    charset='utf8'#中文编码
)
#2.创建一个游标对象：可以让python执行sql语句
cursor = conn.cursor()

for dic in page_text:
    title = dic['title']
    score = dic['score']
    ### print(title,score)
    sql = 'insert into t1 values ("{}","{}")'.format(title,score)
    cursor.execute(sql)
    conn.commit()

# 4.获取查询结果
sql2 = 'SELECT * FROM T1'
cursor.execute(sql2)
ret = cursor.fetchall()
print(ret)

# 5.关闭资源
cursor.close()
conn.close()

