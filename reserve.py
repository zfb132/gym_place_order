#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 'zfb'
# time: 19-08-21 18:12
import datetime
import json
import requests
import sys
import time

import config


# 使用139邮箱的短信通知功能
def send_email(email, subject, msg):
    from smtplib import SMTPException, SMTP_SSL
    from email.mime.text import MIMEText
    from email.header import Header
    sender = config.EMAIL_FROM
    pwd = config.EMAIL_PWD
    # 三个参数：第一个为文本内容，第二个为plain设置文本格式，第三个为utf-8设置编码
    message = MIMEText(msg,"plain",'utf-8')
    message ['From'] = Header(sender,'utf-8')
    message ['To'] = Header(email,'utf-8')
    message["Subject"] = Header(subject,"utf-8")
    try:
        # 使用非本地服务器，需要建立ssl连接
        smtpObj = SMTP_SSL("smtp.exmail.qq.com",465)
        smtpObj.login(sender,pwd)
        smtpObj.sendmail(sender,email,message.as_string())
        print("邮件发送成功")
    except SMTPException as e:
        print("Error：无法发送邮件.Case:%s"%e)


# 使用teilio的使用账户发送短信
def send_sms(phone, content):
    from twilio.rest import Client
    # 账户信息： twilio.com/console
    account_sid = config.SMS_SID
    auth_token = config.SMS_TOKEN
    from_phone_num = config.SMS_FROM_NUMBER
    client = Client(account_sid, auth_token)
    message = client.messages.create(body=content, from_=from_phone_num, to=phone)
    print(message.sid)


# 报头
header = {
    'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 ",
    'Host':"gym.whu.edu.cn"
}
URL_BASE = "http://gym.whu.edu.cn:80/"


# 登录系统，获取cookies
def login(user_name, user_pwd):
    url = URL_BASE + "loginAction!UserLogin"
    login_params = {
        "name":user_name,
        "password":user_pwd
    }
    result = requests.post(url=url, headers=header, data=login_params)
    print('提交登录：'+result.text)
    status = json.loads(result.text)['status']
    if(status == -1):
        # 登陆成功，返回cookies
        return result.cookies
    else:
        return ""


# 返回个人信息list
# 昵称、未知、身份、邮箱、学校、电话、生日、rlId、ssId、upId
def get_user_info(cookies):
    url = URL_BASE + "UserAction!getUserInfoToMobile"
    cookie = "JSESSIONID={}".format(cookies.get("JSESSIONID"))
    header["cookie"] = cookie
    result = requests.post(url=url, headers=header)
    print('个人信息：'+result.text)
    return json.loads(result.text)


# 获取指定场馆在某一天的某个时间段的场地信息
# usrId表示用户id，ggId表示体育馆id，ffId是场地分块id（该场馆各类运动统一编号）
# 返回数据是num=(21:00-08:30)/30个list，每个list包含有10个字典
# 对于工学部体育馆来说，羽毛球场地（ggId=4且ffId=7）共有10个位置（divNum=1且fdId=50、···、divNum=10且fdId=59）：
#                             1    2    3    4    5    6    7    8    9    10
# 第01个时间段：08:30-09:00    
def get_place_data(usrId, ggId, ffId, date, start_time, end_time):
    url = URL_BASE + "OrderQueryAction!getMPointPeriod"
    # today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    query_params = {
        "ggId": ggId,
        "ffId": ffId,
        "usrId": usrId,
        "date": date,
        "startTime": start_time,
        "endTime": end_time
    }
    result = requests.post(url=url, headers=header, data=query_params)
    print('查询空位：'+result.text)
    return json.loads(result.text)


# 根据场馆id获取内部的场地信息
def get_field_info(ggId):
    url = URL_BASE + "GymAction!getFieldinfo"
    field_params = {
        "ggId": ggId,
    }
    result = requests.post(url=url, headers=header, data=field_params)
    print('场地信息：'+result.text)


