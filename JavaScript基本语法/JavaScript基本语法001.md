
### JS的三大块：
1. ECMA标准语法（最重要）
2. DOM
3. BOM

### ECMA标准语法：
1. 解释型语言或者编译型语言
   JS是一个解释型语言，需要解释器，浏览器是解释器
2. 变量
3. 数据类型（基本数据类型，容器类型）
4. 运算符
5. 流程控制语句（分支+循环）
6. 函数

### Js的引入方法：

- <script>可以直接写。
- index.js可以引入。

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        h3 {
            color: rebeccapurple;
            font-style: italic;
        }
    </style>

</head>
<body>


<h3>hello JavaScript!</h3>


<script>
   /* dom = document.getElementsByTagName("h3")[0]
    dom.onclick = function () {
        alert(123)
    }*/
</script>

<!--<script src="index.js"></script>-->

</body>
</html>
```

### Js的变量

```JavaScript

// 单行注释

/*
多行注释
多行注释
多行注释
 */
 
/*// 变量声明

var x
console.log("x:::",x) //默认值：undefined
// 变量赋值
x = 100
console.log("x:::",x)
// 声明并赋值

var y = 200;
console.log("y:::",y)

// 一次性可以声明多个变量
var name="yuan", age=20, job="lecturer";
var a, b, c=3, d, e = 5;
console.log(a,b,d)
console.log(c,e)*/

// 注意事项:
// var x = 10;
// x = 20;
```


### 数据类型

```JavaScript
// (1) 基本数据类型: 字符串 数字 布尔类型

/*var a = "hello yuan"
console.log(typeof a)  // string

var b = 100
var c = 3.14
console.log(typeof b)
console.log(typeof c)
d = true
e = 2 < 1
console.log(typeof d) // boolean
console.log(typeof e) // boolean*/


// (2) 高级(容器)数据了类型： 数组 [] object {}

/*var arr01 = [1, true, "yuan"]
console.log(typeof arr01) // object


// var info = {"name":"yuan","age":18}
var info = {name: "yuan", age: 18}
console.log(info)
console.log(info.name)
console.log(info["name"])
console.log(info.age)
console.log(info["age"])
// info.name = "Yuan"
info["n" + "a" + "m" + "e"] = "Yuan"
console.log(info)
console.log(typeof info)*/


// (3) 两个特殊值:   undefined null


// (4) 类型转换
// JS:弱类型语言

// console.log(1 + "20")

// 将字符串转换成数字

// var x = "123"
// var ret = parseInt(x)
// console.log(ret,typeof ret)

// var y = "123.4"
// var ret2 = parseFloat(y)
// console.log(ret2,typeof ret2)

// var x = "100元元"
// var ret = parseInt(x)
// console.log(ret,typeof ret)


// 将数字转换成字符串

// var a = 100;
// var b = a.toString()
// console.log(b,typeof b)
// var c= [1,2,3].toString()
// console.log(c,typeof c)
// var d= {"name":"yuan"}.toString()
// console.log(d,typeof d)
// console.log(100+"")
```

### 运算符

```JavaScript
// （1） 科学运算符
//  + - * / %

// var a = 10
// a = a + 1
// console.log(a)
// a += 1
// console.log(a)

// var ret01 = a++  // a = a + 1
// console.log(a)
// console.log(ret01)

// var ret02 = ++a // a = a + 1
// console.log(a)
// console.log(ret02)

// （2）比较运算符
// > <   <=  >= === !==
// console.log(2=="2")
// console.log(2==="2")

// （3） 赋值运算符  ++ --
// += -= *= /=  ++


// （4）逻辑运算符：&&  || !, Python中的and, or, not
// console.log(true && false)
// console.log(false && true)
// console.log(false && false)
// console.log(true && true)

// console.log(true || false)
// console.log(false || true)
// console.log(false || false)
// console.log(true || true)

// console.log(!true)
// console.log(!2>1)


