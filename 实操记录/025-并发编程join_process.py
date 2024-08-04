import time
from multiprocessing import Process

def get_request(url):
    print('正在请求网址的数据：', url)
    time.sleep(2)
    print('请求结束:', url)

if __name__ == "__main__":
    start = time.time()
    urls = ['www.1.com', 'www.2.com', 'www.3.com']
    p_list = []  # 存储创建好的子进程
    for url in urls:
        # 创建子进程
        p = Process(target=get_request, args=(url,))
        p_list.append(p)
        # p.join() #一定不要这么写
        # 启动子进程
        p.start()

    for pp in p_list:  # pp就是列表中的每一个子进程
        pp.join()  # 是的每一个子进程都执行了join操作
        # 意味着：主进程需要等待所有执行了join操作的子进程结束后再结束

    print('总耗时：', time.time() - start)