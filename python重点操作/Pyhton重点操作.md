爬虫基础阶段：
​	请求与响应
​	http协议相关
​	数据解析
​	代理、验证码、cookie等
​	相关的反爬技能
​	数据库
​	Playwright高阶操作
​	三方抓包工具

目标：
不要一味地求快，
讲出来

### 重要数据类型

#### 列表数据类型 

- 在实际开发中，经常需要将一组（不只一个）数据存储起来，以便后边的代码使用。列表就是这样的一个数据结构。且列表是Python中最基本也是最常用的数据结构之一。

- 什么是数据结构呢？

  - 通俗来讲，可以将数据结构当做是某种容器，该容器是用来装载或者存储数据的。不同的数据结构决定了对数据不同的组织方式。
  - 那么当数据被装载或者存储到了某个数据结构中后，那么就可以基于该数据结构的特性对数据进行不同形式的处理和运算。

- 列表的创建方式

  - 创建一个列表，只要把逗号分隔的不同的数据元素使用方括号括起来即可。列表内的元素，可以是其它任意类型的数据，可多层嵌套列表，元素个数无限制。

  - ```python
    alist = [1,2,3,4,5]
    items = [1,'bobo',12.34]
    #列表中可以存储任意类型的数据
    ```

- 列表元素：

  - 存储在列表数据结构中的每一个数据被称为列表元素，简称元素。

- 列表索引：

  - 列表中的每个元素都被分配一个数字作为索引，用来表示该元素在列表内所排在的位置。第一个元素的索引是0，第二个索引是1，依此类推。

  ![Snip20231227_34](imgs/Snip20231227_34.png)

- 访问列表内的元素
  - 列表从0开始为它的每一个元素顺序创建下标索引，直到总长度减一。要访问它的某个元素，以方括号加下标值的方式即可。注意要确保索引不越界，一旦访问的 索引超过范围，会抛出异常。所以，一定要记得最后一个元素的索引是len(list)-1。

  - ```python
    alist = [1,12.3,'bobo']
    print(alist[2])  #'bobo'
    print(alist[0:2]) #[1, 12]
    print(alist[6]) #使用索引和切片的时候，不可以访问超出索引范围的元素
    ```
  
- 修改元素的值

  - 直接对元素进行重新赋值

  - ```python
    alist = [1,12.3,'bobo']
    alist[1] = 100.123
    print(alist)
    ```

- 删除元素

  - 使用del语句或者remove(),pop()方法删除指定的元素。

  - ```python
    alist = [1,12.3,'bobo']
    # del alist[0] #删除下标为0的列表元素
    # alist.remove('bobo') #删除列表中bobo这个列表元素
    # alist.pop() #默认情况下pop会把列表中最后一个元素删除
    alist.pop(2) #将列表中下标为2的元素进行删除
    print(alist)
    ```

- 切片

  - 切片指的是对序列进行截取，选取序列中的某一段。

    - 切片的语法是： list[start:end]

    - ```python
      #同字符串的切片机制一样
      alist = [1,12.3,'bobo','jay','hello']
      print(alist[:-1])
      ```

  - 以冒号分割索引，start代表起点索引，end代表结束点索引。省略start表示以0开始，省略end表示到列表的结尾。注意，区间是左闭右开的！也就是说[1:4]会截取列表的索引为1/2/3的3个元素，不会截取索引为4的元素。分片不会修改原有的列表，可以将结果保存到新的变量，因此切片也是一种安全操作，常被用来复制一个列表，例如newlist = lis[:]。

  - 切片过程中还可以设置步长，以第二个冒号分割，例如list[3:9:2]，表示每隔多少距离取一个元素。

- 列表的内置方法

  - 上文中我们说过，数据存储到不同的数据结构中，可以基于该数据结构的特性对数据进行指定形式的操作和处理。下图中的方法是列表专有的内置方法，请熟记于心。
  - ![33](imgs/33.png)

- ```python
  alist = ['bobo',"18","99.5",'北京']
  #将列表转换成字符串
  ret = '-'.join(alist) #将列表中的每一个列表元素根据-为间隔进行拼接，返回字符串结果
  print(ret)
  
  #如何将字符串转换成列表
  s = 'hello-name-bobo-age'
  ret = s.split('-')
  print(ret)
  
  alist = [3,8,5,7,6,2,1]
  alist.sort() #对列表元素进行排序
  print(alist)
  
  a = [1,2,3]
  a.append('bobo') #向列表尾部添加一个元素
  print(a)
  
  a1 = [1,2,3]
  a1.insert(1,999) #向列表下标为1的位置添加一个元素
  print(a1)
  ```

