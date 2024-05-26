# PyQt

## 介绍

PyQt是一个用于创建桌面应用程序的Python绑定库。它提供了对Qt应用程序框架的完整访问，使开发者能够使用Python编写高性能、跨平台的图形用户界面(GUI)应用程序。

PyQt可以在不同操作系统（如Windows、Mac和Linux）上运行，使开发者能够轻松地编写一次代码，然后在多个平台上部署和运行。

Qt是一个功能强大的C++跨平台应用程序框架，它提供了大量用于创建图形用户界面的功能和工具。PyQt则是Qt框架的Python绑定库，可以让Python开发者使用Python语言调用Qt的功能，以开发具有丰富交互和视觉效果的桌面应用程序。

总而言之，PyQt使得Python开发者能够利用Qt框架的强大功能和跨平台特性，快速开发出高质量的桌面应用程序。它被广泛应用于各种领域，如科学计算、数据可视化、企业应用、游戏开发等。

## 环境安装

- 安装pyqt5
  - pip install pyqt5 -i https://pypi.tuna.tsinghua.edu.cn/simple
- 测试安装是否成功：

```python
# 如果执行成功，没有任何错误提示，则表明环境搭建成功
from PyQt5 import QtWidgets

# 当然也可以查看PyQt版本
from PyQt5.QtCore import *
print(QT_VERSION_STR)
```

## 相关操作

### 相关组件

#### QWidget主窗口组件

```python
from PyQt5.QtWidgets import QApplication,QWidget
#1.创建一个qt的应用程序对象
app = QApplication([])
#2.创建一个窗口对象
w = QWidget()
#设置窗口标题
w.setWindowTitle('第一个PyQt程序')
#3.展示窗口
w.show()
#4.程序进入循环等待状态，直到手动关闭窗口
app.exec()
```

#### 按钮组件

按钮对应的控件名称为 ` QPushButton`,位于 `PyQt5.QtWidgets` 里面

```python
from PyQt5.QtWidgets import QApplication,QWidget,QPushButton
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.setWindowTitle('按钮组件')
    #在窗口中添加按钮组件
    btn = QPushButton('我是一个按钮')
    #将按钮显示在窗口里
    btn.setParent(w)
    w.show()
    app.exec()
```

#### 标签组件

标签控件名称为 ` QLabel` ， 位于 `PyQt5.QtWidgets` 里面

标签控件仅仅作为标识显示而已，类似输入内容前的一段标签提示（账号 、密码）

```python
from PyQt5.QtWidgets import QApplication,QWidget,QLabel
app = QApplication([])
w = QWidget()
w.setWindowTitle('标签组件')

label_username = QLabel('账号:',w)
#设置组件大小和位置
#参数： x, y , w, h
label_username.setGeometry(20,20,30,30)
label_password = QLabel('密码:',w)
#设置组件大小和位置
label_password.setGeometry(20,60,30,30)

w.show()
app.exec()
```

#### 输入框

输入框的控件名称为 `QLineEdit`， 位于 `PyQt5.QtWidgets` 里面

setGeometry调整组件位置和大小

```python
from PyQt5.QtWidgets import QApplication,QWidget,QLabel,QLineEdit,QPushButton
app = QApplication([])
w = QWidget()
w.setWindowTitle('标签组件')

label_username = QLabel('账号:',w)
label_username.setGeometry(20,20,30,30)

#输入框标签
username = QLineEdit(w)
#设置默认填充显示内容
username.setPlaceholderText('请输入账号')
#设置组件位置和大小
username.setGeometry(50,20,200,20)

label_password = QLabel('密码:',w)
label_password.setGeometry(20,60,30,30)
password = QLineEdit(w)
password.setPlaceholderText('请输入密码')
password.setGeometry(50,65,200,20)

btn = QPushButton('登录',w)
btn.setGeometry(70,100,70,30)

w.show()
app.exec()
```

#### 表格

表格组件：QTableWidget

表格元素组件：QTableWidgetItem

