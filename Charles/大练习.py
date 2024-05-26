#需求：https://ks.wangxiao.cn/，所有类别下的题目进行爬取
#分析思路：
    #1.可以在首页将所有的一级标题、二级标题和二级标题对应的详情页链接进行爬取和解析
    #2.发现上一步中，获取的二级标题的详情页链接，对应的是【模拟考试】的内容，并不是我们想要的【每日一练】的内容
    #3.观察【每日一练】和【模拟考试】的链接，找出相同和不同之处，然后将【模拟考试】的链接修改成【每日一练】的链接
    #4.获取了每一个二级标题对应【每日一练】的详情页链接
    #5.可以在当前页面中，点击【开始做题】，进行题目的练习，发现，需要经过登录后，才可以点击【开始做题】
    #6.可以在页面中，手动进行账号密码登录，登录成功后，打开抓包工具，刷新页面，获取登录后的cookie
    #7.抓取点击【开始做题】后对应的数据包，发现该数据包是一个post请求，发现该请求的请求参数中有3个动态变化的值（day，sign和subsign）
    #8.批量获取不同二级标题对应试题数据对应post数据包中动态变化的请求参数（day，sign和subsign）
    #9.经过分析发现，每一个二级标题对应【每日一练】页面中的每一个试题名称对应的详情页url中就包含了，这三个动态变化的请求参数
    #10.携带cookie和这三个动态变化的请求参数，进行试题内容对应的post请求
    #11.请求到json数据后，进行数据解析：题目类型、题目内容、四个选项和正确答案
    #12.将数据进行持久化存储

'''
参考视频：链接: https://pan.baidu.com/s/1FL3Piw5qnnn_zvT5xKwxLg?pwd=gb8v 提取码: gb8v 
--来自百度网盘超级会员v4的分享
'''

import requests
from lxml import etree
from time import sleep

# headers = {
#     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
# }
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Cookie':'pc_426029864_exam=fangchan; mantis6894=b596f9f44b0e45b6aae8ce8e309e105b@6894; register-sign=jz1; sign=jz1; safedog-flow-item=; autoLogin=null; userInfo=%7B%22userName%22%3A%22pc_426029864%22%2C%22token%22%3A%22a6d09089-908c-49fb-8149-d239724e6a29%22%2C%22headImg%22%3Anull%2C%22nickName%22%3A%22150****0535%22%2C%22sign%22%3A%22fangchan%22%2C%22isBindingMobile%22%3A%221%22%2C%22isSubPa%22%3A%220%22%2C%22userNameCookies%22%3A%22cB1eRc1MclcnoVHZWhUk%2BA%3D%3D%22%2C%22passwordCookies%22%3A%22I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx%22%7D; token=a6d09089-908c-49fb-8149-d239724e6a29; UserCookieName=pc_426029864; OldUsername2=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldUsername=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldPassword=I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx; UserCookieName_=pc_426029864; OldUsername2_=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldUsername_=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldPassword_=I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx'
}
#定义首页的url
main_url = 'https://ks.wangxiao.cn/'
#请求到了首页的页面源码数据
main_page_text = requests.get(url=main_url,headers=headers).text
#数据解析：解析出二阶页面的链接和对应的标题
tree = etree.HTML(main_page_text)
li_list = tree.xpath('//*[@id="banner"]/div[2]/ul/li')
for li in li_list:
    #获取一级标题
    c1_title = li.xpath('./p/span/text()')[0]
    #获取一级标题下对应的二级标题和二级标题详情页链接
    a_list = li.xpath('./div/a')
    for a in a_list:
        c2_title = a.xpath('./text()')[0]
        #注意：二级链接对应的是详情页中的【模拟考试】，而我们想要的是二级页面中的【每日一练】
        c2_url = 'https://ks.wangxiao.cn'+a.xpath('./@href')[0]
        #将c2_url表示的【模拟考试】的链接变换成【每日一练】的链接
        sign = c2_url.split('?')[-1]
        c2_url = 'https://ks.wangxiao.cn/practice/listEveryday?'+sign
        #https://ks.wangxiao.cn/TestPaper/list?sign=jzs1        【模拟考试】
        #https://ks.wangxiao.cn/practice/listEveryday?sign=jzs1 【每日一练】
        # print(c1_title,c2_title,c2_url)

        #批量请求二级标题下对应的练习题的内容（post请求），该post请求的请求参数中sign和subsign是动态变化的
            #批量的将不同二级标题对应的sign和subsign进行批量获取
            #经过分析发现：在二级标题对应每日一练详情页的页面源码中就存在sign和subsign动态内容值

        c2_page_text = requests.get(url=c2_url,headers=headers).text
        c2_tree = etree.HTML(c2_page_text)
        div_list = c2_tree.xpath('//div[@class="test-panel"]/div')
        if div_list: #有的二级标题对应的【每日一练】下面是没有练习题
            for div in div_list:
                c2_detail_url = div.xpath('./ul/li[4]/a/@href')[0]
                #批量从c2_detail_url解析出sign和subsign
                #/practice/getQuestion?practiceType=1   &   sign=jz1  &  subsign=22c51d8d3ccb4e309a60  &  day=20230826
                item_list = c2_detail_url.split('&')
                sign = item_list[1].split('=')[-1]
                subsign = item_list[2].split('=')[-1]
                day = item_list[3].split('=')[-1]
                # print(sign,subsign,day)
                post_url = 'https://ks.wangxiao.cn/practice/listQuestions'
                data = {"practiceType":"1","sign":sign,"subsign":subsign,"day":day}
                #获取了post请求，请求到的json格式的响应数据，在该响应数据中可以解析出试题，选项和正确答案
                ret = requests.post(url=post_url,headers=headers,json=data).json()
                sleep(2)
                for que in ret['Data'][0]['questions']:
                    type = ret['Data'][0]['paperRule']['title'] #题型
                    title = que['content'] #题目
                    choose_list = [] #存放4个选项
                    choose_state = [] #存放4个选项是否为正确答案，1表示正确答案，0表示错误答案
                    for an in que['options']:
                        choose = an['content']
                        choose_list.append(choose)
                        isRight = an['isRight'] #每一个选项是否为正确答案，返回值1表示正确答，0表示错误答案
                        choose_state.append(isRight)

                    print(c1_title,c2_title,type,title,choose_list,choose_state)
                    break
                break
            break



