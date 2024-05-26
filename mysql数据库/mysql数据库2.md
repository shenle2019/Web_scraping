### 分组查询：

- 简单的分组查询

  - 注意：使用group by的查询字段必须是分组字段，否则会出错，想要获取其他字段信息,可以借助于聚合函数

- ```sql
  select job_title from emp group by job_title
  ```

- 分组聚合

- ```sql
  #查看每一个岗位的人数
  #count(1)每组的行数
  select job_title, count(1)from emp group by job_title
  
  #计算男女员工的平均年龄
  select gender,avg(age) from emp group by gender
  
  #计算不同岗位员工的平均薪资
  select job_title,avg(salary) from emp group by job_title
  
  #查看男女员工的最大,最小年级和整体年龄
  select gender,max(age),min(age),sum(age) from emp group by gender
  ```

- having子句

  - where 与 having的区别：	

    - where 是针对分组之前的字段内容进行过滤,而having是针对分组后的

  - 注意：having后面的条件字段只可以是分组后结果中存在的字段名，否则会报错！

  - ```sql
    #查看销售岗位的平均薪资
    select job_title,avg(salary) from emp GROUP BY job_title having job_title = 'sale'
    ```

### 多表查询

根据指定条件将两张表中的数据进行合并，然后在合并后的结果表中进行数据的查询

- 准备数据

- ```sql
  create table dep(
  	id int primary key,
  	name char(20)
  );
  create table emp(
  	id int primary key auto_increment,
  	name char(20),
  	sex enum("male","female") not null default "male",
  	age int,
  	dep_id int
  );
  
  # 插入数据
  insert into dep values
  (200,'技术'),
  (201,'人力资源'),
  (202,'销售'),
  (203,'运营');
  
  insert into emp(name,sex,age,dep_id) values
  ('ailsa','male',18,200),
  ('lala','female',48,201),
  ('huahua','male',38,201),
  ('zhangsan','female',28,202),
  ('zhaosi','male',18,200),
  ('shenteng','female',18,204)
  ;
  ```

- 内连接:（取交集）

  - 两张表公共的部分,必须同时有,没有就不显示

- ```
  #语法；select * from 表1 inner join 表2 on 合并条件
  select * from emp inner join dep on emp.dep_id = dep.id
  ```

- 外连接之左连接

  - 以左表为主表,根据左表数据匹配右表,左表数据是全的,而右表若匹配不上则为null

- ```
  select * from emp left join dep on emp.dep_id = dep.id
  ```

- 外连接之右连接

  - 以右表为主表,根据右表数据匹配左表,右表数据是全的,而左表若匹配不上则为null

- ```
  select * from emp right join dep on emp.dep_id = dep.id
  ```

![Snip20220820_54](/Users/zhangxiaobo/Desktop/mysql小课资料/课件/imgs/Snip20220820_54.png)

- 符合条件的多表联查

- ```sql
  #示例1：以内连接的方式查询emp和dep表，并且emp表中的age字段值必须大于25,即找出年龄大于25岁的员工姓名以及员工所在的部门
  select * from emp inner join dep on emp.dep_id = dep.id where age > 25
  #给表通过as起别名
  select d.name,e.name from emp as e inner join dep as d on e.dep_id = d.id where age > 25
  
  #示例2：以内连接的方式查询emp和dep表，并且emp表中的age字段值必须大于25，并且以age字段的升序方式显示
  select * from emp as e inner join dep as d on d.id = e.dep_id where age > 25 order by age
  
  #查询【所有部门】的部门名称和对应员工名字和年龄
  select d.name,e.name,e.age from emp as e right join dep as d on
  e.dep_id = d.id;
  
  #查询【所有员工】的名字和其对应的部门编号
  select d.id,e.name from emp as e left join dep as d on
  e.dep_id = d.id;
  ```

- 子查询:子查询是将一个查询语句嵌套在另一个查询语句中

  - 带in关键字的子查询

    - 查询平均年龄在25岁以上的部门名

  - ```sql
    #下述sql返回的就是201和202
    select dep_id from emp group by dep_id having avg(age) > 25
    
    #下述sql可以查询指定部门员工的姓名
    select name from dep where id in (200,201)
    
    #整合后的子查询语句
    select name from dep where id in 
    (
    	select dep_id from emp group by dep_id having avg(age) > 25
    )
    ```

    - 查看技术部员工姓名

  - ```sql
    select name from emp where dep_id in (200)
    #获取部门编号200
    select id from dep where name = '技术'
    
    #子查询
    select name from emp where dep_id in (
    	select id from dep where name = '技术'
    )
    ```

  - 带比较运算符的子查询(比较运算符: =、!=、>、>=、<、<=、<>)

    - 查询大于所有人平均年龄的员工名字与年龄

    - ```sql
      select id,name from emp where age > xx #xx就是所有员工的平均年龄
      #如何获取所有员工的平均年龄
      select avg(age) from emp
      
      #整合后的子查询
      select id,name from emp where age > (select avg(age) from emp)
      ```

### 条件判断

#### case when语句

语法格式

case when [expr] then [result1]...else [default] end

如果expr条件成立则返回result1，否则返回default，并且最后以end结束条件判断。