```python
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem

if __name__ == "__main__":
    app = QApplication([])

    # 创建一个主窗口对象
    mainWindow = QMainWindow()
    mainWindow.setWindowTitle("Table Widget Example")
    # 创建一个表格控件
    tableWidget = QTableWidget(mainWindow)
    # 设置表格的行数和列数
    tableWidget.setRowCount(2)
    tableWidget.setColumnCount(2)
    # 设置表格的水平和垂直表头标签
    tableWidget.setHorizontalHeaderLabels(["Column 1", "Column 2"])
    tableWidget.setVerticalHeaderLabels(["Row 1", "Row 2"])
    # 设置表格的内容
    tableWidget.setItem(0, 0, QTableWidgetItem("Item 1"))
    tableWidget.setItem(0, 1, QTableWidgetItem("Item 2"))
    tableWidget.setItem(1, 0, QTableWidgetItem("Item 4"))
    tableWidget.setItem(1, 1, QTableWidgetItem("Item 5"))


    # 将表格控件添加到主窗口中
    mainWindow.setCentralWidget(tableWidget)
    # 显示主窗口
    mainWindow.show()

    app.exec_()

```



#### 调整窗口大小

resize调整窗口大小

```python
from PyQt5.QtWidgets import QApplication,QWidget
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.setWindowTitle('设置窗口大小')
    
    #设置窗口大小
    w.resize(300,300)
    
    w.show()
    app.exec()
```

## 打包

- 环境安装：

  - pip install pyInstaller
  - pip install auto-py-to-exe

- 编译生成exe文件

  - 命令行进入桌面文件夹，运行命令行

  ```
  pyinstaller -F -w main.py
  ```

- 生成的dist文件里面含打包文件，点击运行

## 布局

在Qt里面布局分为3个大类 ：

- QBoxLayout
- QGridLayout
- QFormLayout

### QBoxLayout

直译为：盒子布局

一般使用它的两个工具类`QHBoxLayout` 和 `QVBoxLayout` 负责水平和垂直布局

- 垂直布局示例QVBoxLayout：
  - layout.addStretch(n):设置被布局的组件间的空间距离


```python
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QPushButton
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.setWindowTitle('垂直布局')
    w.resize(300,300)

    btn1 = QPushButton("按钮1")
    btn2 = QPushButton("按钮2")
    btn3 = QPushButton("按钮3")

    #创建垂直布局工具且将组建添加到布局工具中
    layout = QVBoxLayout()
    layout.addWidget(btn1)
    #设置被布局的组件间的空间距离
    layout.addStretch(1)
    layout.addWidget(btn2)
    layout.addStretch(2)
    layout.addWidget(btn3)
    layout.addStretch(3)
    #将布局工具作用在窗口上
    w.setLayout(layout)

    w.show()
    app.exec()
```

- 水平布局示例QHBoxLayout+单选按钮QRadioButton：

```python
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QRadioButton
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.setWindowTitle('单选按钮')
    w.resize(500,500)

    #创建单选按钮
    # 创建单选按钮
    radio_btn1 = QRadioButton("选项1")
    #默认选中第一个按钮
    radio_btn1.setChecked(True)
    radio_btn2 = QRadioButton("选项2")
    radio_btn3 = QRadioButton("选项3")
    #创建水平布局工具将单选按钮添加到布局工具中
    layout = QHBoxLayout()
    layout.addWidget(radio_btn1)
    layout.addWidget(radio_btn2)
    layout.addWidget(radio_btn3)
    #将布局工具作用在窗口上
    w.setLayout(layout)

    w.show()
    app.exec()
```

- 水平和垂直布局联合嵌套使用+多选按钮QCheckBox+QGroupBox分组框
  - 思路：
    - 创建主布局工具对象（垂直布局）
    - 创建QGroupBox('title')组
    - 创建组内组件
    - 创建组内布局工具
    - 将组内组件添加到组内布局工具中
    - 将组内布局工具作用/设置在QGroupBox组中
    - 将多个QGroupBox组添加在主布局工具中
    - 将主布局工具设置在主窗口中
  - 将不同组件何其对应的布局作用在一个QGroupBox组中，然后将多个QGroupBox组作用在一个指定的主布局工具中，最后将主布局工具显示作用在主窗体上。

