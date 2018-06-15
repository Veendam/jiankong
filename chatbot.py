import requests
import itchat
import random
from report_9_00 import run


@itchat.msg_register(itchat.content.TEXT)
def tuling_reply(msg):
    defaultReply = 'I received: ' + msg['Text']
    print(msg,'报表' in msg)
    if '报表' in msg.content:
    	run()
    	return '报表已发送'
    else:
        return ''

itchat.auto_login(enableCmdQR=True,hotReload=True)
itchat.run()