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