```python
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QVBoxLayout,QRadioButton,QCheckBox,QLabel,QGroupBox
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.resize(500,500)
    #创建用于布局两个布局工具的布局工具
    main_layout = QVBoxLayout()

    #创建第一个分组框
    group_1 = QGroupBox('性别')
    #创建单选按钮(性别)
    label = QLabel('性别:')
    male = QRadioButton("男")
    female = QRadioButton("女")
    #创建水平布局工具将单选按钮添加到布局工具中
    layout_h = QHBoxLayout()
    layout_h.addWidget(label)
    layout_h.addWidget(male)
    layout_h.addWidget(female)
    #将布局工具作用在分组框上
    group_1.setLayout(layout_h)

    # 创建第二个分组框
    group_2 = QGroupBox('爱好')
    #创建多选按钮,作用在垂直布局中
    label = QLabel('爱好：')
    # 创建多选按钮
    h1 = QCheckBox("运动")
    h2 = QCheckBox("音乐")
    h3 = QCheckBox("读书")
    # 将多选按钮添加到布局中
    layout_v = QVBoxLayout()
    layout_v.addWidget(h1)
    layout_v.addWidget(h2)
    layout_v.addWidget(h3)
    group_2.setLayout(layout_v)

    #将两个分组框添加在主布局工具中
    main_layout.addWidget(group_1)
    main_layout.addWidget(group_2)

    #将主布局工具显示在主窗口上
    w.setLayout(main_layout)
    w.show()
    app.exec()
```

### QGridLayout

网格布局，有的人称之为九宫格布局

```python
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QGridLayout
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    # 准备数据
    data = {
        0: ["7", "8", "9", "+", "("],
        1: ["4", "5", "6", "-", ")"],
        2: ["1", "2", "3", "*", "<-"],
        3: ["0", ".", "=", "/", "C"]
    }
    # 主垂直布局工具
    layout = QVBoxLayout()

    # 输入框
    edit = QLineEdit()
    edit.setPlaceholderText("请输入内容")
    # 把输入框添加到垂直布局中
    layout.addWidget(edit)

    # 网格布局（也需要添加到垂直布局中）
    grid = QGridLayout()
    # 循环创建追加进去
    for line_number, line_data in data.items():
        # 此时line_number是第几行，line_data是当前行的数据
        for col_number, number in enumerate(line_data):
            # 此时col_number是第几列，number是要显示的符号
            #按钮
            btn = QPushButton(number)
            #指定网格布局的组件和行列号
            grid.addWidget(btn, line_number, col_number)

    # 把网格布局追加到容器中
    layout.addLayout(grid)
    # 将主布局显示添加在主窗口上
    w.setLayout(layout)
    w.show()
    app.exec()
```

### QFormLayout

一般适用于提交数据**form表单**。比如： 登录，注册类似的场景

实现步骤：

- 创建表单布局工具
- 创建对应的组件
- 使用表单布局工具调用addRow将组建添加到表单布局中
- 将表单布局设置到主窗口中

```python
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QApplication, QWidget
from PyQt5.QtCore import Qt

if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    #禁止改变窗口大小
    w.setFixedSize(500,350)

    # 表单布局容器
    form_layout = QFormLayout()
    # 创建1个输入框
    edit = QLineEdit()
    edit.setPlaceholderText("请输入账号")
    #将输入框添加到表单布局容器中
    form_layout.addRow("账号：", edit)

    # 创建另外1个输入框
    edit2 = QLineEdit()
    edit2.setPlaceholderText("请输入密码")
    # 将输入框添加到表单布局容器中
    form_layout.addRow("密码：", edit2)

    # 按钮
    login_btn = QPushButton("登录")
    # 指定登录按钮大小固定
    login_btn.setFixedSize(100, 30)

    form_layout.addRow('',login_btn)

    # 主布局容器添加显示到主窗口中
    w.setLayout(form_layout)
    w.show()
    app.exec()
```

## 窗口

在Qt中，生成窗口有三种方式： `QWidget` | `QMainWindow` | `QDialog`

1. QWidget

控件和窗口的父类 ，自由度高（什么都东西都没有），没有划分菜单、工具栏、状态栏、主窗口 等区域

2. QMainWindow是` QWidget`的子类，包含菜单栏，工具栏，状态栏，标题栏等，中间部分则为主窗口区域
2. QDialog对话框窗口

### QMainWindow

- 创建QMainWindow主窗口w
- 基于主窗口创建菜单栏工具w.menuBar()
- 基于菜单栏工具调用addMenu('title')添加菜单选项
- 通过addAction()添加菜单子选项

