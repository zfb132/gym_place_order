#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: 'zfb'
# time: 19-08-26 10:13

# 体育馆预约系统的账户配置
GYM_USER = 'admin132'
GYM_PWD = '123demo'

# 预约场馆id
GGID = 4
# 预约场地分块id（该场馆各类运动统一编号）
FFID = 7
# 场地id（所有场馆统一编号）
FDID = 57

# 预约日期：0表示当天；1表示下一天；2表示下下天
RESERVE_DATE = 2
# 预约最早开始时间
RESERVE_START_TIME = "18:00"
# 预约最晚结束时间
RESERVE_START_TIME = "21:00"
# 预约时长（每30分钟作为一个单位）
RESERVE_DURATION = 4

# twilio发信账户配置
SMS_SID = 'ACb770c5f63aac91c44d97891234567890'
SMS_TOKEN = '42b1294966799e965883181234567890'
SMS_FROM_NUMBER = '+12512123456'

# 接收短信通知的手机号
SMS_TO_NUMBER = '+8613212345678'

# 邮箱发信账户配置
EMAIL_FROM = 'gym@example.cn'
EMAIL_PWD = '123demo'

# 接受预约成功信息的移动139邮箱账号
EMAIL_TO = 'admin132@139.com'