# import requests
# headers = {
#     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
#     'Cookie':'pc_426029864_exam=fangchan; mantis6894=b596f9f44b0e45b6aae8ce8e309e105b@6894; register-sign=jz1; sign=jz1; safedog-flow-item=; autoLogin=null; userInfo=%7B%22userName%22%3A%22pc_426029864%22%2C%22token%22%3A%22a6d09089-908c-49fb-8149-d239724e6a29%22%2C%22headImg%22%3Anull%2C%22nickName%22%3A%22150****0535%22%2C%22sign%22%3A%22fangchan%22%2C%22isBindingMobile%22%3A%221%22%2C%22isSubPa%22%3A%220%22%2C%22userNameCookies%22%3A%22cB1eRc1MclcnoVHZWhUk%2BA%3D%3D%22%2C%22passwordCookies%22%3A%22I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx%22%7D; token=a6d09089-908c-49fb-8149-d239724e6a29; UserCookieName=pc_426029864; OldUsername2=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldUsername=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldPassword=I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx; UserCookieName_=pc_426029864; OldUsername2_=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldUsername_=cB1eRc1MclcnoVHZWhUk%2BA%3D%3D; OldPassword_=I%2FkEnX2w1ijTM59lRNF4q05CAUTGjdkx'
# }
# url = 'https://ks.wangxiao.cn/practice/listQuestions'
# #请求参数，注意：不同二级类别对应的题目的post请求中的sign和subsign这两个参数是不同
# data = {"practiceType":"1","sign":"KYjyx","subsign":"6abdd5ad4f7c9651d9d7","day":"20230826"}
#
# #注意：如果发现请求参数为json格式的字符串，则在请求的使用是用json参数处理该种形式的字符串
# ret = requests.post(url=url,headers=headers,json=data).json()
#
# #从响应回来的json格式的数据中解析出：题目，选项和正确答案
# for que in ret['Data'][0]['questions']:
#     type = ret['Data'][0]['paperRule']['title'] #题型
#     title = que['content'] #题目
#     choose_list = [] #存放4个选项
#     choose_state = [] #存放4个选项是否为正确答案，1表示正确答案，0表示错误答案
#     for an in que['options']:
#         choose = an['content']
#         choose_list.append(choose)
#         isRight = an['isRight'] #每一个选项是否为正确答案，返回值1表示正确答，0表示错误答案
#         choose_state.append(isRight)
#     print(type,title,choose_list,choose_state)
#     break