```python
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
if __name__ == '__main__':
    app = QApplication([])
    w = QMainWindow()
    #创建菜单栏工具
    menu = w.menuBar()
    #mac专加，win不用
    # 如果是Mac的话，菜单栏不会在Window中显示而是屏幕顶部系统菜单栏位置，下面这一行代码使得Mac也按照Windows的那种方式在Window中显示Menu
    menu.setNativeMenuBar(False)
    #添加菜单选项
    file_menu = menu.addMenu('文件')
    #添加子选项
    file_menu.addAction('新建')
    file_menu.addAction('打开')
    file_menu.addAction('保存')

    # 添加菜单选项
    edit_menu = menu.addMenu('编辑')
    # 添加子选项
    edit_menu.addAction('复制')
    edit_menu.addAction('粘贴')
    edit_menu.addAction('剪切')

    w.show()
    app.exec()
```

### QDialog

对话框一般不应该作为主窗口的存在，而是通过点击操作弹出，起到提示作用.

```python
from PyQt5.QtWidgets import QDialog, QPushButton, QApplication,QLabel
if __name__ == '__main__':
    app = QApplication([])
    w = QDialog()
    w.setWindowTitle('我是对话框')

    label = QLabel('警告！报错！',w)
    w.show()
    app.exec()
```

## 信号与槽

### 信号

其实就是事件（按钮点击 、内容发生改变 、窗口的关闭事件） 或者是状态 （check选中）

当程序触发了某种状态或者发生了某种事件（比如：按钮被点击了, 内容改变等等），那么即可发射出来一个`信号`。

### 槽

若想捕获这个信号，然后执行相应的逻辑代码，那么就需要使用到 `槽` ， `槽`实际上是一个函数， 当`信号`发射出来后，会执行与之绑定的`槽`函数

### 信号与槽链接

为了能够实现，当点击某个按钮时执行某个逻辑，需要把具体的`信号`和具体的`槽`函数绑定到一起.

操作大体流程如下：

```
组件.信号.connect(槽函数)
```

### 具体操作

##### 校验用户密码是否正确

```python
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton,QLabel,QVBoxLayout,QLineEdit,QFormLayout

if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    #主布局工具
    layout = QVBoxLayout()
    #表单布局
    form = QFormLayout()
    user = QLineEdit()
    pwd = QLineEdit()
    form.addRow('账号:',user)
    form.addRow('密码:',pwd)
    layout.addLayout(form)

    btn = QPushButton('登录')
    layout.addWidget(btn)

    label = QLabel()
    #点击按钮获取账号密码数据
    def get_text():
        #获取账号密码数据
        user_text = user.text()
        pwd_text = pwd.text()
        # print(user_text,pwd_text)
        if user_text == '123' and pwd_text == '456':
            label.setText('正确')
        else:
            label.setText('错误')
        layout.addWidget(label)

    btn.clicked.connect(get_text)
    w.setLayout(layout)
    w.show()
    app.exec()
```

##### 文件选择对话框

```python
from PyQt5.QtWidgets import *
app = QApplication([])
w = QWidget()
def openFile():
    #参数1：指定文件对话框的父窗口
    #参数2：文件对话框的标题
    #参数3：文件对话框打开时显示的默认目录
    #参数4：过滤器，用于限制用户可以选择的文件类型。过滤器是一个字符串，可以包含多个文件类型，每个文件类型之间使用双分号";;"分隔。例如，"Text Files (.txt);;All Files ()"表示只允许选择扩展名为txt的文本文件，或者选择任意类型的文件。
    file_dialog = QFileDialog()
    file, _ = file_dialog.getOpenFileName(w,"Open File", "", "All Files (*)")
    if file:
        print(file)

button = QPushButton("Open File")
button.setParent(w)
button.clicked.connect(openFile)
button.setGeometry(150, 150, 100, 30)

w.show()
app.exec()
```

##### 文件夹选择

```python
from PyQt5.QtWidgets import *
app = QApplication([])
w = QWidget()
def openFile():
    file_dialog = QFileDialog()
    folder_path = file_dialog.getExistingDirectory(w, "选择文件夹", "/")
    print(folder_path)

button = QPushButton("Open Folder")
button.setParent(w)
button.clicked.connect(openFile)
button.setGeometry(150, 150, 100, 30)

w.show()
app.exec()
```

##### 下拉框

- 创建下拉框 QComboBox()
- 添加选项addItem('xxx')

```python
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QComboBox

def on_combobox_changed(text):
    label.setText("你选择了：" + text)
    
if __name__ == '__main__':
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("下拉框示例")

    layout = QVBoxLayout(window)

    label = QLabel("请选择一个选项")
    layout.addWidget(label)

    combobox = QComboBox()
    combobox.addItem("选项1")
    combobox.addItem("选项2")
    combobox.addItem("选项3")
    layout.addWidget(combobox)
    #下拉框选项变化信号
    combobox.currentTextChanged.connect(on_combobox_changed)

    window.show()
    app.exec()
```

