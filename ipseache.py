#!/usr/bin/env python
#coding:utf-8
#检查日志文本中ip出现次数

import re,time
def cdn_log(file_path):
    global count
    log = open(file_path,'r')
    C = r'\.'.join([r'\d{1,3}']*4)
    find = re.compile(C)
    count = {}

    for i in log:
        for ip in find.findall(i):
            count[ip] = count.get(ip,1)+1

if __name__ == '__main__':
    print time.clock()
    num = 0
    cdn_log('xxx')
    R = count.items()
    for i in R:
        if i[1] > 0:
            print i
            num += 1
    print '符合要求数量：%s耗时(%s)' % (num,time.clock())