#### 字典数据类型

- 字典的实现机制：
  - Python的字典数据类型是基于hash散列算法实现的，采用键值对(key:value)的形式，根据key的值计算value的地址，具有非常快的查取和插入速度。

- 字典特性：
  - 字典包含的元素个数不限，值的类型可以是任何数据类型！但是字典的key必须是不可变的对象，例如整数、字符串、bytes和元组，最常见的还是将字符串作为key。列表、字典、集合等就不可以作为key。同时，同一个字典内的key必须是唯一的，但值则不必。
  - 注意：从Python3.6开始，字典是有序的！它将保持元素插入时的先后顺序！请务必清楚！

- 创建字典

  - 字典的每个键值对用冒号(:)分割，每个对之间用逗号(,)分割，整个字典包括在花括号({})中 ，例如：

    - d = {key1 : value1, key2 : value2 }

  - ```python
    #键值对：key : value
    #key：只能使用不可变类型的数据充当，通常使用字符串
    #value：任意数据类型的值充当
    #字典中无法存储重复的键值对
    dict_1 = {'name':'bobo','age':18,'score':100,'age':18}
    #注意：不要在字段中存储相同的key，value可以相同
    dict_2 = {'name':'bobo','age':18,'age':20}
    print(dict_2)
    ```

- 访问字典

  - 虽然现在的字典在访问时有序了，但字典依然是集合类型，不是序列类型，因此没有索引下标的概念，更没有切片的说法。但与list类似的地方是，字典采用把相应的键放入方括号内获取对应值的方式取值。

  - ```python
    d = {'name':'bobo','age':20,"scores":[100,120,99]}
    #根据key访问对应的value值
    print(d['name'],d['scores']) #依次访问name和scores对应的value值
    print(d.get('name')) #通过get使用对应的key访问对应的value值
    
    #注意：使用[]访问不存在的key对应的value值程序会报错
    # print(d['adress']) #程序报错
    
    #注意：使用get访问不存在的key程序不会报错，但是会返回None这个空值
    print(d.get('address'))
    ```

- 添加和修改

  - 增加就是往字典插入新的键值对，修改就是给原有的键赋予新的值。由于一个key只能对应一个值，所以，多次对一个key赋值，后面的值会把前面的值冲掉。

  ```python
  d = {'name':'bobo','age':20,"scores":[100,120,99]}
  d['name'] = 'jay' #给存在的key修改对应的value值
  d['address'] = 'Beijing' #给一个不存在的key赋值表示新增键值对
  del d['age'] #删除age键值对
  print(d)
  ```

- 删除字典元素、清空字典和删除字典

  - 使用del关键字删除字典元素或者字典本身，使用字典的clear()方法清空字典。

```python
d = {'name':'bobo','age':20,"scores":[100,120,99],'name':'bobo'}
del d['name']
print(d)

d = {'name':'bobo','age':20,"scores":[100,120,99],'name':'bobo'}
del d
print(d)

d = {'name':'bobo','age':20,"scores":[100,120,99],'name':'bobo'}
d.clear()
print(d)
```

- 字典的重要方法

```python
d = {'name':'bobo','age':20,"scores":[100,120,99]}
print(d.keys()) #返回字典中所有的key
print(d.values()) #返回字典中所有的value
print(d.items()) #返回字典中所有的键值对
```

### 练习

- 写一个程序，输出100以内的所有偶数，直到累加和大于1000停止程序。

```python
#写一个程序，输出100以内的所有偶数，直到累加和大于1000停止程序。
sum = 0 #用来存储累加后的结果
for i in range(101): #range(101)返回就是0-100之间的一个序列
    if i % 2 == 0:
        if sum >= 1000:
            break
        sum = sum + i
print(sum)
```

- 已知a+b+c=1000且a^2+b^2=c^2(a,b,c都是自然数)，求出符合条件的a,b,c的所有组合。