##### 单选和多选

```python
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QVBoxLayout,QRadioButton,QCheckBox,QLabel,QGroupBox
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    w.resize(500,500)
    #创建用于布局两个布局工具的布局工具
    main_layout = QVBoxLayout()

    #创建第一个分组框
    group_1 = QGroupBox('性别')
    #创建单选按钮(性别)
    label = QLabel('性别:')
    male = QRadioButton("男")
    female = QRadioButton("女")
    #创建水平布局工具将单选按钮添加到布局工具中
    layout_h = QHBoxLayout()
    layout_h.addWidget(label)
    layout_h.addWidget(male)
    layout_h.addWidget(female)
    #将布局工具作用在分组框上
    group_1.setLayout(layout_h)

    # 创建第二个分组框
    group_2 = QGroupBox('爱好')
    #创建多选按钮,作用在垂直布局中
    label = QLabel('爱好：')
    # 创建多选按钮
    h1 = QCheckBox("运动")
    h2 = QCheckBox("音乐")
    h3 = QCheckBox("读书")
    # 将多选按钮添加到布局中
    layout_v = QVBoxLayout()
    layout_v.addWidget(h1)
    layout_v.addWidget(h2)
    layout_v.addWidget(h3)
    group_2.setLayout(layout_v)

    #将两个分组框添加在主布局工具中
    main_layout.addWidget(group_1)
    main_layout.addWidget(group_2)
    # 创建标签用于显示状态信息
    label_msg = QLabel("")
    main_layout.addWidget(label_msg)
    #将主布局工具显示在主窗口上
    w.setLayout(main_layout)

    #信号与槽(单选按钮)
    def male_func():
        label_msg.setText('单选按钮被选中:'+male.text())
    def female_func():
        label_msg.setText('单选按钮被选中:'+female.text())
    
    male.toggled.connect(male_func)
    female.toggled.connect(female_func)

    # 信号与槽(多选按钮)
    def h1_func():
        label_msg.setText('多选按钮被选中:'+h1.text())
    def h2_func():
        label_msg.setText('多选按钮被选中:'+h2.text())
    def h3_func():
        label_msg.setText('多选按钮被选中:'+h3.text())
    
    h1.stateChanged.connect(h1_func)
    h2.stateChanged.connect(h2_func)
    h3.stateChanged.connect(h3_func)
    w.show()
    app.exec()
```

##### 表格控件

- cellClicked信号：当用户点击一个单元格时触发

```python
from PyQt5.QtWidgets import *

if __name__ == "__main__":
    app = QApplication([])

    # 创建一个主窗口对象
    mainWindow = QWidget()
    mainWindow.setWindowTitle("Table Widget Example")
    # 创建一个表格控件
    tableWidget = QTableWidget(mainWindow)
    # 设置表格的行数和列数
    tableWidget.setRowCount(2)
    tableWidget.setColumnCount(2)
    # 设置表格的水平和垂直表头标签
    tableWidget.setHorizontalHeaderLabels(["Column 1", "Column 2"])
    tableWidget.setVerticalHeaderLabels(["Row 1", "Row 2"])
    # 设置表格的内容
    tableWidget.setItem(0, 0, QTableWidgetItem("Item 1"))
    tableWidget.setItem(0, 1, QTableWidgetItem("Item 2"))
    tableWidget.setItem(1, 0, QTableWidgetItem("Item 4"))
    tableWidget.setItem(1, 1, QTableWidgetItem("Item 5"))



    # 连接cellClicked信号与handleCellClick槽
    def handleCellClick(row,col):
        print("Cell Clicked: ", row, col)
    tableWidget.cellClicked.connect(handleCellClick)

    # 显示主窗口
    mainWindow.show()

    app.exec_()
```

- itemChanged信号：当单元格的内容发生改变时触发。

