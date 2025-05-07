
### JS ��������

```js
/*
var obj = {
    name: "yuan",
    age: 18,
    gfs:{
        count:1000,
        names_arr:["��ԲԲ","�����"]
    }
}

console.log(obj.name)
console.log(obj.gfs.names_arr)*/


// ������������
/*function foo(){
    console.log("foo")
}
foo()*/


/*function Foo() {
    this.name = "yuan"
    this.age = 18
    this.bar = function () {
        console.log("bar...")
    }
}

var f1 = new Foo()
console.log(f1)
console.log(f1.name)
console.log(f1.age)

f1.bar()*/


/*function Person(name, age) {
    this.name = name
    this.age = age
    /!*this.bar = function () {
        console.log("bar...")
    }*!/
}*/

/*Person.prototype.eat = function () {
    console.log(this.name+"���ڳԶ���")
}

p1 = new Person("alex", 22)
p1.eat()
// p1.bar()

p2 = new Person("rain", 32)
p2.eat()*/
// p2.bar()


// call����

/*function Person(name, age) {
    this.name = name
    this.age = age
}

p = new Person("yuan", 22)

function eat() {
    // "use strict";
    console.log("this:::", this)
    console.log(this.name + "���ڳԶ���")
}*/

// eat.call(p)
// eat.apply(p)


/*
function Person(name, age) {
    this.name = name
    this.age = age
}

p = new Person("yuan", 22)

function eat(a, b, c) {
    console.log(this.name + "���ڳԶ���")
    console.log(a)
    console.log(b)
    console.log(c)
}


var foods = ["apple", "banana", "peach"]
eat.apply(p, foods)
eat.call(p, foods)*/
```

### ��ͷ����

```js

// var
// let


/*function foo(item) {
    return item ** 2
}

console.log(foo(12))


var bar = i => i ** 2

console.log(bar(12))*/

let getUser = id => {
    let x = 1 + 1;
    return x ** 2
}
console.log(getUser(100))

let getUser2 = id => ({id: id, name: "yuan"})
console.log(getUser2(100))

l = [23, 45, 323, 12, 7,32]
// console.log(l.map(item => item ** 2))
// console.log(l.filter(item => item % 2 === 0))

```

### expors �﷨

- cal.js

```js

// �ӷ�����
function add(a, b) {
    return a + b;
}

// �˷�����
function multiply(a, b) {
    return a * b;
}

// exports.add = add;
// exports.multiply = multiply;

exports.cal_obj = {
    "add": add,
    "multiply": multiply
}

```

```js

var {cal_obj} = require("./cal")

console.log(cal_obj.add(11, 22))
console.log(cal_obj.multiply(11, 22))

```

### window����

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>

    <script>

        // JS�� ECMA��BOM��DOM

        /*
        function foo() {

            // cssѡ����
            dom = document.querySelector("h3")
            console.log(dom)
            dom.innerHTML = "hello yuan"
        }*/


        // (1) window��ȫ���ص�
        /*
        var username = "yuanhao";  //ȫ�ֱ���

        function f() {  //ȫ�ֺ���
            console.log(username);

            function bar() {
                console.log("bar...")
            }

            window.yuan = bar

        }

        f()
        window.yuan()*/

        // (2) window�Ŀ�

        // window.alert("�����������ˣ���ע��")
        // var ret = window.confirm("��Ϸ�Ƿ������")
        // console.log(ret)
        // var ret = window.prompt("��������ѡ�������")
        // console.log(ret)

        // alert()

        // (3) ���ʿͻ��˶���
        /*
        - window���ͻ��� JavaScript �������ÿ�� <body> �� <frameset> ��ǩ����ʱ��window ����ͻᱻ�Զ�������
        - navigator�������ͻ����й��������Ϣ��
        - screen�������ͻ�����Ļ����Ϣ��
        - history��������������ڷ��ʹ��� URL ��Ϣ��
        - location��������ǰ��ҳ�ĵ��� URL ��Ϣ��
        - document���������� HTML �ĵ����ɱ����������ĵ����ݼ�������ҳ��Ԫ�ء�*/


        // (4)  setInterval setTimeout
        /*
        var count = 0
        var ID = setInterval(function () {
            count++
            console.log(count)
        }, 1000)

        clearInterval(ID)*/
        /*
        function foo() {
            var now = new Date().toLocaleString()
            console.log(now)
            dom = document.querySelector("input")
            dom.value = now
        }

        function start() {
              foo()
              setInterval(foo,1000)
        }*/


        function bar() {
            console.log("bar")
        }

        var ID = setTimeout(bar, 5000)

        clearTimeout(ID)


    </script>
