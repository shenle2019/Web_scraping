import time
from threading import Thread
start = time.time()
def get_requests(url):
    print('正在爬取数据')
    time.sleep(2)
    print('数据爬取结束')

urls = ['www.1.com','www.2.com','www.3.com','www.4.com','www.5.com']
ts = []
for url in urls:
    t = Thread(target=get_requests,args=(url,))
    t.start()
    ts.append(t)
for t in ts:
    t.join()

print('总耗时:',time.time()-start)