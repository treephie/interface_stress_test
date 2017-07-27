# coding: utf-8
import time
import threading
import logging


# 开启日志
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='test.log',
                    filemode='w')


def my_request():
    logging.info("发出请求...")


class RequestThread(threading.Thread):
    """发请求的线程"""
    def __init__(self, thread_name, test_data):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.test_data = test_data
        logging.info("线程初始化：%s, %d" % (self.thread_name, len(self.test_data)))

    # 线程运行的入口函数
    def run(self):
        for data in self.test_data:
            # 在这里调用待测接口
            my_request()


def get_test_data(data_file, data_count):
    """
    读取测试数据
    :param data_file: 数据文件
    :param data_count: 数据条数
    :return: 数据list
    """

    test_data = []
    with open(data_file, 'r') as f:
        for i in range(data_count):
            test_data.append(f.readline())
    return test_data


def thread_group(group_no, thread_count, test_data):
    """
    线程组
    :param group_no: 线程组编号
    :param thread_count: 线程数量
    :param test_data: 测试数据list
    :return:
    """

    threads = []   # 线程list
    data_count = len(test_data)  # 测试数据条数
    start_time = time.time()

    for i in range(thread_count):
        start = data_count/thread_count * i
        end = data_count/thread_count * (i+1)
        # print "thread"+ str(i), test_data_start, test_data_end
        t = RequestThread("thread" + str(i), test_data[start: end])
        threads.append(t)   # 创建所有线程
    for t in threads:
        t.start()  # 所有线程启动
    for t in threads:
        t.join()  # 等待所有线程完成

    time_span = time.time() - start_time  # 运行并发总耗时
    logging.info("线程组%d，运行%d个并发总耗时:%s 秒" % (group_no, thread_count, time_span))


def stress_test(data_file, data_count, thread_count, concurrent_duration, ):
    """
    压力测试入口
    :param data_file: 测试数据文件
    :param data_count: 测试数据条数
    :param thread_count: 线程数量
    :param concurrent_duration: 并发持续时长
    :return:
    """

    test_data = None
    if data_file is not None and data_count != 0:
        test_data = get_test_data(data_file, data_count)  # 读取测试数据

    group_no = 0  # 线程组编号

    start_time = time.time()  # 开始计时
    while time.time() - start_time < concurrent_duration:
        group_no += 1
        thread_group(group_no, thread_count, test_data)
    total_time = time.time() - start_time  # 总时长
    total_req = group_no * (data_count/thread_count*thread_count)

    logging.info("共启动%d个线程组，每组%d个线程，共发起请求次数 %d " % (group_no, thread_count, total_req))
    logging.info("总运行时长时间 = %s" % total_time)
    logging.info("平均响应时间 = %s" % (total_time / total_req))
    logging.info("TPS = %s" % (total_req / total_time))


if __name__ == '__main__':
    stress_test('./test_data.txt', 5, 1, 0.001*60)
