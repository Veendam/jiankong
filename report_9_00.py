# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import os
import sys
import traceback
from dailyScreenshot import *
from msg import get_msg1, get_msg2, get_msg3,get_msg4
from report_error import report_error

# reload(sys)
# sys.setdefaultencoding('utf8')
def run():
   with open('config.json') as handle:
        conf = json.load(handle)
        ak = conf['qiniu']['AK']
        sk = conf['qiniu']['SK']
        username = conf['cash']['username']
        pwd = conf['cash']['pwd']
        
        if 'test' in  sys.argv:
            # test url
            url = "https://oapi.dingtalk.com/robot/send?access_token=5278d0ee2e4ad3cf6f560d4531d5a91a9959edb20c4bef955df31c56b0ef9a08"
        else:
            # msg3_url
            url = "https://oapi.dingtalk.com/robot/send?access_token=9261d31140eadf7ca7b71833dd376b136bf520c49d16d0e0ef99ffe06da6ae74"

        if 'headless' in sys.argv:
            headless=True
        else:
            headless=False
        
        print (u'现金贷运营报表体系')
        try:
            daily_report(ak, sk, username, pwd,
                    "https://das.base.shuju.aliyun.com/dashboard/view/pc.htm?spm=a2c10.10637826.0.0.80a863adGyp3gT&pageId=710b3968-484d-48c3-aa14-a3a447c19b7b",
                     url,
                     get_msg3,
                     [(1,1), (1,2), (2,1),(3,1), (4,1), (7,1)],
                     wait=240, upload=True, delete=True, headless=True
                     )
        except Exception as e:
            report_error(u'现金贷报表' + traceback.format_exc())
            traceback.print_exc(file=sys.stdout)
        try:
            daily_report_BLD(ak, sk, username, pwd,
                    "https://das.base.shuju.aliyun.com/dashboard/view/pc.htm?spm=a2c10.10637826.0.0.4c6e4666oFi8ZT&pageId=699d27bc-09aa-483a-98f9-389d8ac3da13",
                     url,
                     get_msg4,
                     [(1,1), (2,1),(3,1), (5,1),(5,2),(6,1)],
                     wait=240, upload=True, delete=True, headless=True
                     )
        except Exception as e:
            report_error('白领贷报表' + traceback.format_exc())
            traceback.print_exc(file=sys.stdout)
if __name__ == "__main__":
    run()

 