```python
from PyQt5.QtWidgets import *

if __name__ == "__main__":
    app = QApplication([])

    # 创建一个主窗口对象
    mainWindow = QMainWindow()
    mainWindow.setWindowTitle("Table Widget Example")
    # 创建一个表格控件
    tableWidget = QTableWidget(mainWindow)
    # 设置表格的行数和列数
    tableWidget.setRowCount(2)
    tableWidget.setColumnCount(2)
    # 设置表格的水平和垂直表头标签
    tableWidget.setHorizontalHeaderLabels(["Column 1", "Column 2"])
    tableWidget.setVerticalHeaderLabels(["Row 1", "Row 2"])
    # 设置表格的内容
    tableWidget.setItem(0, 0, QTableWidgetItem("Item 1"))
    tableWidget.setItem(0, 1, QTableWidgetItem("Item 2"))
    tableWidget.setItem(1, 0, QTableWidgetItem("Item 4"))
    tableWidget.setItem(1, 1, QTableWidgetItem("Item 5"))

    # 将表格控件添加到主窗口中
    mainWindow.setCentralWidget(tableWidget)

    # 连接cellClicked信号与handleCellClick槽
    def handleItemChanged(item):
        row = item.row()
        col = item.column()
        text = item.text()
        print("Item Changed: ", row, col, text)
    tableWidget.itemChanged.connect(handleItemChanged)


    # 显示主窗口
    mainWindow.show()

    app.exec_()

```

##### 将excel文件数据加载到表格组件中

```python
from PyQt5.QtWidgets import *
import pandas as pd
def selectFile():
    file_dialog = QFileDialog()
    file, _ = file_dialog.getOpenFileName(w, "Open File", "", "All Files (*)")
    #file就是选中的文件路径
    df = pd.read_excel(file)
    row_count,col_count = df.shape
    #设置表格的行和列数
    table.setRowCount(row_count)
    table.setColumnCount(col_count)
		#将df表格中的数据写入到table中
    for row in range(row_count):
        for col in range(col_count):
            value = df.iloc[row,col]
            table.setItem(row, col, QTableWidgetItem(value))

#1.创建一个qt的应用程序对象
app = QApplication([])
#2.创建一个窗口对象
w = QWidget()

layout = QVBoxLayout()
btn = QPushButton('选择要加载的文件')
btn.clicked.connect(selectFile)

table = QTableWidget()

layout.addWidget(btn)
layout.addWidget(table)

w.setLayout(layout)

#3.展示窗口
w.show()
#4.程序进入循环等待状态，直到手动关闭窗口
app.exec()
```



## 综合项目案例

文件查找功能和文件数据批量修改

- 页面搭建

```python
from PyQt5.QtWidgets import *
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    # 设置窗口大小
    w.resize(800, 600)
    #创建主布局对象（垂直布局）:用于布局表单布局容器和table表格
    layout = QVBoxLayout()

    #创建表单布局工具
    form = QFormLayout()

    #文件查找范围指定
    dir_path = QLineEdit()
    dir_path.setPlaceholderText('先确定查找文件的范围')
    dir_path.setFixedSize(250, 30)
    form.addRow('范围:', dir_path)

    btn = QPushButton('选择查找范围')
    form.addRow('', btn)

    #查找文件/文件夹
    fileName = QLineEdit()
    fileName.setPlaceholderText('请输入要查找文件/文件夹的名字')
    fileName.setFixedSize(250, 30)
    form.addRow('文件名:', fileName)

    btn_1 = QPushButton('查找')
    form.addRow('', btn_1)

    showMsg = QLabel("")
    form.addRow('', showMsg)

    #文件数据修改
    filePathEdit = QLineEdit()
    filePathEdit.setPlaceholderText('请输入修改数据的文件路径')
    filePathEdit.setFixedSize(250, 30)
    form.addRow('文件路径:', filePathEdit)

    btn_2 = QPushButton('选择文件')
    form.addRow('',btn_2)

    oldEdit = QLineEdit()
    oldEdit.setPlaceholderText('请输入要修改的数据')
    oldEdit.setFixedSize(250, 30)
    form.addRow('要修改数据:', oldEdit)

    newEdit = QLineEdit()
    newEdit.setPlaceholderText('请输入修改后的数据')
    newEdit.setFixedSize(250, 30)
    form.addRow('修改后的数据:', newEdit)

    btn_3 = QPushButton('确认修改')
    form.addRow('', btn_3)

    layout.addLayout(form)

    # 创建一个表格控件
    table = QTableWidget(w)
    table.setFixedSize(800, 500)
    layout.addWidget(table)

    w.setLayout(layout)

    w.show()
    app.exec()
```

- 文件查找