# 过滤找到符合要求的场地
def place_interval_filter(data, early_time, late_time, interval_num=4):
    # 每个元素都是一个list（表示某个场地编号的离散空闲时间）
    empty_place = []
    for time_row in data:
        temp = []
        for place in time_row:
            if place['status'] == 0 and place['ordId'] == -1:
                # 场地空闲且可被预约
                temp.append([place['fdId'], place['startTime'], place['endTime']])
                print(place['fdId'], place['startTime'], place['endTime'])
        empty_place.append(temp)
    print(empty_place)


# 根据fdId提交订单
# ggId表示体育馆id，ffId是场地分块id（该场馆各类运动统一编号）、fdId是场地id（所有场馆统一编号）
def submit_order(usrId, ggId, ffId, fdId, start_time, end_time):
    url = URL_BASE + "OrderAction!bookOrder?deposit=0.00"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_params = {
        "ggId": ggId,
        "ffId": ffId,
        "fdId": fdId,
        "usrId": usrId,
        "beginTime": start_time,
        "endTime": end_time,
        "ordTime": now,
        "payType": 2
    }
    result = requests.post(url=url, headers=header, data=order_params)
    print('预约结果：'+result.text)
    if result.text == -1:
        return False
    else:
        content = "{}元；{}；{}--{}".format(
            json.loads(result.text)["money"], start_time[0:10], start_time[-8:-3], end_time[-8:-3]
        )
        send_email(config.EMAIL_TO, '体育馆预约', content)
        # send_sms(config.SMS_TO_NUMBER, "测试短信")
        return True

if __name__ == "__main__":
    # 提取保持登录
    cookies = login(config.GYM_USER, config.GYM_PWD)
    usr_id = int(get_user_info(cookies)[-1]) + 5
    tomorrow = (datetime.date.today() + datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    data = get_place_data(usr_id, 4, 7, tomorrow, "00:00:00", "23:59:59")
    place_interval_filter(data, "18:00", "21:00", 4)
    # 工学部体育馆、羽毛球场、下一天、16:30、17:30
    # submit_order(usr_id, 4, 7, 57, tomorrow+" 16:30:00", tomorrow+" 17:30:00")

'''
if __name__ == "__main__":
    # 提取保持登录
    cookies = login(config.GYM_USER, config.GYM_PWD)
    usr_id = int(get_user_info(cookies)[-1]) + 5
    # 准备预约的日期
    date_reserve = (datetime.date.today() + datetime.timedelta(days=config.RESERVE_DATE)).strftime("%Y-%m-%d")
    # 18:00:00之前可以预约当天和下一天；之后可以预测当天、下一天、下下一天
    # 当前时间
    now = int(datetime.datetime.now().strftime("%H%M%S"))
    if now < 180000:
        # 只能预约当天和下一天
        t = datetime.datetime.now()
        st = '{}-{}-{} {}:{}:{}'.format(t.year,t.month,t.day,18,00,1)
        startTime = datetime.datetime.strptime(st, "%Y-%m-%d %H:%M:%S")
        print('休眠{}s'.format((startTime-t).seconds))
        for i in range((startTime-t).seconds):
            time.sleep(1)
            #当前时间是否达到17:59:59
            now = int(datetime.datetime.now().strftime("%H%M%S"))
            if(now > 175959):
                print('等待第{}个1s时break'.format(i))
                break
        print('休眠结束')
        # 工学部体育馆、羽毛球场、下一天、16:30、17:30
        if submit_order(usr_id, 4, 7, 57, date_reserve+" 16:30:00", date_reserve+" 17:30:00"):
            sys.exit("成功预约")
        else:
            # 重新筛选找到剩余场地
            pass
    else:
        # 工学部体育馆、羽毛球场、下一天、16:30、17:30
        if submit_order(usr_id, 4, 7, 57, date_reserve+" 16:30:00", date_reserve+" 17:30:00"):
            sys.exit("成功预约")
        else:
            # 重新筛选找到剩余场地
            pass
'''