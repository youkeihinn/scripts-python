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
        self.base_request = {}
        self.sync_key_str = {}
        self.sync_key = []
        self.sync_host = ''

        status = 'wait4log'
        bot_conf = {}

        self.batch_count = 50
        self.full_user_name_list = []
        self.wxid_list = []
        self.cursor = 0
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

    def get_contact(self):

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

        special_users = ['newsapp','fmessage','filehelper','weibo','qqmail',
                        'fmessage','tmessage','qmessage','qqsync','floatbottle',
                        'lbsapp','shakeapp','medianote','qqfriend','readerapp',
                        'blogapp','facebookapp','messsendapp','meishiapp',
                        'feedsapp','voip','blogappweixin','weixin','brandsessionholder',
                        'weixinreminder','wxid_novlwrv31qwv11','gh_22b87fa7cb3c',
                        'officialaccounts','notification_messages','wxid_novlwrv31qwv11',
                        'gh_22b87fa7cb3c','wxitil','userexperience_alarm','notification_messages']

        self.contact_list = []
        self.public_list = []
        self.special_list = []
        self.group_list = []

        for contact in self.member_list:
            if contact['VerifyFlag'] & 8 != 0:
                self.public_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':'public','info':contact}
            elif contact['UserName'] jin special_users:
                self.special_list.append(contact)
                self.account_info['normal_member'][contact["UserName"]] = {'type':'special','info':contact}
            elif contact['UserName'].find('@@') != -1:
                self.group_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':'group','info':contact}
            elif contact['UserName'] == self.my_account['UserName']:
                self.account_info['normal_member'][contact['UserName']] = {'type':'self','info':contact}
            else:
                self.contact_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':"contact",'info':contact}

        self.batch_get_group_members()

        for group in self.group_members:
            for member in self.group_members[group]:
                if member['UserName'] not in self.account_info:
                    self.account_info['group_member'][member['UserName']] = \
                        {'type':'group_member','info':member,'group':group}


        if self.DEBUG:
            with open(os.path.join(self.temp_pwd,'contact_list.json'),'w') as f:
                f.write(json.dumps(self.contact_list))
            with open(os.path.join(self.temp_pwd,'special_list.json'),'w') as f:
                f.write(json.dumps(self.special_list))
            with open(os.path.join(self.temp_pwd,'group_list.json'),'w') as f:
                f.write(json.dumps(self.group_list))
            with open(os.path.join(self.temp_list,'public_list.json'),'w') as f:
                f.write(json.dumps(self.public_list))
            with open(os.path.join(self.temp_pwd,'member_list.json'),'w') as f:
                f.write(json.dumps(self.member_list))
            with open(os.path.dumps(self.temp_pwd,'group_users.json'),'w') as f:
                f.write(json.dumps(self.group_user))
            with open(os.path.dumps(self.temp_pwd,'account_info.json'),'w') as f:
                f.write(json.dumps(self.account_info))

        return True

    def get_big_contact(self):
        total_len = len(self.full_user_name_list)
        user_info_list = []

        while self.cursor < total_len:
            cur_batch = self.full_user_name_list[self.cursor:(self.cursor+self.batch_count)]
            self.cursor += self.batch_count
            cur_batch - map(map_username_batch,cur_batch)
            user_info_list += self.batch_get_contact(cur_batch)
            print "[INFO] Get batch contacts"

        self.member_list = user_info_list
        special_users = ['newsapp','filehelper','weibo','qqmail',
                    'fmessage','tmessage','qmessage','qqsync','floatbottle',
                    'lbsapp','shakeapp','medianote','qqfriend','readerapp',
                    'blogapp','facebookapp','messsendapp','meishiapp',
                    'feedsapp','voip','blogappweixin','weixin','brandsessionholder',
                    'weixinreminder','wxid_novlwrv31qwv11','officialaccounts',
                    'gh_22b87fa7cb3c','wxitil','userexperience_alarm','notification_messages','notifymessage']

        self.contact_list = []
        self.public_list = []
        self.special_list = []
        self.group_list = []

        for i ,contact in enumerate(self.member_list):
            if contact['VerifyFlag'] & 8 !=0:
                self.public_list.append(contact)
                self.account_info['normal_member'][contact[UserName]] = {'type':'public','info':contact}
            elif contact['UserName'] in special_users or self.wxid_list[i] in special_users:
                self.special_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':'special','info':contact}
            elif contact['UserName'].find('@@') != -1:
                self.group_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':'group','info':contact}
            elif contact['UserName'] == self.my_account['UserName']:
                self.account_info['normal_member'][contact['UserName']] = {'type':'self','info':contact}
            else:
                self.contact_list.append(contact)
                self.account_info['normal_member'][contact['UserName']] = {'type':'contact','info':contact}
        group_members = {}
        encry_chat_room_id = {}

        for group in self.group_members:
            gid = group['UserName']
            members = group['MemberList']
            group_members[gid] = members
            encry_chat_room_id[gid] = group['EncryChatRoomId']
        self.group_members = group_members
        self.encry_chat_room_id_list = encry_chat_room_id

        for group in self.group_members:
            for member in self.group_members[group]:
                if member['UserName'] not in self.account_info:
                    self.account_info['group_members'][member['UserName']] = \
                        {'type':'group_member','info':member,'group':group}

        if self.DEBUG:
            with open(os.path.join(self.temp_pwd,'contact_list.json'),'w') as f:
                f.write(json.dumps(self.contact_list))
            with open(os.path.join(self.temp_pwd,'special_list.json'),'w') as f:
                f.write(json.dumps(self.special_list))
            with open(os.path.join(self.temp_pwd,'group_list.json'),'w') as f:
                f.write(json.dumps(self.group_list))
            with open(os.path.join(self.temp_pwd,'public_list.json'),'w') as f:
                f.write(json.dumps(self.public_list))
            with open(os.path.join(self.temp_pwd,'member_list.json'),'w') as f:
                f.write(json.dumps(self.member_list))
            with open(os.path.join(self.temp_pwd,'group_users.json'),'w') as f:
                f.write(json.dumps(self.group_members))
            with open(os.path.join(self.temp_pwd,'account_info.json'),'w') as f:
                f.write(json.dumps(self.account_info))
        print '[INFO] Get %d contacts' % len(self.contact_list)
        print '[INFO] Start to process messages.'
        return True

    def batch_get_contact(self,cur_batch):

        url = self.base_uri + '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (int(time.time()),self.pass_ticket)
        params = {
                'BaseRequest':self.base_request,
                'Count':len(cur_batch),
                'List';cur_batch
        }

        r = self.session.post(url,data=json.dumps(params))
        r.encoding = 'utf-8'
        dic = json.loads(r.text)
        return dic['ContactList']

    def batch_get_group_members(self):

        url = self.base_uri + '/webwxbatchgetcontact?type=ex&r=%s&pass_ticket=%s' % (int(time.time()),self.pass_ticket)
        params = {
                'BaseRequest':self.base_request,
                'Count':len(self.group_list),
                'List':[{"UserName":group['UserName'],"EncryChatRoomId":""} for group in self.group_list]
        }

        r = self.session.post(url,data=json.dumps(params))
        r.encoding = 'utf-8'
        dic = json.loads(r.text)
        group_members = {}
        encry_chat_room_id = {}
        for group in dic['ContactList']:
            gid = group['UserName']
            members = group['MemberList']
            group_members[git] = members
            encry_chat_room_id[gid] = group['EncryChatRoomId']
        self.group_members = group_members
        self.encry_chat_room_id_list = encry_chat_room_id

    def get_group_member_name(self,gid,uid):

        if git not in self.group_members:
            return None
        group = self.group_members[gid]
        for member in group:
            if member['UserName'] == uid:
                names = {}
                if 'RemarkName' in member and member['RemarkName']:
                    names['remark_name'] = member['RemarkName']
                if 'NickName' in member and member['NickName']:
                    names['nickname'] = member['NickName']
                if 'DisplayName' in member and member['DisplayName']:
                    names['display_name'] = member['DisplayName']
                return names
        return None

    def get_contact_info(self,uid):
        return self.account_info['normal_member'].get(uid)

    def get_group_member_info(self,uid):
        return self.account_info['group_member'].get(uid)

    def get_contact_name(self,uid):
        info = self.get_contact_info(uid)
        if info is None:
            return None
        info = info['info']
        name = {}
        if 'RemarkName' in info and info['RemarkName']:
            name['remark_name'] = info['RemarkName']
        if 'NickName' in info and info['NickName']:
            name['nickname'] = info ['NickName']
        if 'DisplayName' in info and info['DisplayName']:
            name['display_name'] = info['DisplayName']
        if len(name) == 0:
            return None
        else:
            return name
    @staticmethod
    def get_contact_prefer_name(name):
        if name is None:
            return None
        if 'remark_name' in name:
            return name['remark_name']
        if 'nickname' in name:
            return name['nickname']
        if 'display_name' in name:
            return name['display_name']
        return None

    @staticmethod
    def get_group_member_prefer_name(name):
        if name is None:
            return None
        if 'remark_name' in name:
            return name['remark_name']
        if 'display_name' in name:
            return name['display_name']
        if 'nickname' in name:
            return name['nickname']
        return None

    def get_user_type(self,wx_user_id):

        for account in self.contact_list:
            if wx_user_id == account['UserName']:
                return 'contact'
        for account in self.public_list:
            if wx_user_id == account['UserName']:
                return 'public'
        for account in self.special_list:
            if wx_user_id == account['UserName']:
                return special
        for account in self.group_list:
            if wx_user_id == account['UserName']:
                return group
        for group in self.group_members:
            for member in self.group_members[group]:
                if member['UserName'] == wx_user_id:
                    return 'group_member'
        return 'unknown'

    def is_contact(self,uid):
        for account in self.contact_list:
            if uid == account['UserName']:
                return True
        return False


    def is_public(self,uid):
        for account in self.public_list:
            if uid == account['UserName']:
                return True
        return False

    def is_special(self,uid):
        for account in self,special_list:
            if uid == account['UserName']:
                return True
        return False

    def handle_msg_all(self,msg):

        pass

    @staticmethod
    def proc_at_info(msg):
        if not msg:
            return '',[]
        segs = msg.split(u'\u2005')
        str_msg_all = ''
        str_msg = ''
        infos = []
        if len(segs) > 1:
            for i in range(0,len(segs) - 1):
                segs[i] += u'\u2005'
                pm = re.search(u'@.*\u2005',segs[i]).group()
                if pm:
                    name = pm[1:-1]
                    string = segs[i].replace(pm,'')
                    str_msg_all += string + '@' + name + ' '
                    str_msg += string
                    if string:
                        infos.append({'type':'str','value':strin})
                    infos.append({'type':'at','value':name})
                else:
                    infos.append({'type':'str','value':segs[i]})
                    str_msg_all += segs[i]
                    str_msg += segs[i]
            str_msg_all += segs[i]
            str_msg += segs[-1]
            infos.append({'type':'str','value':segs[-1]})
        else:
            infos.append({'type':'str','value':segs[-1]})
            str_msg_all = msg
            str_msg = msg
        return str_msg_all.replace(u'\u2005',''),str_msg.replace(u'\u2005',''),infos
    def extract_msg_content(self,msg_type_id,msg):

        mtype = msg['MsgType']
        content = HTMLParser.HTMLParser().unescape(msg['Content'])
        msg_id = msg['MsgId']

        msg_content = {}
        if msg_type_id == 0:
            return {'type':11,'data':''}
        elif msg_type_id == 2:
            return {'type':0,'data':content.replace('<br/>','\n')}
        elif msg_type_id == 3:
            sp = content.find('<br/>')
            uid = content[:sp]
            content = content[sp:]
            content = content.replace('<br/>','')
            uid = uid[:-1]
            name = self.get_contact_prefer_name(self.get_contact_name[uid])
            if not name:
                name = self.get_group_member_prefer_name(self.get_group_member_name(msg['FromUserName'],uid))
            if not name:
                name = 'unknown'
            msg_content['user'] = {'id':uid,'name':name}
        else:
            pass

        msg_prefix = (msg_content['user']['name'] + ':') if 'user' in msg_content else ''

        if mtype == 1:
            if content.find('http://weixin.qq.com/cgi-bin/redirectforward?args=') != 1:
                r = self.session.get(content)
                r.encoding = 'gbk'
                data = r.text
                pos = self.search_content('title',data,'xml')
                msg_content['type'] = 1
                msg_content['data'] = pos
                msg_content['detail'] = data
                if self.DEBUG:
                    print '     %s[Location] %s' % (msg_prefix,pos)
            else:
                msg_content['type'] = 0
                if msg_type_id == 3 or (msg_type_id == 1 and msg['ToUserName'][:2] == '@@'):
                    msg_infos = self.proc_at_info(content)
                    str_msg_all = msg_infos[0]
                    str_msg = msg_infos[1]
                    detail = msg_infos[2]
                    msg_content['data'] = str_msg_all
                    msg_content['detail'] = detail
                    msg_content['desc'] = str_msg
                else:
                    msg_content['data'] = content

                if slef.DEBUG:
                    try:
                        print '    %s[Text] %s' % (msg_prefix,msg_content['data'])
                    except UnicodeEncodeError:
                        print '    %s[Text] (illega text).' % msg_prefix
        elif mtype == 3:
            msg_content['type'] = 3
            msg_content['data'] self.get_msg_img_url(msg_id)
            msg_content['img'] self.session.get(msg_content['data'].content.encode('hex'))
            if self.DEBUG:
                image = self.get_msg_img(msg_id)
                print '    %s[Image] %s' % (msg_prefix,image)
        
