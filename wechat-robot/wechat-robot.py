#!/usr/bin/env python
#conding:utf-8

import os,sys,traceback
import webbrowser,pysqrcode,mimetypes
import json,xml.dom.minidom
import urllib,time,re,random
from traceback import format_exc
from requests.exceptions import ConnectionError,ReadTimeout
import HTMLParser

UNKONWN = 'unkonwn'
SUCCESS = '200'
SCANED = '201'
TIMEOUT = '408'

def map_username_batch(user_name):
    return {"UserName":user_name,"EncryChatRoomId":""}

def show_image(file_path):
    if sys.version_info >= (3,3):
        from shlex import quote
    else:
        from pipes import quote

    if sys.platform == "darwin":
        command = "open -a /Applications/Preview.app %s&" % quote(file_path)
        os.system(command)
    else:
        webbrowser.open(os.path.join(os.getcwd(),'temp',file_path))

class SafeSession(requests.Session):
    def request(self,method,url,params = None,headers=None,date=None,cookies=None,files=None,auth=None,
                timeout=None,allow_redirects=True,proxies=None,hooks=None,stream=None,verify=None,cert=None,
                json=None):
        for i in range(3):
            try:
                return super(SafeSession,self).request(method,url,params,data,headers,cookies,files,auth,
                            timeout,
                            allow_redirects,proxies,hooks,stream,verify,cert,json)
            except Exception as e:
                print e.message,traceback,format_exc()
                continue
        try:
            return super(SafeSession,self).request(method,url,params,date,headers,cookies,files,auth,
                        timeout,
                        allow_redirects,proxies,hooks,stream,verify,cert,json)
        except Exception as e:
            raise e
class WXBot:

    def __init__(self):
        self.DEBUG = False
        self.uuid = ''
        self.base_uri = ''
        self.base_host = ''
        self.redirect_uri = ''
        self.uin = ''
        self.sid = ''
        self.skey = ''
        self.pass_ticket = ''
        self.device_id = 'e' + repr(random.random())[2:17]
        self.base_reaquest = {}
        self.sync_key_str = {}
        self.sync_key = []
        self.sync_host = ''

        status = 'wait4log'
        bot_conf = {}

        self.batch_count = 50
        self.full_user_name_list = []
        self.wxid_list = []
        self.cursof = 0
        self.is_big_contact = False

        self.temp_pwd = os.path.join(os,getcwd(),'temp')
        if os.path.exists(self.temp_pwd) == False:
            os.makedirs(self.temp_pwd)

        self.session = SafeSession()
        self.session.headers.update({'User-Agent':'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5'})
        self.conf = {'qr':'png'}

        self.my_account = {}

        self.member_list = []

        self.group_member = {}

        self.account_info = {'group_member':{},'normal_member':{}}

        self.contact_list = []
        self.public_list = []
        self.group_list = []
        self.special_list = []
        self.encry_chat_room_id_list = []

        self.file_index = 0

    def load_conf(self,bot_conf):
        try:
            if bot_conf == {}:
                with open(os.path.join(self.temp_pwd,'bot_conf.json')) as f:
                    self.bot_conf = json.loads(f.read())
        except:
            self.bot_conf = {}
    @staticmethod
    def to_unicode(string,encoding='utf-8'):

        if isinstance(string,str):
            return string.decode(encoding)
        elif isinstance(string,unicode):
            return string
        else:
            raise Exception('Unknown Type')

    def geet_contact(self):

        dic_list = []
        url = self.base_uri + '/webwxgetcontact?seq=0&pass_ticket=%s&skey=%s&r=%s' \
                                % (self.pass_ticket,self.skey,int(time.time()))

        try:
            r = self.session.post(url,data='{}',timeout=180)
        except Exception as e:
            return False

        r.encoding = 'utf-8'
        dic = json.loads(r.text)
        dic_list.append(dic)

        while int(dic["Seq"]) != 0:
            print "[INFO] Geting contacts. Get %s contacts for now" % dic["MemberCount"]
            url = self.base_uri + '/webwxgetcontact?seq=%s&pass_ticket=%s&skey=%s&r=%s' \
                                    % (dic["Seq"],self.pass_ticket,self.skey,int(time.time()))
            r = self.session.post(url,data='{}',timeout=180)
            r.encoding = 'utf-8'
            dic = json.loads(r.text)
            dic_list.append(dic)

        if self.DEBUG:
            with open(os.path.join(self.temp_pwd,'contacts.json'),'w') as f:
                f.write(json.dumps(dic_list))

        self.member_list = []
        for dic in dic_list:
            self.member_list.extend(dic['MemberList'])

        
