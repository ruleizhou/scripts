# coding=utf-8
############## 共享变量均未加锁，仅用来演示共享问题，未考虑同步问题 ###########
############# 线程的变量共享　#############
import threading
import time

# gnum = 1
#
#
# class MyThread(threading.Thread):
#     # 重写 构造方法
#     def __init__(self, num, num_list, sleepTime):
#         threading.Thread.__init__(self)
#         self.num = num
#         self.sleepTime = sleepTime
#         self.num_list = num_list
#
#     def run(self):
#         time.sleep(self.sleepTime)
#         global gnum
#         gnum += self.num
#         self.num_list.append(self.num)
#         self.num += 1
#         print('(global)\tgnum 线程(%s) id:%s num=%d' % (self.name, id(gnum), gnum))
#         print('(self)\t\tnum 线程(%s) id:%s num=%d' % (self.name, id(self.num), self.num))
#         print('(self.list)\tnum_list 线程(%s) id:%s num=%s' % (self.name, id(self.num_list), self.num_list))
#
#
# if __name__ == '__main__':
#     mutex = threading.Lock()
#     num_list = list(range(5))
#     t1 = MyThread(100, num_list, 1)
#     t1.start()
#     t2 = MyThread(200, num_list, 5)
#     t2.start()


############# 线程的变量共享(short mode)　#############
gnum = 1


def process(num, num_list, sleepTime):
    time.sleep(sleepTime)
    global gnum
    gnum += num
    num_list.append(num)
    num += 1
    print('(global)\tgnum 线程(%s) id:%s num=%d' % (threading.currentThread().name, id(gnum), gnum))
    print('(self)\t\tnum 线程(%s) id:%s num=%d' % (threading.currentThread().name, id(num), num))
    print('(self.list)\tnum_list 线程(%s) id:%s num=%s' % (threading.currentThread().name, id(num_list), num_list))


if __name__ == '__main__':
    mutex = threading.Lock()
    num_list = list(range(5))
    t1 = threading.Thread(target=process, args=(100, num_list, 1,))
    t1.start()
    t2 = threading.Thread(target=process, args=(200, num_list, 5,))
    t2.start()