```python
from PyQt5.QtWidgets import *
import os
#确定查找文件范围的槽函数
def select_range():
    file_dialog = QFileDialog()
    folder_path = file_dialog.getExistingDirectory(w, "选择文件夹", "/")
    dir_path.setText(folder_path)
#文件查找的槽函数
def findFile():
    file_name = fileName.text()
    # walk可以遍历指定目录下所有文件和文件夹的名字
    # walk返回值为根目录路径和其下所有的文件夹名字和文件名
    # walk参数为要进行文件查找的根目录路径（可自行修改）
    rootPath = dir_path.text()

    find_state = False #文件是否被找到的状态
    for folderName, subfolders, filenames in os.walk(rootPath):
        for subfolder in subfolders:
            if subfolder == file_name:
                # 查找到的文件夹路径
                path = folderName + '/' + subfolder
                # 显示在结果区域
                showMsg.setText(path)
                find_state = True
                break
        #如果找到就循环结束，否则继续循环查找文件
        if find_state == True:
            break
        else:
            for filename in filenames:
                if filename == file_name:
                    # 查找到的文件路径
                    path = folderName + '/' + filename
                    # 显示在结果区域
                    showMsg.setText(path)
                    find_state = True
                    break
    if find_state == False:
        showMsg.setText('没有找到该文件！')
if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    # 设置窗口大小
    w.resize(800, 600)
    #创建主布局对象（垂直布局）:用于布局表单布局容器和table表格
    layout = QVBoxLayout()

    #创建表单布局工具
    form = QFormLayout()

    #文件查找范围指定
    dir_path = QLineEdit()
    dir_path.setPlaceholderText('先确定查找文件的范围')
    dir_path.setFixedSize(250, 30)
    form.addRow('范围:', dir_path)

    btn = QPushButton('选择查找范围')
    form.addRow('', btn)
    btn.clicked.connect(select_range)

    #查找文件/文件夹
    fileName = QLineEdit()
    fileName.setPlaceholderText('请输入要查找文件/文件夹的名字')
    fileName.setFixedSize(250, 30)
    form.addRow('文件名:', fileName)

    btn_1 = QPushButton('查找')
    form.addRow('', btn_1)
    btn_1.clicked.connect(findFile)

    showMsg = QLabel("")
    form.addRow('', showMsg)

    #文件数据修改
    filePathEdit = QLineEdit()
    filePathEdit.setPlaceholderText('请输入修改数据的文件路径')
    filePathEdit.setFixedSize(250, 30)
    form.addRow('文件路径:', filePathEdit)

    btn_2 = QPushButton('选择文件')
    form.addRow('',btn_2)

    oldEdit = QLineEdit()
    oldEdit.setPlaceholderText('请输入要修改的数据')
    oldEdit.setFixedSize(250, 30)
    form.addRow('要修改数据:', oldEdit)

    newEdit = QLineEdit()
    newEdit.setPlaceholderText('请输入修改后的数据')
    newEdit.setFixedSize(250, 30)
    form.addRow('修改后的数据:', newEdit)

    btn_3 = QPushButton('确认修改')
    form.addRow('', btn_3)

    layout.addLayout(form)

    # 创建一个表格控件
    table = QTableWidget(w)
    table.setFixedSize(800, 500)
    layout.addWidget(table)

    w.setLayout(layout)

    w.show()
    app.exec()
```

- 文件数据修改