// 短路运算
// console.log(false && 0)
// console.log(true && true)
// console.log(true && 1000)
// console.log(true || -1000)
// console.log(false || "hello")

// 案例1
/*var islogin = true

function show(){
    console.log("展示个人信息")
}*/

/*if (islogin===true){
    show()
}*/

// islogin && show()

// 案例2
/*
function login(){
    return true
}
function show(){
    console.log("展示个人信息")
}

login() && show()*/

// （5）逗号运算符 ,

// var x = (1, 2, 3, 4, 5, 6)
// console.log(x)

/*function test1() {
    console.log("1")
    return 1
}

function test2() {
    console.log("2")
    return 2
}

function test3() {
    console.log("3")
    return 3
}

var ret = (test1(), test2(), test3())
console.log(ret)*/

// a = (1,2,3,4)
// console.log(a)


/*function test1() {
    console.log("1")
    return 1
}

function test2() {
    console.log("2")
    return 2
}

function test3() {
    console.log("3")
    return 3
}

var ret = (a = test1(), b = a + 1, c = b * a)
console.log(ret)*/


// (6) 三目运算：条件? 成立: 不成立
// 方案1
/*
isLogin = true
var user
if (isLogin === true) {
    user = "yuan"
} else {
    user = "匿名用户"
}
console.log(user)*/

// 方案2
// isLogin = false
// var user = isLogin?"yuan":"匿名用户"
// console.log(user)


// 方案3
/*var x = 1000
var y = 200

if (x>y){
    console.log("x大于y")
}else {
    console.log("x小于y")
}*/

var x = 100
var y = 200

var s = x > y ? "x大于y" : "x小于y"

console.log(s)

```

### dom

```JavaScript
dom = document.getElementsByTagName("h3")[0]
dom.onclick = function () {
    alert(123)
}


### 流程控制

```JavaScript
// 流程控制
/*
Python：

if 表达式:
    语句块
else:
    语句块
语句A


if 表达式1:
    语句块
elif 表达式2:
    语句块
elif 表达式2:
    语句块
elif 表达式2:
    语句块

JS：

if (表达式){
   语句块
}else{
   语句块
}



if (表达式){
   语句块
}else if (表达式){
   语句块
}else if (表达式){
   语句块
}else if (表达式){
   语句块
}else{

}
 */


// （1）双分支
// var age = 13
// if (age > 18) {
//     console.log("播放成人电影！")
// } else {
//     console.log("播放未成年电影")
// }


（2）多分支
// var score = 95;
// if (score >= 90) {
//     console.log("A");
// } else if (score >= 80) {
//     console.log("B");
// } else if (score >= 70) {
//     console.log("C");
// } else if (score >= 60) {
//     console.log("D");
// } else {
//     console.log("E");
// }


（3）switch多分支

var week = 14;
switch(week){
    case 1:
        console.log("星期一");
        break;
    case 2:
        console.log("星期二");
        break;
    case 3: // 某一个case匹配成功. 那么后面的case就不判断了, 直接被执行.
        console.log("星期三");
        break;
    case 4:
        console.log("星期四");
        break;
    case 5:
        console.log("星期五");
        break;
    case 6:
        console.log("星期六");
        break;
    case 7:
        console.log("星期天");
        break;
    default:
        console.log("啥也不是!");
        break;
}
```


### 字符串对象

```JavaScript

var s = "hello world"

console.log(s.toUpperCase())
console.log(s.toLowerCase())
console.log(s.slice(1, 4))
console.log(s.slice(1))
console.log(s.slice(1, -1))
console.log(s.split(" "))
var s1 = "   yuan         "
console.log(s1.length)
console.log(s1.trim(" "))
console.log(s1.trim(" ").length)
var s2 = "hello yuan"
console.log(s2.indexOf("a"))
console.log(s2.indexOf("l"))
console.log(s2.replace("yuan","rain"))
console.log(s2.startsWith("hel"))
console.log(s2.startsWith(" hel"))
console.log(s2.startsWith("h"))
console.log(s2.startsWith("el"))

```