</head>
<body>

<h3 onclick="foo()">welcome to JS</h3>

<input type="text">
<button onclick="start()">show</button>

</body>
</html>

```

### ���֪ʶ��

```python

# class Student(object):
#     students = []
#
#     def add_stu(self):
#         print("���ѧ��")
#
#     def del_stu(self):
#         print("ɾ��ѧ��")
#
#     def update_stu(self):
#         print("���ѧ��")
#
#     def show_stu(self):
#         print("����ѧ��")
#
#
# class Customer(object):
#     customer = []
#
#     def add_customer(self):
#         print("��ӿͻ�")
#
#     def del_customer(self):
#         print("ɾ���ͻ�")
#
#     def update_customer(self):
#         print("��ӿͻ�")
#
#     def show_customer(self):
#         print("���ǿͻ�")


# �汾2����


# class Dog:
#     # ���ԣ�����
#     # ��Ϊ������
#     leg_num = 4
#     has_hair = True
#
#     def bark(self):
#         print("���")
#
#     def kenGuTou(self):
#         print("�й�ͷ")
#
# alex = Dog()
# print(alex.leg_num)
# print(alex.has_hair)
# alex.kenGuTou()
#
# peiQi = Dog()
# print(alex.leg_num)
# print(alex.has_hair)
# peiQi.kenGuTou()


# l = [23, 45, 323, 12, 7]
# print([i ** 2 for i in l])

# def foo(item):
#     return item**2
#
# print(list(map(foo, l)))

# print(list(map(lambda item:item**2, l)))


# l = [23, 45, 323, 12, 7]

# for i in l:
#     if i % 2 != 0:
#         l.remove(i)
# print(l)

# l2 = []
# for i in l:
#     if i % 2 == 0:
#         l2.append(i)
# print(l2)
#
# l = l2

l = [23, 45, 323, 12, 7, 22]
print(list(filter(lambda i: i % 2 == 0, l)))

person_list = [
    {"name": "yuan", "gfs": ["��ԲԲ", "�����"]},
    {"name": "rain", "gfs": ["��ԲԲ", "�����", "����ӱ"]},
    {"name": "alex", "gfs": ["�ֵ�"]},
]

print(list(filter(lambda item: len(item.get("gfs")) >= 2, person_list)))


```


### url����

```python
import urllib.parse

# (1) ֵ����
# x = "!"
# x = "#"
# x = "Է"
# # url����
# ret = urllib.parse.quote(x)
# print(ret)


# (2) ���ֵ�תΪurlencoded��ʽ�ַ���
data = {
    "wd": "��Ů",
    "page": 1
}
ret = urllib.parse.urlencode(data)
print(ret)  # "wd=%E7%BE%8E%E5%A5%B3&page=1"

data2 = {
    "device_platform": "webapp",
    "aid": 6383,
    "channel": "channel_pc_web",
    "sec_user_id": "MS4wLjABAAAAQERLUS1XLl1qZMZDkibRWUdHGBAoG0pJq_5hAj3XjIZXnxgtW_CcE17nuHHfikpQ",
    "max_cursor": 0,
    "locate_query": "false",
    "show_live_replay_strategy": 1,
}

# ret2 = urllib.parse.urlencode(data2)
# print(ret2) # device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAAQERLUS1XLl1qZMZDkibRWUdHGBAoG0pJq_5hAj3XjIZXnxgtW_CcE17nuHHfikpQ&max_cursor=0&locate_query=false&show_live_replay_strategy=1


# (3) ��urlencoded��ʽ�ַ���תΪ�ֵ�

# res = "device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAAQERLUS1XLl1qZMZDkibRWUdHGBAoG0pJq_5hAj3XjIZXnxgtW_CcE17nuHHfikpQ&max_cursor=0&locate_query=false&show_live_replay_strategy=1"

# print(urllib.parse.parse_qs(res))
# print(urllib.parse.parse_qsl(res))

```


### ��������

```python
import requests
import urllib.parse

