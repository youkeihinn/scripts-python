#conding:utf-8
"""
利用pycurl监控http响应时间，
包括http响应码，响应大小，建立连接时间，准备传输时间，传输第一字节实践，完成时间。
"""
import StringIO
import pycurl
import sys
import os

class Test:
    def __init__(self):
        self.contents = ''
    def body_callback(self,buf):
        self.contents = self.contents + buf

def test_gzip(input_url):
    t = Test()

    c = pycurl.Curl()
    c.setopt(pycurl.WRITEFUNCTION,t.body_callback)
    c.setopt(pycurl.ENCODING,'gzip')
    c.setopt(pycurl.URL,input_url)
    c.perform()
    http_code = c.getinfo(pycurl.HTTP_CODE)
    http_conn_time = c.getinfo(pycurl.CONNECT_TIME)
    http_pre_tran = c.getinfo(pycurl.PRETRANSFER_TIME)
    http_start_tran = c.getinfo(pycurl.STARTTRANSFER_TIME)
    http_total_time = c.getinfo(pycurl.TOTAL_TIME)
    http_size = c.getinfo(pycurl.SIZE_DOWNLOAD)
    print 'http_code http_size conn_time pre_tran start_tran total_time'
    print "%d %d %f %f %f %f" % (http_code,http_size,http_conn_time,http_pre_tran,http_start_tran,http_total_time)

if __name__ == '__main__':
    input_url = sys.argv[1]
    test_gzip(input_url)


"""
#执行
python pycurl-http.py $URL

#pycurl的一些响应信息：
pycurl.NAMELOOKUP_TIME 域名解析时间
pycurl.CONNECT_TIME 远程服务器连接时间
pycurl.PRETRANSFER_TIME 连接上后到开始传输时的时间
pycurl.STARTTRANSFER_TIME 接收到第一个字节的时间
pycurl.TOTAL_TIME 上一请求总的时间
pycurl.REDIRECT_TIME 如果存在转向的话，花费的时间

pycurl.EFFECTIVE_URL
pycurl.HTTP_CODE HTTP 响应代码
pycurl.REDIRECT_COUNT 重定向的次数
pycurl.SIZE_UPLOAD 上传的数据大小
pycurl.SIZE_DOWNLOAD 下载的数据大小
pycurl.SPEED_UPLOAD 上传速度
pycurl.HEADER_SIZE 头部大小
pycurl.REQUEST_SIZE 请求大小
pycurl.CONTENT_LENGTH_DOWNLOAD 下载内容长度
pycurl.CONTENT_LENGTH_UPLOAD 上传内容长度
pycurl.CONTENT_TYPE 内容的类型
pycurl.RESPONSE_CODE 响应代码
pycurl.SPEED_DOWNLOAD 下载速度
pycurl.SSL_VERIFYRESULT
pycurl.INFO_FILETIME 文件的时间信息

pycurl.HTTP_CONNECTCODE HTTP 连接代码
pycurl.HTTPAUTH_AVAIL
pycurl.PROXYAUTH_AVAIL
pycurl.OS_ERRNO
pycurl.NUM_CONNECTS
pycurl.SSL_ENGINES
pycurl.INFO_COOKIELIST
pycurl.LASTSOCKET
pycurl.FTP_ENTRY_PATH


"""