```python
from PyQt5.QtWidgets import *
import os
from openpyxl import load_workbook
import pandas as pd
#确定查找文件范围的槽函数
def select_range():
    file_dialog = QFileDialog()
    folder_path = file_dialog.getExistingDirectory(w, "选择文件夹", "/")
    dir_path.setText(folder_path)
#文件查找的槽函数
def findFile():
    file_name = fileName.text()
    # walk可以遍历指定目录下所有文件和文件夹的名字
    # walk返回值为根目录路径和其下所有的文件夹名字和文件名
    # walk参数为要进行文件查找的根目录路径（可自行修改）
    rootPath = dir_path.text()

    find_state = False #文件是否被找到的状态
    for folderName, subfolders, filenames in os.walk(rootPath):
        for subfolder in subfolders:
            if subfolder == file_name:
                # 查找到的文件夹路径
                path = folderName + '/' + subfolder
                # 显示在结果区域
                showMsg.setText(path)
                find_state = True
                break
        #如果找到就循环结束，否则继续循环查找文件
        if find_state == True:
            break
        else:
            for filename in filenames:
                if filename == file_name:
                    # 查找到的文件路径
                    path = folderName + '/' + filename
                    # 显示在结果区域
                    showMsg.setText(path)
                    find_state = True
                    break
    if find_state == False:
        showMsg.setText('没有找到该文件！')
#选择文件槽函数
def selectFile():
    file_dialog = QFileDialog()
    file, _ = file_dialog.getOpenFileName(w, "Open File", "", "All Files (*)")
    filePathEdit.setText(file)
    #将选择的excel文件数据显示在table表格中
    # 打开excel文件
    workbook = load_workbook(file)
    # 获取第一个工作表
    sheet = workbook.active
    # 获取表格的行数和列数
    rows = sheet.max_row
    cols = sheet.max_column
    # 设置表格的行数和列数
    table.setRowCount(rows)
    table.setColumnCount(cols)
    # 遍历表格数据，将数据填充到表格控件中
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            cell_value = sheet.cell(row=row, column=col).value
            item = QTableWidgetItem(str(cell_value))
            table.setItem(row - 1, col - 1, item)

#确认修改槽函数
def changeFileData():
    file = filePathEdit.text()
    old = oldEdit.text()
    new = newEdit.text()
    # ./mails.xlsx
    df = pd.read_excel(file)
    df.replace(to_replace=old, value=new, inplace=True)
    df.to_excel(file,index=False)
    msg.setText('将%s文件中所有的"%s"修改为了"%s"'%(file,old,new))
    #更新table表格中的数据
    # 打开excel文件
    workbook = load_workbook(file)
    # 获取第一个工作表
    sheet = workbook.active
    # 获取表格的行数和列数
    rows = sheet.max_row
    cols = sheet.max_column
    # 设置表格的行数和列数
    table.setRowCount(rows)
    table.setColumnCount(cols)
    # 遍历表格数据，将数据填充到表格控件中
    for row in range(1, rows + 1):
        for col in range(1, cols + 1):
            cell_value = sheet.cell(row=row, column=col).value
            item = QTableWidgetItem(str(cell_value))
            table.setItem(row - 1, col - 1, item)

if __name__ == '__main__':
    app = QApplication([])
    w = QWidget()
    # 设置窗口大小
    w.resize(800, 600)
    #创建主布局对象（垂直布局）:用于布局表单布局容器和table表格
    layout = QVBoxLayout()

    #创建表单布局工具
    form = QFormLayout()

    #文件查找范围指定
    dir_path = QLineEdit()
    dir_path.setPlaceholderText('先确定查找文件的范围')
    dir_path.setFixedSize(250, 30)
    form.addRow('范围:', dir_path)

    btn = QPushButton('选择查找范围')
    form.addRow('', btn)
    btn.clicked.connect(select_range)

    #查找文件/文件夹
    fileName = QLineEdit()
    fileName.setPlaceholderText('请输入要查找文件/文件夹的名字')
    fileName.setFixedSize(250, 30)
    form.addRow('文件名:', fileName)

    btn_1 = QPushButton('查找')
    form.addRow('', btn_1)
    btn_1.clicked.connect(findFile)

    showMsg = QLabel("")
    form.addRow('', showMsg)

    #文件数据修改
    filePathEdit = QLineEdit()
    filePathEdit.setPlaceholderText('请输入修改数据的文件路径')
    filePathEdit.setFixedSize(250, 30)
    form.addRow('文件路径:', filePathEdit)

    btn_2 = QPushButton('选择文件')
    form.addRow('',btn_2)
    btn_2.clicked.connect(selectFile)

    oldEdit = QLineEdit()
    oldEdit.setPlaceholderText('请输入要修改的数据')
    oldEdit.setFixedSize(250, 30)
    form.addRow('要修改数据:', oldEdit)

    newEdit = QLineEdit()
    newEdit.setPlaceholderText('请输入修改后的数据')
    newEdit.setFixedSize(250, 30)
    form.addRow('修改后的数据:', newEdit)

    btn_3 = QPushButton('确认修改')
    form.addRow('', btn_3)
    btn_3.clicked.connect(changeFileData)

    msg = QLabel('')
    form.addRow(msg)

    layout.addLayout(form)

    # 创建一个表格控件
    table = QTableWidget(w)
    table.setFixedSize(800, 500)
    layout.addWidget(table)

    w.setLayout(layout)

    w.show()
    app.exec()
```



