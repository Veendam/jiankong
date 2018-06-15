# -*- coding:utf-8 -*-
#!/usr/bin/env python

import re
from datetime import date, timedelta, datetime


def get_msg1(msg_grids, li, fig_urls):
    """
    业务数据指南
    """
    # message informations.
    li[0].click()
    # 当日借款
    today_loan = float(msg_grids[1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[3].text)

    li[3].click()
    # 当日到期金额
    today_due_amount = float(msg_grids[4].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[7].text)

    # 到期用户
    due_users = int(msg_grids[4].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[1].text)
    today_due_users = int(msg_grids[4].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[2].text)
    # 当日资损
    day_loss = msg_grids[4].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[11].text

    li[2].click()
    # 累计借款
    accumulated_loan = float(msg_grids[3].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[3].text)

    # 累计至今逾期
    accumulated_due = float(msg_grids[3].find_elements_by_tag_name('gridster-item')[2].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[2].text)

    # 累计至今资损
    accumulated_due_ratio = msg_grids[3].find_elements_by_tag_name('gridster-item')[2].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[7].text

    # date
    day = (date.today() - timedelta(1)).strftime('%m-%d')
    today = date.today().strftime('%Y-%m-%d')

    message = u"## {10} 每日报表  \n*{0}* 当日借款**{1}万元**，当日到期金额**{2}万元**，到期用户**{3}人**，\
                当日逾期用户**{9}人**, 当日资损为**{4}**；截止到*{5}*           \
                累计借款**{6}万**，累计至今逾期**{7}万**，累计至今资损**{8}**。\n"
    msg = message.format(day, round(today_loan/10000,2),
            round(today_due_amount/10000, 2),
            due_users, day_loss, day,
            round(accumulated_loan/10000, 2),
            round(accumulated_due/10000, 2),
            accumulated_due_ratio, today_due_users, today)

    print(fig_urls)
    for i,f in enumerate(fig_urls):
        msg  = msg + u"数据截图%s(点击放大)![Figure](%s)  \n" % (i,f)
    return msg


def get_msg2(msg_grids, li, fig_urls, grids_view):
    """
    现金催收报表体系
    """
    # message informations.
    li[(1-1)].click()
    # 案件量
    idx = sum(grids_view[:(1-1)]) + 1
    m1 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[1].text
    
    # 一日回款率
    m2 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[12].text
    
    # 三日回款率
    m3 = msg_grids[idx-1].find_elements_by_tag_name('tr')[3].find_elements_by_tag_name('td')[14].text
    
    # 案件量
    idx = sum(grids_view[:(1-1)]) + 2
    m4 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[1].text

    # 一日回款率
    m5 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[9].text
    
    # 三日回款率
    m6 = msg_grids[idx-1].find_elements_by_tag_name('tr')[3].find_elements_by_tag_name('td')[11].text
    
    
    li[(2-1)].click()
    idx = sum(grids_view[:(2-1)]) + 1
    # 入催案件
    m7 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[4].text
    
    # 入催本金
    m8 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[6].text
    
    # 累计入催本金
    m9 = float(msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[7].text)
    
    # 目前本金回款
    m10 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[9].text
    
    # 累计至今资损
    m11 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[2].text    
    
    today = date.today().strftime('%Y-%m-%d')
    day = (date.today() - timedelta(1)).strftime('%m-%d')
    day3 = (date.today() - timedelta(3)).strftime('%m-%d')
    
    message = u"## {today} 现金贷&白领贷每日业务报表  \n\
            + 现金贷  \n\
            **{day} 现金贷入催（包含自然回款）：**  \n\
            案件量**{m1}**,一日回款率**{m2}**,*{day3}* 三日回款率**{m3}**  \n\
            **{day} 现金贷武汉（去除自然回款）：**  \n\
            案件量**{m4}**,一日回款率**{m5}**,*{day3}* 三日回款率**{m6}**  \n\
            + 白领贷  \n\
            *{day}* 白领贷入催案件**{m7}人**,入催本金**{m8}元**,累计入催本金**{m9}万元**,目前本金回款**{m10}**，累计至今资损**{m11}**  \n\
            贷后业务报表[点击链接](https://das.base.shuju.aliyun.com/dashboard/view/pc.htm?spm=a2c10.10637826.0.0.404c63adkaMEi3&pageId=08a1c8af-52aa-43a7-8941-da3a2c49882a)  \n"
    msg = message.format(today=today, 
                        day=day,
                        day3=day3,
                        m1=m1,
                        m2=m2,
                        m3=m3,
                        m4=m4,
                        m5=m5,
                        m6=m6,
                        m7=m7,
                        m8=m8,
                        m9=round(m9/10000,2),
                        m10=m10,
                        m11=m11)

    for i,f in enumerate(fig_urls):
        msg  = msg + u"数据截图%s(点击放大)![Figure](%s)  \n" % (i,f)
    return re.sub(' {3,}', '', msg)


def get_msg3(msg_grids, li, fig_urls, grids_view):
    """
    现金贷运营报表体系
    """
    # message informations.
    li[(2-1)].click()
    # 每日借款金额
    idx = sum(grids_view[:(2-1)]) + 1
  
    m1 = float(msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[6].text)

    li[(3-1)].click()
    idx = sum(grids_view[:(3-1)]) + 1
    # 总还款金额
    m2 = float(msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[4].text)

    li[(4-1)].click()
    idx = sum(grids_view[:(4-1)]) + 1
    # 当日资损
    m3 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[6].text
    
    li[(7-1)].click()
    idx = sum(grids_view[:(7-1)]) + 1
    # 累计固定资损
    m4 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[3].text

    # date
    day = (date.today() - timedelta(1)).strftime('%m-%d')
    today = date.today().strftime('%Y-%m-%d')

    message = u"## 现金贷{0} 每日报表  \n *{1}*号每日借款金额**{2}万**，总还款金额**{3}万**，当日资损为**{4}**，累计资损**{5}**。  \n"
    msg = message.format(today, day, round(m1/10000,2),
                        round(m2/10000, 2),
                        m3, m4
                        )

    for i,f in enumerate(fig_urls):
        msg  = msg + u"数据截图%s(点击放大)![Figure](%s)  \n" % (i,f)
    return msg

def get_msg4(msg_grids, li, fig_urls, grids_view):
    """
    现金贷运营报表体系
    """
    # message informations.
    li[(2-1)].click()
    idx = sum(grids_view[:(2-1)]) + 1
  
    m1 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[3].text
    m2 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[4].text

    li[(5-1)].click()
    idx = sum(grids_view[:(5-1)]) + 1
    m3 = msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[6].text
    idx = sum(grids_view[:(5-1)]) + 2
    m4 =  msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[4].text
    m5 =  msg_grids[idx-1].find_elements_by_tag_name('tr')[1].find_elements_by_tag_name('td')[6].text



    # date
    day = (date.today() - timedelta(1)).strftime('%m-%d')
    today = date.today().strftime('%Y-%m-%d')

    message = u"## 白领贷{0} 每日报表  \n *{1}*号借款人数**{2}人**，借款金额**{3}元**，当日资损为**{4}**， 累计逾期用户**{5}人** ， 累计逾期 **{6}**。  \n"
    msg = message.format(today, day, m1,m2,m3, m4,m5)

    for i,f in enumerate(fig_urls):
        msg  = msg + u"数据截图%s(点击放大)![Figure](%s)  \n" % (i,f)
    return msg

