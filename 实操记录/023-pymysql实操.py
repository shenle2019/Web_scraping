import pymysql
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
#3.使用游标对象执行sql语句(查询)
# sql = 'select * from new_dep where id = 66'
sql = 'select * from t1'
cursor.execute(sql)
#4.获取查询结果
ret = cursor.fetchall()
print(ret)
#5.关闭资源
cursor.close()
conn.close()