### 数组对象

```JavaScript

gfArr = ["高圆圆", "刘亦菲", "赵丽颖"]
console.log(gfArr)
console.log(gfArr.length)
//一、增删：push pop  unshift  shift
var ret = gfArr.push("范冰冰")
console.log("ret:::",ret)
console.log(gfArr)
gfArr.pop()
console.log(gfArr)
//按首位进行操作
gfArr.unshift("林志玲")
console.log(gfArr)
gfArr.shift()
console.log(gfArr)
//二、修改
gfArr = ["高圆圆", "刘亦菲", "赵丽颖"]
console.log(gfArr)
gfArr[0] = "高OO"
console.log(gfArr)
//三、查
console.log(gfArr.slice(0,2))


gfArr = ["高圆圆", "刘亦菲", "赵丽颖", "范冰冰", "林志玲"]
//splice 删除
gfArr.splice(1,2)
console.log(gfArr)
//splice 插入元素
gfArr.splice(1, 0, "apple")
console.log(gfArr)

//splice 替换元素（先删除再添加）
gfArr.splice(1,2,"lyf","zly")
console.log(gfArr)

//数组循环

gfArr = ["高圆圆", "刘亦菲", "赵丽颖", "范冰冰", "林志玲"]

for(var i=0;i<gfArr.length;i++){
    console.log(i,gfArr[i])
}

```

###  JS的循环语句。

```JavaScript
// 条件循环

/*

while (表达式){
   循环语句
}

for (循环三要素){
   循环语句
}

for (初始语句;判断表达式;步进语句){
    循环语句
}

 */

// while循环
/*var n = 1 // 循环的初始语句
while (n <= 100) { // 判断表达式
    console.log(n)
    n++ // 步进语句
}*/

/*for (var n = 1;n <= 100;n++){
    // console.log("yuan")
    console.log(n)
}*/

/*var arr = [111, 222, 333, 444, 555]
for (var x in arr) { // 此时拿到的是数组的索引(key)
    console.log(x,arr[x]);
}*/

/*var arr = [111, 222, 333, 444, 555]
for (var x of arr) { // 此时拿到的是数组的索引(key)
    console.log(x);
}*/

/*while (true){
    console.log("hello")
}*/


// break
// 寻找88
for (var n = 1; n <= 100; n++) {
    // console.log("yuan")
    // console.log(n)
    console.log(n)
    if (n === 88) {
        break
    }
}

// continue

/*for (var n = 1; n <= 100; n++) {

    if (n === 88) {
        continue
    }
    console.log(n)
}*/

```

### JS的object对象

```JavaScript
var info = {
    name: "yuan",
    age: 18,
    gender: "male",
    gfArr: ["高圆圆", "刘亦菲", "赵丽颖", "范冰冰", "林志玲"]
}
// 获取属性值
console.log(info["name"])
console.log(info.name)
info["age"] = 19
console.log(info)

info.gfArr[4] = "lzl"
console.log(info)


// 序列化和反序列化
// JSON.stringify()
// JSON.parse()
```

### 常见对象

```JavaScript
// var timer =  new Date().getTime()
// console.log(timer) // 1710855697826 ms


// Math对象
/*// 四舍五入
console.log(Math.round(3.5415926))
// 向上取整
console.log(Math.ceil(3.1))
console.log(Math.ceil(3.5))
// 向下取整
console.log(Math.floor(3.1))
console.log(Math.floor(3.5))

console.log(Math.pow(3,5))*/
// 0-1的随机浮点型值
// console.log(Math.random())
// console.log(Math.round(Math.random()*5))

```

### 函数基础

