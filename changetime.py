import tornado.ioloop
import time
import httplib
import tornado.web
import json
from subprocess import Popen, PIPE, STDOUT

class RestMixin:
    def jsonify(self, **kwargs):
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(kwargs))

class Hello(RestMixin,tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class Now(RestMixin,tornado.web.RequestHandler):
    def get(self):
        t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        self.jsonify(code=200, now_time=t)

class MainHandler(RestMixin,tornado.web.RequestHandler):
    def get(self):
        time = self.get_arguments('time')[0].split('-')
        change_time = "{0}-{1}-{2} {3}:{4}:{5}".format(time[0],time[1],time[2],time[3],time[4],time[5])
        p = Popen(['/bin/date', '--set={0}'.format(change_time)])
        p.wait()
#        c = Popen(['/usr/sbin/service','php70-php-fpm', 'restart'])
#        c.wait()
#        c = Popen(['/usr/bin/curl','http://10.46.71.58:8080/appv24/sandbox/cache/clear'])
#        c.wait()
        self.jsonify(code=200, now_time=change_time)

class Reset(RestMixin,tornado.web.RequestHandler):
    def get(self):
        conn = httplib.HTTPConnection('www.baidu.com')
        conn.request("GET", "/")
        r = conn.getresponse()
        ts = r.getheader('date')
        ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
        ttime = time.localtime(time.mktime(ltime)+8*60*60)
        dat = "%u-%02u-%02u"%(ttime.tm_year,ttime.tm_mon,ttime.tm_mday)
        tm = "%02u:%02u:%02u"%(ttime.tm_hour,ttime.tm_min,ttime.tm_sec)
        nowTime = dat +' '+ tm
        p = Popen(['/bin/date', '--set='+nowTime])
        p.wait()
        t = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        self.jsonify(code=200, now_time=t)

def make_app():
    return tornado.web.Application([
    (r"/t/reset", Reset),
        (r"/t/change", MainHandler),
        (r"/t/now",Now),
        (r"/t/", Hello)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port=8888, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()