```sql
#建表  
CREATE TABLE t_demo (
 id int(32) NOT NULL,
 name varchar(255) DEFAULT NULL,
 age int(2) DEFAULT NULL,
 num int(3) DEFAULT NULL,
 PRIMARY KEY (`id`)
);

#插入数据
INSERT INTO t_demo VALUES ('1', '张三', '21', '69');
INSERT INTO t_demo VALUES ('2', '李四', '12', '98');
INSERT INTO t_demo VALUES ('3', '王五', '20', '54');
INSERT INTO t_demo VALUES ('4', '赵甜', '17', '80');

#给t_demo添加一列level，表示学生的得分等级
select * ,
  case 
  	when t.num >= 85 then '优秀'
    when t.num < 85 and t.num >= 60 then '一般'
    else '不及格'
  end as level
from t_demo as t;
```

#### if判断

用法1：if(expr1,ret1,ret2)

如果expr1条件为真，则返回ret1否则返回ret2

```sql
#添加一列表示学生是否成年
select *,
if(t.age >= 18,'成人','未成年') as 是否成年
from t_demo as t;
```

### 窗口函数

是MySQL8中新增的特性

#### 语法格式

```
窗口函数 over(partiton by 分组字段 order by 排序字段 asc|desc)
```

- 窗口函数的分类

1. rank() 
2. dense_rank()   
3. row_number()

- partiton by：
  - 将表数据根据partiton by后面的字段进行分组
  - partiton by和 group by分组的区别
    - group by 会改变显示结果的行数 【相当于按照字段 折叠 把同一组的数据折叠在一起】
    - partiton by 不会改变表显示的行数【与原表显示是一样的】 只是把相同组的数据归纳纵向相连在一起
- order by ：
  - 就是根据指定的字段进行排序

#### 排名开窗函数

数据集：student.sql

```sql
#给每一个班级的学生成绩从高到低进行排名，然后将排名结果作为新的一列和原始数据汇总到一起
#使用rank排名函数
select *,rank() over(partition by caption order by num desc) as 排名
from student;

#使用dense_rank排名函数，查看和rank的区别
select *,dense_rank() over(partition by caption order by num desc) as 排名
from student;

#使用row_number排名函数，查看和rank和dense_rank的区别
select *,row_number() over(partition by caption order by num desc) as 排名
from student;

#查询每个班级的分数排名为前2的学生信息
select * from
(select *, dense_rank() over(partition by caption order by num desc) 排名 from student) as e
where e.排名 <= 2;

#使用窗口函数查找每个班级成绩最高的所有学员信息
select * from 
(select *, dense_rank() over(partition by caption order by num desc) 排名 from student) as e
where 排名 <= 1;
```

### python连接数据库（重点）

- 环境安装：pip install pymysql
- 操作流程：

```python
#数据的增删改
import pymysql
#1.创建一个链接对象:决定了要去访问链接哪一个数据库服务器下的哪一个数据仓库
conn = pymysql.Connect(
    host='127.0.0.1',#数据库服务器的ip地址
    port=3306,#mysql的端口
    user='root',#mysql用户名
    password='boboadmin',#mysql的密码
    db='new_spider',#数据库的名字
    charset='utf8'#中文编码
)
#2.创建一个游标对象：可以让python执行sql语句
cursor = conn.cursor()
#3.使用游标对象执行sql语句(增删改)
# sql = 'delete from new_dep where id = 5'
# sql = 'insert into new_dep values (66,"haha","xxx")'
sql = 'update new_dep set dep_name="销售" where id = 66'
cursor.execute(sql)
#4.提交事务:让游标执行的sql语句完全的映射到数据库中
conn.commit()
#5.关闭资源
cursor.close()
conn.close()

```

```python
#数据查询操作
import pymysql
#1.创建一个链接对象:决定了要去访问链接哪一个数据库服务器下的哪一个数据仓库
conn = pymysql.Connect(
    host='127.0.0.1',#数据库服务器的ip地址
    port=3306,#mysql的端口
    user='root',#mysql用户名
    password='boboadmin',#mysql的密码
    db='new_spider',#数据库的名字
    charset='utf8'#中文编码
)
#2.创建一个游标对象：可以让python执行sql语句
cursor = conn.cursor()
#3.使用游标对象执行sql语句(查询)
# sql = 'select * from new_dep where id = 66'
sql = 'select * from new_dep'
cursor.execute(sql)
#4.获取查询结果
ret = cursor.fetchall()
print(ret)
#5.关闭资源
cursor.close()
conn.close()
```

- 爬取豆瓣电影数据，存储到数据库中

```python
import requests
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
for dic in page_text:
    title = dic['title']
    score = dic['score']
    print(title,score)
```

### pandas数据表格（重点）

- 环境安装：

```python
pip install openpyxl
pip install pandas
```

- 基础操作

```python
import pandas as pd
#pandas会帮我们创建一个数据表格，可以对数据表格进行相关操作，最后将该数据表格同步到excel

#1.手动的创建一个pandas的数据表格
table = pd.DataFrame(columns=['name','salary','job_title'])
#2.给数据表格插入数据
table.loc[0] = ['Jay',40000,'singer']
table.loc[1] = ['Tom',10000,'sale']
print(table)
#3.将数据表格转换成excel
table.to_excel('test.xlsx',sheet_name='haha')

```

- 爬取数据存储到excel

```python
import pandas as pd
import requests
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

#创建一个数据表格
table = pd.DataFrame(columns=['title','score'])

index = 0 #初始的行索引
for dic in page_text:
    title = dic['title']
    score = dic['score']
    table.loc[index] = [title,score]
    index += 1

table.to_excel('movie_list.xlsx',index=False)
print('存储成功！')

```