```python
#已知a+b+c=1000且a^2+b^2=c^2(a,b,c都是自然数)，求出符合条件的a,b,c的所有组合
for a in range(0,1001):#确定a的取值范围
    for b in range(0,1001):#确定b的取值范围
        c = 1000 - a - b
        if a + b + c == 1000 and a**2 + b**2 == c**2:
            print(a,b,c)
```

- 给定一个字符串string = "Hello, World!"，请统计字符串中每个字符的出现次数，并将结果存储在一个字典中。

```python
#给定一个字符串string = "Hello"，请统计字符串中每个字符的出现次数，并将结果存储在一个字典中。
string = "Hello"
char_count = {} #字典，用于保存每一个字符串的次数
for char in string:
    if char not in char_count:
        char_count[char] = 1
    else:
        char_count[char] += 1
print(char_count)
#{"H":1,'e':1,'l':2,'o':1}
```

- 猜数字游戏设计：可以不间断的进行猜数字游戏环节，找到猜对了，结束程序，猜不对，可以不断的进行游戏，并且需要提示用户猜打了还是猜小了。
  - 最后需要统计出，用户猜了多少次才猜对。
  - 每一个用户的初始分数为100，每猜错一次扣5分，最后程序结束，统计用户的得分

```python
#电脑随机生成一个随机数
import random #工具箱
guess_num = random.randint(0,10) #使用random工具箱中的randint工具生成一个0-10之间的随机数
count = 0 #用于保存用户猜的次数（就是循环的次数）
score = 100 #初始分值
while 1:#死循环
    count += 1
    #让用户从键盘上录入一个数字
    num = int(input('enter a num:'))
    #判断num和guess_num是否一样
    if num == guess_num:
        print('猜对了')
        break #只有猜对了，循环才会结束
    elif num < guess_num:
        print('猜小了')
        score -= 5
    else:
        print('猜大了')
        score -= 5

print('一共猜的次数:',count)
print('总计得分:',score)
```

### 文件操作

#### 引言  

- 到目前为止，我们做的一切操作，都是在内存里进行的，这样会有什么问题吗？如果一旦断电或发生意外关机了，那么你辛勤的工作成果将瞬间消失。是不是感觉事还挺大的呢？现在你是否感觉你的编程技巧还缺了点什么呢？是的，我们还缺少将数据在本地文件系统进行持久化的能力，白话讲就是文件的读写能力。

#### 文件打开

- Python内置了一个open()方法，用于对文件进行读写操作。使用open()方法操作文件就像把大象塞进冰箱一样，可以分三步走，一是打开文件，二是操作文件，三是关闭文件。
- 文件句柄/文件描述符
  - open()方法的返回值是一个file对象，可以将它赋值给一个变量，这个变量就是所谓的文件句柄。
  - file对象：
    - 可以调用read()和write()方法，对打开的文件进行读写操作。

- open方法的语法
  - f = open(filename, mode)
    - filename：
      - 一个包含了你要访问的文件名称的字符串值，通常是一个文件路径。
      - 文件路径作用：定位到指定文件
    - mode：
      - 打开文件的模式，有很多种，默认是只读方式r。

- 文件打开的模式：
  - 在Python中，使用内置的open函数时，可以指定不同的文件打开模式，这些模式定义了文件的访问和操作方式。常用的文件打开模式包括：
  - 'r'：只读模式，文件必须存在。
  - 'w'：写入模式，文件不存在则创建，存在则清空内容。
  - 'x'：写入模式，创建新文件，如果文件已存在则报错。
  - 'a'：追加模式，文件不存在则创建，存在则在末尾追加内容。
  - 'b'：二进制模式，用于音频、图像等非文本文件。
  - 't'：文本模式，默认模式，与'b'模式结合使用时，需放在最后。
  - '+'：更新模式，可以同时读写文件。

- 常规文件打开模式操作演示
  - b模式：
    - 二进制模式，通常用来读取图片、视频等二进制文件。注意，它在读写的时候是以bytes类型读写的，因此获得的是一个bytes对象而不是字符串。在这个读写过程中，需要自己指定编码格式。在使用带b的模式时一定要注意传入的数据类型，确保为bytes类型。
  - +模式：
    - 对于w+模式，在读写之前都会清空文件的内容。
    - 对于a+模式，永远只能在文件的末尾写入。
    - 对于r+模式，也就是读写模式。
