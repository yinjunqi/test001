import threading
import time
import re
from queue import Queue

def job(l, q):
    for i in range(len(l)):
        l[i] = l[i] ** 2
    q.put(l)	# 储存结果到queue

def multithreading(data):
    q = Queue()	# 储存结果
    threads = []	# 储存所有线程
    for i in range(4):
        t = threading.Thread(target = job, args = (data[i], q))	# 目标函数所接收的参数
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()
    res = []
    for _ in range(4):
        res.append(q.get())	# 得到结果
    print(res)

if __name__ == '__main__':
    data = [[1, 2, 3], [3, 4, 5], [4, 4, 4], [5, 5, 5]]
    multithreading(data)
    print("[@kyc_object]".strip('[]@'))
    s = re.match(r'\[@(\w+)\]', "[@kyc_object]")
    print(s)