headers = {
    'authority': 'www.douyin.com',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': 'ttwid=1%7CvQ6QCiLyIG9SJypBIXRtIfGPJXv6br9a79NgmLfR-U4%7C1697436889%7C0ea69e384e5deb1dc65f4200190d8d2f33f9c4ca6c30e10208ee46af29a5015d; xgplayer_user_id=905282558930; live_use_vvc=%22false%22; bd_ticket_guard_client_web_domain=2; n_mh=k9zkCfOQfFegoa7kc0V7SXvDVdHwnUROJ967U1dUUI0; store-region=cn-bj; store-region-src=uid; LOGIN_STATUS=0; odin_tt=20343b08ecb1611a4b04324c1a697f7e92e68e324e4606b2c80abadd3210987dc5b78518a2b0b6e221726782326016937e13203155c45a3b6a704d48ceb7e65e7f250011dbd98cd56711807de5cccdf0; passport_csrf_token=b00b43817b50596803e09e6ce4e0657b; passport_csrf_token_default=b00b43817b50596803e09e6ce4e0657b; s_v_web_id=verify_lsub58hh_glq5XScC_Tt8r_4mRB_8zor_2Bk8mJbmvS1j; dy_swidth=1728; dy_sheight=1117; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; download_guide=%223%2F20240324%2F0%22; pwa2=%220%7C0%7C3%7C0%22; __ac_nonce=06609539900318e8d992d; __ac_signature=_02B4Z6wo00f018hEBiAAAIDAmrsmOsmX6J.IZAKAAJQhgTVtaXgfw8kaFLXiCBfESOsjTGTavK2heYsdJ6T7o156O0rYlNZEfxZSWPmO2zDaBNC5Is49dOHBhzInU4364EahTZHnzS-n6AzW6e; strategyABtestKey=%221711887259.853%22; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.314%7D; SEARCH_RESULT_LIST_TYPE=%22single%22; GlobalGuideTimes=%221711887290%7C0%22; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQnNtWm5qUEJ6SExwVlpzZjhzV1BoYWlOQzJZM0ZNNk9iTnNoOGRQMzFmRFVtOVdDLzhXWHJ4NVFDTXZvTWZLdFNuMVlKU2ZvclVETmZ6SEkrUkF5MVE9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; douyin.com; xg_device_score=7.750418532313436; device_web_cpu_core=10; device_web_memory_size=8; csrf_session_id=4f58a2384ec86335f78ba7f0dcf78a69; stream_player_status_params=%22%7B%5C%22is_auto_play%5C%22%3A0%2C%5C%22is_full_screen%5C%22%3A0%2C%5C%22is_full_webscreen%5C%22%3A0%2C%5C%22is_mute%5C%22%3A1%2C%5C%22is_speed%5C%22%3A1%2C%5C%22is_visible%5C%22%3A0%7D%22; msToken=mCY7fXd3-COC_vgzqW7DmsZ2bbjHCrO1FZ5j1BsdHyLy3kp_FI7n1o3h1sV6zLD9u4n-n21fpPSpgzePExHAbpQQf7F2xoxGgrAX5L8QZH5i9HKK5I7_ZU55xT5fbA==; tt_scid=17ylA14KQE4k99NOPYI-Dojgn6j3bTye7Q42BntLjJXK5..2BgRJ.pR4Bu-KAqXV4900; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1728%2C%5C%22screen_height%5C%22%3A1117%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A10%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A10%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A50%7D%22; home_can_add_dy_2_desktop=%221%22; msToken=wJqXkF2J0OJ9CVXYCFAXvBhnU6J-pkycr_Q3vnUhZZ0ba250wlXxi7reFBq7_7Hg5X8Xlj64taHci_gUPKKJH-cqUtx0lP7-x337p2awomZ9aUr5L5bRd8cX97GfKw==; IsDouyinActive=false',
    'pragma': 'no-cache',
    'referer': 'https://www.douyin.com/user/MS4wLjABAAAAQERLUS1XLl1qZMZDkibRWUdHGBAoG0pJq_5hAj3XjIZXnxgtW_CcE17nuHHfikpQ',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

params_str = "device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id=MS4wLjABAAAAQERLUS1XLl1qZMZDkibRWUdHGBAoG0pJq_5hAj3XjIZXnxgtW_CcE17nuHHfikpQ&max_cursor=1704240643000&locate_query=false&show_live_replay_strategy=1&need_time_list=0&time_list_query=0&whale_cut_token=&cut_version=1&count=18&publish_video_strategy_type=2&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1728&screen_height=1117&browser_language=zh-CN&browser_platform=MacIntel&browser_name=Chrome&browser_version=122.0.0.0&browser_online=true&engine_name=Blink&engine_version=122.0.0.0&os_name=Mac+OS&os_version=10.15.7&cpu_core_num=10&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=50&webid=7290435875619390995&msToken=wJqXkF2J0OJ9CVXYCFAXvBhnU6J-pkycr_Q3vnUhZZ0ba250wlXxi7reFBq7_7Hg5X8Xlj64taHci_gUPKKJH-cqUtx0lP7-x337p2awomZ9aUr5L5bRd8cX97GfKw==&X-Bogus=DFSzswVEK/sANCC6t-9vdELNKBPU"
params = urllib.parse.parse_qs(params_str, strict_parsing=True)
print(params)

# response = requests.get(
#     'https://www.douyin.com/aweme/v1/web/aweme/post/',
#     headers=headers,
# )
# print(response.text)

```

### base64����

```python
import base64

# print(ord("a"))
# print(ord("b"))
# print(chr(65))
# print(chr(66))

# ����1
# # s = "you"
# s = "Է�"
#
# # (1) ���ݻ������루GBK��utf8��
# s = s.encode("GBK") # Ĭ��utf8
# # (2) base64����
# ret = base64.b64encode(s).decode()
# print(ret)
# # (3) base64����
# res = "1Lfquw=="
# ret = base64.b64decode(res)
# print(ret)
# # (4) �������루GBK��utf8��
# print(ret.decode())


# ����2

# s = "y"
# ret = base64.b64encode(s.encode())
# print(ret)


import base64

# s = "eW91"
# ret = base64.b64decode(s)
# print(ret)

# s = "eW91eQ"
# s += "="*(4-len(s)%4)
# ret = base64.b64decode(s).decode()
# print(ret)


# ����3 base64����

# res = "Z21kD9ZK1ke6ugku2ccWu-MeDWh3z252xRTQv-wZ6jddVo3tJLe7gIXz4PyxGl73nSfLAADyElSjjvrYdCvEP4pfohVVEX1DxoI0yhm36ytQNvu-WLU94qULZQ72aml6JKK7ArS9fJXAcsG7ufBIE0gd6fbnhFcsGmdXspZe-8 whVFbRB_8Fc9JlMHh8DDXnskDhGfEscN_rfi-A-AHB3F9Vets82vIYpkGNaJOft_JA-m5cGEjo-UNRDDpkTz_NIAvo5PbATpkh7PSna2tHcE6Hou9GBtPLB67vjScwplB96-zqZKXJJEzU5HGF0oPDY_weAkXArzXyGLBPXFCnn_IWJDkGD4vqBQQAh2n52f48GD_cb-PSCT_8b-ESsKUI9NJa11XsdaUZxAc8TzrYnXwdcQbtl_kZGKhS6_rCtuNEBouA_lvM2CbS7TTtV2U4zVmJKpp-c6nt3yZePK3Av01GWn1pH_3sZbaPEx8DUjSbdp4i4iK-Mj4p2HPoph67DR7B9MFETYku_28SgP9xsKRRvFH4aHBHESWX4FDbwaU="
# res = res.replace("-","+").replace("_","/")
# ret = base64.b64decode(res)
# print(ret)


# ����4

# img_base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAA7VBMVEUAAAD////////s8v////+txP+qwv+4zf/w9f/2+P+hu//Q3f+yyP+4zf/Q3f////+kvv+90P+80f+2yv/S4P/T4P/M2//z9/+cuP/V4P9Whv////9Uhf9Sg/9Pgf9NgP/8/f9di/9Xh/9lkf5aif9qlP7z9//k7P/c5v+2y/94nv51nP6lv/+LrP6Ep/6BpP5gjf7v9P+wxv/U4f/M2/+sxP+vxv73+f/P3v/J2v+5zf+ivP+fuv9xmf+Ytv6Usv6Hqf58of5vl/7m7v/g6f+zyf6QsP75+//q8P/B0v/W4//C1P6+0P6qwv6ct/76fHZiAAAAGnRSTlMAGAaVR/Py45aC9Mfy2b8t9OPZ2ce/v4L0x/e74/EAAAIZSURBVDjLZVPXYuIwEDSmQ4BLv5O0ku3Yhwu2IZTQe0hy7f8/57QSoYR5sVea1c424wgzl324LRRuH7I507hEJluYucCFEOBGhWzmy7X5+N0WwIjTbrcdBsKulM0z96onGCGE2X6n+cTkj/CqJ480igzkNXp26E9JkABSbBz8i4Bn3EkH840mKHoxs49fZQzt2Kd03FQEzSB3WsejB9Jqf1CJQBM0wCurABWBoub0gkDENwyStTHA62pwSWDtklRQ4FLfjnaiPqVW60hAYeLKNHIREOZuKTL80H6XBFCwn4BAmDOyLiOQUIlOSEjaoS+Ju57NZuul73Fml4w6yAivSLBW3MGfcfBmIegmArg3alICdJHgy1jQt8Z/6CcC4DdGXhLIoiWRACpbLYbDYW80GnXp2GH8ShP+PUvEoHsAIFq9Xm8+kXlIwkkI9pm+05Tm3yWqu9EiB0pkwjWBx2i+tND1XqeZqpPU4VhUbq/ekR8CwTRVoRxf3ifTbeIwcONNsJZ2lxFVKDMv1KNvS2zXdrnD+COvR1PQpTZKNlKD3cLCOJNnivgVxkw169BunlKFaV9/B+LQbqOsByY4IVgDB59dl/cjR9TIJV1Lh7CGqUqH/DDPhhZYOPkdLz6m0X7GrzPHsSe6zJwzxvm+5NeNi8U5ABfn7mz7zHJFrZ6+BY6rd7m8kQtcAtwwXzq4n69/vZbP1+pn6/8fsrRmHUhmpYYAAAAASUVORK5CYII="
# img_bytes = base64.b64decode(img_base64)
# print(img_bytes)
# with open("a.png","wb") as f:
#     f.write(img_bytes)
```


### ժҪ�㷨

```pytyhon
from hashlib import md5, sha1, sha256, sha512

# md5_obj = md5()

# ժҪ����
# md5_obj.update("123456".encode())
# e10adc3949ba59abbe56e057f20f883e
# md5_obj.update("yuanlaoshitebieshuai".encode())
# ժҪ�Ľ��
# ʮ�������ַ���
# print(md5_obj.hexdigest())

# �ֽڴ�
# print(md5_obj.digest())


# �ص�
# 1. ���������������һ����ĸ��ͬ������ժҪ�����ȫ��һ��
# 2. �����ͬ��ֵ��һ��μ��㣬���Ҳһ��
# 3. ������ժҪ����������棬����ײ��
# 4. �㷨ȷ�ϣ����ɳ���һ���ǹ̶���
# 5. �ۼ�ժҪ���
# 6. ����
# 7. �����㷨�����㷨����


# ����2

# md5_obj.update("hello".encode())
# md5_obj.update("yuan".encode())

# md5_obj.update("hello yuan".encode())

# print(md5_obj.hexdigest())

# d843cc930aa76f7799bba1780f578439
# d843cc930aa76f7799bba1780f578439


# ����3
# md5_obj = md5(b"12q34nkjsakdfnjksd23423asdkjnaksd")
# md5_obj.update("123456".encode())
# print(md5_obj.hexdigest())


# ����4
# sha256_obj = sha256(b"12q34nkjsakdfnjksd23423asdkjnaksd")
# sha256_obj.update("123456".encode())
# print(sha256_obj.hexdigest())

# 313262ebb5fe39c4fcd3d9b9f7ab983b195af36364d945f86b9f7950cdb4f546

```

- https://curlconverter.com/


### AES �㷨����

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64


# (1) ��������
# AES-128
# 16λ�ֽ�

# key: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
key = "0123456789abcdef".encode()
# iv: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
iv = "abcdefghigklmnop".encode()

aes = AES.new(key, AES.MODE_CBC, iv)

text = "Alex is a stupid monkey!!!"

# aes.encrypt()
# aes.decrypt()
# Data must be padded to 16 byte boundary in CBC mode
data = text.encode()

# ���ķ�ʽ1
# data += (16 - len(data) % 16)*b" "
# ���ķ�ʽ2
data = pad(data, 16)
print(len(data), data)
encrypt_data = aes.encrypt(data)
print("encrypt_data:::", encrypt_data)

# (2) �Լ�������base64����
base64_encrypt_data = base64.b64encode(encrypt_data).decode()
print("base64_encrypt_data",base64_encrypt_data)

```

### AES�㷨����

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

base64_encrypt_data = "Awu9exRUaddGXNuca1rO0QSKUxxhwMvhTwvUswlDAGY="

# (1) base64����

encrypt_data = base64.b64decode(base64_encrypt_data)
print("encrypt_data��", encrypt_data)

# (2) ����
# key: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
key = "0123456789abcdef".encode()
# iv: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
iv = "abcdefghigklmnop".encode()
aes = AES.new(key, AES.MODE_CBC, iv)
data = aes.decrypt(encrypt_data)
print("data:", data)

data = unpad(data, 16).decode()
print("data", data)

```

### ������Կ˽Կ

```python

from Crypto.PublicKey import RSA

# ������Կ
rsakey = RSA.generate(1024)
with open("rsa.public.pem", mode="wb") as f:
    f.write(rsakey.publickey().exportKey())

with open("rsa.private.pem", mode="wb") as f:
    f.write(rsakey.exportKey())
    
```

### RSA�㷨����

```python
import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# (1) �����ݼ���

text = "Alex is a stupid monkey!!!"

with open("rsa.public.pem") as f:
    public_key = f.read()
    print("public_key:", public_key)

# ���ڹ�Կ�����ݼ��ܣ����ݼ��ܣ���Կ���� ����ǩ����˽Կ���ܣ�
# Կ�׶���
rsa_pk = RSA.importKey(public_key)
# ���ڹ�ԿԿ�׵��㷨����
rsa = PKCS1_v1_5.new(rsa_pk)

encrypt_data = rsa.encrypt(text.encode())

print("encrypt_data:::", encrypt_data)

# (2) base64����

base64_encrypt_data = base64.b64encode(encrypt_data).decode()
print(base64_encrypt_data) # cAG+/VdV2Fe/RPakh1s/YSpmqoliHz/USZ2oNd6DoQfpB4Djfom2h7t++ED7UgnSL7KihKmwFZXjaO25Xgufa3PDuay0vJ+tGAAQFo3sV1UUBHsDOn6yiO0NjQBjeNzvbm8olXUs/73h2o9/3qzhkinY28/2+hUb9zlORXY5Tqg=


```

### RSA�㷨����

```python
import base64
from Crypto.PublicKey import RSA

from Crypto.Cipher import PKCS1_v1_5

base64_encrypt_data = "f05yVGDPRq8wpu//mck85con+ob54xNiKMFkW/yrBhdSbXNjGPn3rlc9PevdKrg5My0phPdwXePxgTGezEkETkr+QZrETC5QN6QMT35nCG0vOblQw1mIMYlrRMoRcQCmZ+/N74S0RtVGcvkReh1PoxYI1Txgz9/rbzvK38gklfM="

# (1) base64����

encrypt_data = base64.b64decode(base64_encrypt_data)
print("encrypt_data:::", encrypt_data)

# (2) RSA����


with open("rsa.private.pem") as f:
    private_key = f.read()
    print("private_key:", private_key)

# ���ڹ�Կ�����ݼ��ܣ����ݼ��ܣ���Կ���� ����ǩ����˽Կ���ܣ�
# Կ�׶���
rsa_pk = RSA.importKey(private_key)
# ����˽ԿԿ�׵��㷨����
rsa = PKCS1_v1_5.new(rsa_pk)

data = rsa.decrypt(encrypt_data, None)

print("data:::",data)

```

### JS�ӽ����㷨

```js
// (1) md5ժҪ�㷨

const CryptoJS = require('crypto-js');
// ԭʼ����
const data = '123456';
// ����MD5ժҪ
const md5Digest = CryptoJS.MD5(data).toString();

console.log(md5Digest);


// (2)  AES����

// const CryptoJS = require("crypto-js")

// ��Կ��128λ��16�ֽڣ�
var key = CryptoJS.enc.Utf8.parse('0123456789abcdef');

// ��ʼ��������IV����128λ��16�ֽڣ�
var iv = CryptoJS.enc.Utf8.parse('1234567890abcdef');

// �����ܵ�����
var plaintext = 'Hello, yuan!';

// ����AES-128���ܣ�ʹ��CBCģʽ��PKCS7���
var encrypted = CryptoJS.AES.encrypt(plaintext, key, {
    iv: iv,
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
});

// ��ȡ���ܺ������
var ciphertext = encrypted.toString();

console.log(ciphertext);

```

### ��JS��AES�������ݽ��н���

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

base64_encrypt_data = "qxfU+ELL+4i37LgFRNMwPQ=="

# (1) base64����

encrypt_data = base64.b64decode(base64_encrypt_data)
print("encrypt_data��", encrypt_data)

# (2) ����
# key: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
key = "0123456789abcdef".encode()
# iv: It must be 16 (*AES-128)*, 24 (*AES-192*) or 32 (*AES-256*) bytes long.
iv = "1234567890abcdef".encode()
aes = AES.new(key, AES.MODE_CBC, iv)
data = aes.decrypt(encrypt_data)
print("data:", data)

data = unpad(data, 16).decode()
print("data", data)

```


### rsa�㷨

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jsencrypt/2.3.1/jsencrypt.min.js"></script>
    <script>
        // ������Կ��
        var encrypt = new JSEncrypt();
        var privateKey = encrypt.getPrivateKey();
        var publicKey = encrypt.getPublicKey();

        console.log("Private Key: " + privateKey);
        console.log("Public Key: " + publicKey);

        function encryptData(data) {
            var encrypted;

            var rsaEncrypt = new JSEncrypt();
            rsaEncrypt.setPublicKey(publicKey);

            encrypted = rsaEncrypt.encrypt(data);

            return encrypted;
        }

        // ʹ��˽Կ�������ݽ���
        function decryptData(encryptedData) {
            var decrypted;

            var rsaDecrypt = new JSEncrypt();
            rsaDecrypt.setPrivateKey(privateKey);

            decrypted = rsaDecrypt.decrypt(encryptedData);

            return decrypted;
        }
    </script>
</head>
<body>

</body>
</html>

```


### RSA�㷨����

```python
import base64
from Crypto.PublicKey import RSA

from Crypto.Cipher import PKCS1_v1_5

base64_encrypt_data = 'IOB8BIzkfnbUgi8nsDlkGcYnjCkUVTOn/G+1T2VdVH41avakXUh85+pcx6ZxnuoqvLXbF+LTZ6uYZ8V5gZgBWrDW15xvlO9EKm9cYG8Z20zXaiFVy0zDCdZvAOkQluSB3GGl0QqKSA4l8joDxzsViYZFPTfdzrfifcxtAY7Fyg=='

# (1) base64����

encrypt_data = base64.b64decode(base64_encrypt_data)
print("encrypt_data:::", encrypt_data)

# (2) RSA����

# with open("rsa.private.pem") as f:
#     private_key = f.read()
#     print("private_key:", private_key)

private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIICXQIBAAKBgQCVxb2f5mVyw3AcChGs0RMPyjkMEJl0YqiiEzArFp0Xf/CKDvSH\nFqU9LIKFtH/rN+ZQswVTodOh97o/QbEOYVIvziCQHs/h7DoOXi80k5wyLvjstMX0\nxv/Wqjsu1zOfvGd7Tx4biPipeWIiNd7CIDdb8+HpjI4uuMI9CsbJ2dYZOwIDAQAB\nAoGAMdVfqMqSSsM4lDvNccEHJKPWo2sKhC0nivXzewLFNkJ9mJItTp18UYRz0WUj\ngvJQkd1fElqv/h5dPBrxfKVpILesmUWCatPtvKWzgNKhFTQx8fuLhs710eWTw1+n\n6k1C9YAQPKKHAztQAui66XmbM7/YzcYxVecjfeqdU7QfFZECQQDcjNuky/Hy+mZc\navJDFVXCK1+ueSQmvfwLUweaZ9vQfrHo8m2eZcLiTrlM9oP3smwSdIYsC632HY4g\nec2TBXvFAkEArdiJXdHf4sucykg7kwXLbyMt9gLHcI/8ECFcwTTuhgQJrLr94SOc\nA7nC7CxI5+sg6uIWTf6jsVKD4CSSsc2Q/wJAO8VMzVecJY5o6UjuiPGiQTICB0W7\nX2iDgwooeFcHQnTjgE8bGB9Z9n0BSPNSBnHrSgEcT5mGtrmByBladiq5RQJBAKY6\nO7cK/CH3AVfmU5iUXN5K7CKkq6E0/BdMX02a2Ewqxjl0n1dMXlytnfWHrrqbeGE/\nh4ZSaqEePlzve5kp728CQQC//a/haeKjIAGY8/IimHLQmp8xMqWjJHH0A6L3Prts\n0bbZ5kqsY+DWDBey66+ZVDr5G43WXbRa6VOSOOc424HD\n-----END RSA PRIVATE KEY-----'

# ���ڹ�Կ�����ݼ��ܣ����ݼ��ܣ���Կ���� ����ǩ����˽Կ���ܣ�
# Կ�׶���
rsa_pk = RSA.importKey(private_key)
# ����˽ԿԿ�׵��㷨����
rsa = PKCS1_v1_5.new(rsa_pk)

data = rsa.decrypt(encrypt_data, None)

print("data:::",data)

```

### js��base64

```js
console.log(btoa("hello yuan"))
console.log(btoa("alex ....."))


console.log(atob("YWxleCAuLi4uLg==\n"))
```

### �ļ�����

```python

-- package.json

{
  "dependencies": {
    "crypto-js": "^4.2.0"
  }
}


-- package-lock.json

  {
    "name": "Day19 �����㷨",
    "lockfileVersion": 3,
    "requires": true,
    "packages": {
      "": {
        "dependencies": {
          "crypto-js": "^4.2.0"
        }
      },
      "node_modules/crypto-js": {
        "version": "4.2.0",
        "resolved": "https://registry.npmjs.org/crypto-js/-/crypto-js-4.2.0.tgz",
        "integrity": "sha512-KALDyEYgpY+Rlob/iriUtjV6d5Eq+Y191A5g4UqLAi8CyGP9N1+FdVbkc1SxKc2r4YAYqG8JzO2KGL+AizD70Q=="
      }
    }
  }


-- rsa.private.pem

-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCVxb2f5mVyw3AcChGs0RMPyjkMEJl0YqiiEzArFp0Xf/CKDvSH
FqU9LIKFtH/rN+ZQswVTodOh97o/QbEOYVIvziCQHs/h7DoOXi80k5wyLvjstMX0
xv/Wqjsu1zOfvGd7Tx4biPipeWIiNd7CIDdb8+HpjI4uuMI9CsbJ2dYZOwIDAQAB
AoGAMdVfqMqSSsM4lDvNccEHJKPWo2sKhC0nivXzewLFNkJ9mJItTp18UYRz0WUj
gvJQkd1fElqv/h5dPBrxfKVpILesmUWCatPtvKWzgNKhFTQx8fuLhs710eWTw1+n
6k1C9YAQPKKHAztQAui66XmbM7/YzcYxVecjfeqdU7QfFZECQQDcjNuky/Hy+mZc
avJDFVXCK1+ueSQmvfwLUweaZ9vQfrHo8m2eZcLiTrlM9oP3smwSdIYsC632HY4g
ec2TBXvFAkEArdiJXdHf4sucykg7kwXLbyMt9gLHcI/8ECFcwTTuhgQJrLr94SOc
A7nC7CxI5+sg6uIWTf6jsVKD4CSSsc2Q/wJAO8VMzVecJY5o6UjuiPGiQTICB0W7
X2iDgwooeFcHQnTjgE8bGB9Z9n0BSPNSBnHrSgEcT5mGtrmByBladiq5RQJBAKY6
O7cK/CH3AVfmU5iUXN5K7CKkq6E0/BdMX02a2Ewqxjl0n1dMXlytnfWHrrqbeGE/
h4ZSaqEePlzve5kp728CQQC//a/haeKjIAGY8/IimHLQmp8xMqWjJHH0A6L3Prts
0bbZ5kqsY+DWDBey66+ZVDr5G43WXbRa6VOSOOc424HD
-----END RSA PRIVATE KEY-----

-- rsa.public.pem

-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCkadKyZcN4+EqvWb+IZPdnXqGP
M6OqD65WL9O/u8MVbIvmVaruh8Qj2zvllMiyeEeuuJKot3B6eDBPeL6+OWyDTHIV
wCMutYYdEcAUay14j52EcTS0i8n8APukNRE/97zAEEW6xB/ozPS5gujKpdXHebAv
74wP4tkkp2GeiwOopQIDAQAB
-----END PUBLIC KEY-----

```