- 编码问题
  - 要读取非UTF-8编码的文件，需要给open()函数传入encoding参数，例如，读取GBK编码的文件
  - 遇到有些编码不规范的文件，可能会抛出UnicodeDecodeError异常，这表示在文件中可能夹杂了一些非法编码的字符。遇到这种情况，可以提供errors=’ignore‘参数，表示如果遇到编码错误后如何处理。

#### 文件对象操作

- 每当我们用open方法打开一个文件时，将返回一个文件对象。这个对象内置了很多操作方法。

- f.read(size) #size读取数据的个数

  - 读取一定大小的数据, 然后作为字符串或字节对象返回。size是一个可选的数字类型的参数，用于指定读取的数据量。当size被忽略了或者为负值，那么该文件的所有内容都将被读取并且返回。
  - 注意：
    - 如果文件体积较大，请不要使用read()方法一次性读入内存，而是read(512)这种一点一点的读。

- f.readline()

  - 从文件中读取一行n内容。换行符为'\n'。如果返回一个空字符串，说明已经已经读取到最后一行。这种方法，通常是读一行，处理一行，并且不能回头，只能前进，读过的行不能再读了。

- f.readlines()

  - 将文件中所有的行，一行一行全部读入一个列表内，按顺序一个一个作为列表的元素，并返回这个列表。readlines方法会一次性将文件全部读入内存，所以也存在一定的风险。但是它有个好处，每行都保存在列表里，可以随意存取。

- ```python
  #需求：读取文件中的数据
  fp = open('./test.txt','r')
  text = fp.read(10) #读取指定字节的数据
  text_line = fp.readline() #一次读取一行数据
  text_lines = fp.readlines() #读取多行数据，返回一个列表
  print(text_lines)
  fp.close()
  ```

- 总结：

  - 几种不同的读取和遍历文件的方法比较：如果文件很小，read()一次性读取最方便；如果不能确定文件大小，反复调用read(size)比较保险；如果是配置文件，调用readlines()最方便。普通情况，使用for循环更好，速度更快。

- f.write()

  - 将字符串或bytes类型的数据写入文件内。write()动作可以多次重复进行，其实都是在内存中的操作，并不会立刻写回硬盘，直到执行close()方法后，才会将所有的写入操作反映到硬盘上。在这过程中，如果想将内存中的修改，立刻保存到硬盘上，可以使用f.flush()方法。

  - ```python
    fp = open('./test123.txt','w')
    fp.write('hello bobo')
    fp.close() #将文件内容清空，在写入新数据
    
    ```

  - ```python
    fp = open('./test123.txt','a')
    fp.write('hello bobo')
    fp.close() #在文件数据末尾追加数据
    
    ```

- f.close()

  - 关闭文件对象。当处理完一个文件后，调用f.close()来关闭文件并释放系统的资源。文件关闭后，如果尝试再次调用该文件对象，则会抛出异常。忘记调用close()的后果是数据可能只写了一部分到磁盘，剩下的丢失了，或者更糟糕的结果。也就是说大象塞进冰箱后，一定不要忘记关上冰箱的门。

#### with关键字

with关键字用于Python的上下文管理器机制。为了防止诸如open这一类文件打开方法在操作过程出现异常或错误，或者最后忘了执行close方法，文件非正常关闭等可能导致文件泄露、破坏的问题。Python提供了with这个上下文管理器机制，保证文件会被正常关闭。在它的管理下，不需要再写close语句。注意缩进。

```python
with open('./test123.txt','r') as fp: #fp = open()
    text = fp.read(5)
print(text)

#上下两组代码功效一样
fp = open('./test123.txt','r')
text = fp.read(5)
print(text)
fp.close()
```

- 对图片，音频，视频，压缩包等二进制的数据进行文件读写操作

  - 实现一个图片文件的拷贝

    - 1.打开一个图片文件，读取其二进制的数据

    - 2.将读取到的数据写入到另一个路径下

    - ```python
      #实现一个图片的复制粘贴功能
          #原理：将图片文件打开，读取图片文件中二进制的数据，将二进制数据写入到另一个文件即可
      
      def cvImg(imgPath,targetPath):
          #imgPath是原图文件路径
          #targetPath粘贴路径
          fp = open(imgPath,'rb') #打开原图
          img_data = fp.read() #读取图片数据
          new_fp = open(targetPath,'wb')
          new_fp.write(img_data)
          
          fp.close()
          new_fp.close()
          
      cvImg('./girl.jpg','./girls/meinv.jpg')
      
      ```