```JavaScript
/*// 调用
foo()

// 函数声明
function foo(x, y) {
    // 标识语句体
    console.log("foo功能")
}*/


/*function add(x, y) {
    console.log(x + y)
}

add(1, 2)
add(1, 2, 3)
add(1,)*/


/*function add(x, y, z) {
    console.log(x + y + z)
}*/
//arguments
/*function add2() {
    // 函数中 arguments
    // console.log(arguments)

    let ret = 0
    for (let i = 0; i < arguments.length; i++) {
        ret += arguments[i]
    }

    return ret
}

console.log(add2(1, 2, 3, 4, 5, 6,7,1000))*/
```

### 函数作用域

```JavaScript
/*var x = 1
if (2>1){
    var x = 100
}
console.log(x)*/


/*
var x = 100

function foo() {
    // var x = 200
    var x = 200 // 修改全局的x
    console.log("foo的x：", x)
}

function bar() {
    var foo = 100
    // var x = 200
    // var y = 200 // 修改全局的x
    // console.log("bar的y：", y)
    foo()
}
*/

// foo()
// bar()
// console.log("全局x：", x)
// console.log("全局y：", y)


//  函数一等公民： 函数享受和其他数据（数字，字符串等）一样的权利
function test() {
    console.log("test....")
    return 10000
}

/*var a = test
var b = a
b()*/

/*var a = test()
console.log(a)
a()*/


/*function test2(x, y) {
    return x + y
}

// test2(1, 2,)
var a = 100
var b = 200
test2(a, b)*/

```

### 匿名函数

```JavaScript
/*function foo(){

}*/

// 匿名函数
/*
var x = function (x, y) {
    return x + y
}

console.log(x(1, 2))
console.log(x(1, 3))*/


// console.log(1+2)
// 自执行函数
/*(function (x, y) {
    return x + y
})(1, 2)*/

// 函数中声明函数


function outer() {

    /* function inner(){
         console.log("inner")
     }
     return inner*/

    return function () {
        console.log("inner")
    }

}

// 方式1
// var x = outer()
// x()
// 方式2
// outer()()

```


### 高阶函数


```JavaScript
// 高阶函数： 函数以函数作为参数或者函数作为返回值称之为高阶函数


//  函数一等公民： 函数享受和其他数据（数字，字符串等）一样的权利，可以变量传递，可以作为参数，可以作为返回值

/*
function test01(x){
    console.log(x)
}

var a = 100
var b = [1,2,3]

function foo(){
    console.log("foo功能")
}
test01(a)
test01(b)
test01(foo)*/

// 版本1
/*function foo() {
    console.log("foo功能")
}

function bar() {
    console.log("bar功能")
}*/

/*function dec(func) {
    console.log("start")
    func()
    console.log("end")
}*/

// foo()
// 调用foo
// dec(foo)
// dec(bar)


// 前端业务线：
// foo()
// foo()
// foo()
// foo()
// foo()
// foo()


// 版本2
function foo() {
    console.log("foo功能")
}

function bar() {
    console.log("bar功能")
}


function dec(func) {
    console.log("start")
    func()  // func: foo
    console.log("end")
}


function xxx(func) {

    function dec() {
        console.log("start")
        func()  // func: foo
        console.log("end")
    }
    return dec

}
foo = xxx(foo)
foo()
foo()


// foo()
// foo()
// foo()
// foo()
// foo()
// foo()


// 前端业务线：
// foo()
// foo()
// foo()
// foo()
// foo()
// foo()


bar = xxx(bar)
bar()

```

### 闭包函数

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <script>

        function getCounter() {
            // 计数器

            var aaa = "123"
            var count = 0
            function counter() {
                count++  // count = count+1
                console.log(count)
                return count
            }
            // counter()
            return counter
        }
        counter1 = getCounter()
        counter1()
        counter1()
        counter1()
        counter2 = getCounter()
        counter2()
        counter2()
        counter2()


    </script>
    <script>
        var count = 1000
    </script>
    <script>
        // js代码3
    </script>
    <script>
        // js代码4
    </script>
</head>
<body>

<button onclick="counter()">click</button>

</body>
</html>
```













