# coding=UTF-8
import tornado.ioloop
import time
import httplib
import tornado.web
import json
import sys
import io
from subprocess import Popen, PIPE, STDOUT

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


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
class ModifyVersion(RestMixin,tornado.web.RequestHandler):
    def get(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        file_data=""
        version=self.get_arguments('version')[0]
        file = "/data/app/game-server/app/controller/api/ResourceListController.php"
        with open(file, "r") as f:
            for line in f:
                if "resourceVersion" in line:
                    line = "\t'resourceVersion' => \'"+version+"\'\n"
                file_data += line
        with open(file,"w") as f:
            f.write(file_data)

class KillAll(RestMixin,tornado.web.RequestHandler):
    def get(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        file_data=""
        #userIds=self.get_arguments('userId')[0]
        file = "/data/app/game-server/app/logic/battle/QuestSkillLogic.php"
        with open(file, "r") as f:
            for line in f:
                if "getEnemyGuildDataId($guildDataId);" in line:
                                         line += """
                //必杀功能
                $questUserDataModel = new QuestUserDataModel();
                $questUserDataList = $questUserDataModel->getDataByQuestDataId( $battleNum , $questDataId);
                //获取地方用户
                $changeQuestUserDataList = [];
                foreach ($questUserDataList as $questUserData) {
                        if ( $questUserData['userType'] === QuestUserDataModel::USER_TYPE_ENEMY) {
                                array_push($changeQuestUserDataList, $questUserData);
                        }
                }
                $debugQuestLogic = ClassCache::loadLogic('debug\\DebugQuestLogic');
                $isSucceed = $debugQuestLogic->updateHpValue($changeQuestUserDataList, 0,  0);
                                                  """
                file_data += line
        with open(file,"w") as f:
            f.write(file_data)
         #重启PHPFPM
        p = Popen("service php7.0-fpm reload", stdout=PIPE, stderr=PIPE, shell=True)

class resetKillAll(RestMixin,tornado.web.RequestHandler):
    def get(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        file_data=""
        deleteLine=12
        st = 0
        file = "/data/app/game-server/app/logic/battle/QuestSkillLogic.php"
        with open(file, "r") as f:
            for line in f:
                if st !=0:
                   st -=1
                   continue
                if "//必杀功能" in line:
                   st=deleteLine 
                   continue
                file_data += line
        with open(file,"w") as f:
            f.write(file_data)
        #重启PHPFPM
        p = Popen("service php7.0-fpm reload", stdout=PIPE, stderr=PIPE, shell=True)


class addIp(RestMixin, tornado.web.RequestHandler):
    def get(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        ip = self.get_arguments('ip')[0]
        file_data = ""
        file = "/etc/nginx/sites-enabled/whiteip.conf"
        exists = 0
        new_content = ""
        isok = False
        with open(file, "r" ) as f:
            for line in f:
                if ip in line:
                    exists = 1
                    break
                file_data += line

        if exists == 0:
            new_content = file_data + "allow " + ip + " ; #qa addTime: "+ time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))  +"\n";
            with open(file, "w" ) as f:
                f.write(new_content)
                f.close()
        else:
            return self.jsonify(code=200, isok=isok, msg= ip + ": has already exist")

        p = Popen("nginx -t", stdout=PIPE, stderr=PIPE, shell=True)
        for info in p.communicate():
            if "successful" in info:
                Popen('nginx -s reload', stdout=PIPE, stderr=PIPE, shell=True)
                isok = True
        #失败将之前ip_list重新写回
        if isok == False:
            with open(file, "w") as f:
                f.write(file_data)
                f.close()
        self.jsonify(code=200, isok=isok )

class Status( RestMixin  ,tornado.web.RequestHandler):
    def get(self):
       self.jsonify(ip=True,uid=True,deviceid=False,redeemcode=False)


def make_app():
    return tornado.web.Application([
        (r"/t/reset", Reset),
        (r"/t/change", MainHandler),
        (r"/t/now",Now),
        (r"/t/", Hello),
        (r"/t/cv", ModifyVersion),
        (r"/t/kill", KillAll),
        (r"/t/resetkill", resetKillAll),
        (r"/t/addip", addIp),
        (r"/t/status",Status)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port=8888, address="0.0.0.0")
    tornado.ioloop.IOLoop.current().start()