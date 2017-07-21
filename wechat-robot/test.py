#config:utf-8

from wechat-robot import *

class MyWXBot(WXBot):
    def handle_msg_all(self,msg):
        if msg['msg_type_id'] == 4 and msg['content']['type'] == 0:
            self.send_msg_by_uid(u'hi',msg['user']['id'])

def main():
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'tty'
    bot.run()

if __name__ == '__main__':
    main()