### 序列化模块(重点)   

> 序列化： 将python中的字典，列表对象转换成指定形式字符串
>
> 反序列化：将指定格式的字符串转换成字典，列表对象

- 基本使用

- ```python
  import json
  dic = {
      'hobby':['football','pingpang','smoke'],
      'age':20,
      'score':97.6,
      'name':'zhangsan'
  }
  #序列化：将字典对象转换成了json格式的字符串
  r = json.dumps(dic)
  print(r)
  ```
  
  ```python
  import json
  
  str = '{"hobby": ["football", "pingpang", "smoke"], "age": 20, "score": 97.6, "name": "zhangsan"}'
  #反序列化：将字符串转换成了字典对象
  dic = json.loads(str)
  print(dic)
  ```

  ```python
  #持久化存储字典
  import json
  dic = {
      'hobby':['football','pingpang','smoke'],
      'age':20,
      'score':97.6,
      'name':'zhangsan'
  }
  fp = open('./dic.json','a')
  #dump首先将dic字典进行序列化，然后将序列化后的结果写入到了fp表示的文件中
  json.dump(dic,fp)
  fp.close()
  ```

  ```python
  import json
  fp = open('./dic.json','r')
  #load将文件中的字符串数据进行读取，且将其转换成字典类型
  dic = json.load(fp)
  print(dic)
  fp.close()
  ```

### 正则模块(一般/不重要)  http协议

- 什么是正则表达式？

  - 正则表达式(Regular Expression)是一种文本模式，包括普通字符（例如，a 到 z 之间的字母）和特殊字符（例如，*，+，？等）。
  - 正则表达式使用单个字符串来描述、匹配一系列匹配某个句法规则的字符串。

- 常用的正则标识

- ```
  单字符：
      . : 除换行以外所有字符
      [] ：[aoe] [a-w] 匹配集合中任意一个字符
      \d ：数字  [0-9]
     
  数量修饰：
      * : 任意多次  >=0
      + : 至少1次   >=1
      ? : 可有可无  0次或者1次
      {m} ：固定m次 hello{3,}
      {m,} ：至少m次
      {m,n} ：m-n次
  边界：
      $ : 以某某结尾 
      ^ : 以某某开头
  分组：
  		(ab)  
  贪婪模式： .*
  非贪婪（惰性）模式： .*?
  
  ```

- 正则在python中的使用

  - 基于re模块进行正则匹配操作

  - 主要使用re模块中的findall进行指定规则的匹配

    - findall(str,rule)
      - str表示即将进行匹配的原始字符串数据
      - rule表示指定规则的正则表达式
      - findall返回的是列表，列表中存储匹配到的指定内容

  - 练习

  - ```python
    import re
    
    #提取170
    string = '我喜欢身高为170的女孩'
    ex = '\d+'
    result = re.findall(ex,string)
    print(result[0])
    #####################################################################
    #提取出http://和https://
    key='http://www.baidu.com and https://boob.com'
    ex = 'https?://'
    result = re.findall(ex,key)
    print(result)
    #####################################################################
    import re
    #提取出hello
    key='lalala<hTml>hello</HtMl>hahah' #输出<hTml>hello</HtMl>
    ex = '<hTml>.*</HtMl>'
    result = re.findall(ex,key)
    print(result)
    
    #####################################################################
    #提取出hit.
    key='bobo@hit.edu.com'#想要匹配到hit.
    # ex = 'h.*\.' #贪婪模式
    ex = 'h.*?\.' #？将正则的贪婪模式调整为非贪婪模式。默认下为贪婪模式
    result = re.findall(ex,key)
    print(result)
    #####################################################################
    #匹配sas和saas
    key='saas and sas and saaas'
    ex = 'sa{1,2}s'
    result = re.findall(ex,key)
    print(result)
    #####################################################################
    key = '你好我的手机号是13222222222你记住了吗'
    ex = '1[3,5,7,8,9]\d{9}'
    result = re.findall(ex,key)
    print(result)
    ```

    







