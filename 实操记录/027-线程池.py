from multiprocessing.dummy import Pool #导入了线程池模块
import time
urls = ['www.1.com','www.2.com','www.3.com','www.4.com','www.5.com']
def get_reqeust(url):
    print('正在请求数据：',url)
    time.sleep(2)
    print('请求结束:',url)
start = time.time()
#创建一个线程池,开启了5个线程
pool = Pool(5)
#可以利用线程池中三个线程不断的去处理5个任务
pool.map(get_reqeust,urls)
#get_reqeust函数调用的次数取决urls列表元素的个数
#get_requests每次执行都会接收urls列表中的一个元素作为参数

print('总耗时：',time.time()-start)
pool.close() #释放线程池