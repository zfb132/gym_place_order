# 体育馆预约系统的使用
## 准备工作
1. 基于Python3编写，因此需要首先[安装Python3](https://www.python.org/downloads/ "python3")
2. 依赖`requests、twilio`两个库，前者用于网络请求，后者用于发送手机短信（免费[注册twilio](https://www.twilio.com/ "twilio")后即可使用），运行前需要先安装依赖的库（`-i`参数用于指定`pypi`的源，国内[清华的镜像源](https://mirrors.tuna.tsinghua.edu.cn/ "tsinghua")下载速度还是很快的）  
`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests twilio`
3. 重命名`config.example.py`为`config.py`，修改里面的个人配置，注意自己申请twilio应用
## 运行程序
开始预约，系统会自动预约指定场地，打开终端切换到当前目录并输入：  
`python3 reserve.py`  
失败则退出，成功会发送短信通知或邮件通知
## 全自动化
使用Linux系统的定时任务`crontab`来实现（也可以自己用Windows实现），在终端编辑定时文件：  
`crontab -e`  
在打开的文件中添加一行内容：  
`44 22 * * * /usr/bin/python3 ~/gym_place_order/reserve.py`  
这句话意思是：每天的22:45分开始运行本程序（假设本程序位于主目录下，根据实际位置自行更改`py`文件路径）  
**声明：本代码仅供测试，请勿用于大量并发请求，否则后果自负**

# 体育馆预约系统部分接口
## 1. 登录系统
url：  http://gym.whu.edu.cn/loginAction!UserLogin  
登录方式： post  
登录参数： `name=admin132&password=123demo`  
返回结果：  
```json
{
    "rem":"5312e33ad2d0007cfdaf09da3eeb6993",
    "status":-1
}
```
其中，`status=-1`表示成功
## 2. 获取个人信息
url： http://gym.whu.edu.cn/UserAction!getUserInfoToMobile  
登录方式： post  
登录参数： `usrId=10876`（用户id，**可选**参数）  
返回结果：
```json
[
    "admin132",null,"学生用户","myemail@example.com",
    "武汉大学","15876541234","1988-11-24","6","1","10871"
]
```
元素的含义依次是：用户名、未知、身份、邮箱、学校、电话、生日、rlId、ssId、upId（**注意不是usrId**）
## 3. 获取所有场馆信息
url： http://gym.whu.edu.cn/GymAction!getGymPositionInfo  
请求方式： post  
参数：无  
返回内容：
```json
[
    {
        "fieldLabel":["羽毛球","乒乓球","网球"],
        "g_coordinate":[114.362331,30.527656],
        "ggId":1,
        "name":"信息学部体育馆",
        "ssId":1
    },
    {
        "fieldLabel":["羽毛球","网球","乒乓球","形体"],
        "g_coordinate":[114.359696,30.53828],
        "ggId":2,
        "name":"风雨体育馆",
        "ssId":1
    },
    {
        "fieldLabel":["形体","羽毛球","网球","乒乓球"],
        "g_coordinate":[114.366602,30.543993],
        "ggId":4,
        "name":"工学部体育馆",
        "ssId":1
    },
    {
        "fieldLabel":["排球"],
        "g_coordinate":[114.366795,30.543757],
        "ggId":5,
        "name":"工学部体育馆B馆",
        "ssId":1
    },
    {
        "fieldLabel":["羽毛球","乒乓球","网球"],
        "g_coordinate":[114.357756,30.553538],
        "ggId":7,
        "name":"医学部体育馆",
        "ssId":1
    }
]
```
## 4. 获取指定场馆粗略信息
url： http://gym.whu.edu.cn/GymAction!getFieldinfo  
请求方式： post  
参数： `ggId=4`（场馆id）  
返回内容：
第一个元素表示ffId，第二个元素表示全称，第三个元素表示简称，第四个元素表示场地个数
```json
[
    [7,"工学部体育馆羽毛球场","羽毛球",10,0],
    [8,"工学部体育馆乒乓球室","乒乓球",14,0],
    [9,"工学部体育馆形体房","形体",2,0],
    [15,"工学部网球场","网球",5,0]
]
```
其他场馆的信息：
```json
[
    [1,"信息学部体育馆羽毛球场","羽毛球",9,0],
    [2,"信息学部体育馆乒乓球场","乒乓球",14,0],
    [3,"信息学部体育馆网球场","网球",3,0]
],
[
    [4,"风雨体育馆羽毛球场","羽毛球",6,0],
    [5,"风雨体育馆乒乓球室","乒乓球",14,0],
    [6,"风雨体育馆形体房","形体",1,0],
    [17,"风雨网球场","网球",3,0]
],
[
    [11,"工学部体育馆排球场","排球",1,0]
],
[
    [13,"医学部体育馆羽毛球场","羽毛球",12,0],
    [14,"医学部体育馆乒乓球室","乒乓球",5,0],
    [16,"医学部网球场","网球",2,0]
]
```
## 5. 获取指定场馆详细信息
url：  http://gym.whu.edu.cn/OrderQueryAction!getGymItems  
请求方式： post  
参数： `ggId=4&date=2019-08-26`（场馆id、预约日期）  
返回内容：
```json
{
    "afternoon":[
        "12:00-12:30","12:30-13:00","13:00-13:30","13:30-14:00",
        "14:00-14:30","14:30-15:00","15:00-15:30","15:30-16:00",
        "16:00-16:30","16:30-17:00","17:00-17:30","17:30-18:00"
    ],
    "evening":[
        "18:00-18:30","18:30-19:00","19:00-19:30","19:30-20:00",
        "20:00-20:30","20:30-21:00"
    ],
    "fieldInfo":[
        ["7","羽毛球","0"],["8","乒乓球","0"],
        ["9","形体","0"],["15","网球","0"]
    ],
    "midnight":[],
    "morning":[
        "08:30-09:00","09:00-09:30","09:30-10:00","10:00-10:30",
        "10:30-11:00","11:00-11:30","11:30-12:00"
    ]
}
```
## 6. 获取某天的可用时间段
url：  http://gym.whu.edu.cn/OrderQueryAction!getMPointPeriod  
登录方式： post  
登录参数： `ggId=4&ffId=7&usrId=10876&date=2019-08-21&startTime=00%3A00%3A00&endTime=23%3A59%3A00`  
其中，ggId表示场馆id，ffId是场地分块id，`%3A`其实是`:`的url编码（代码里可以直接用`:`）  
返回json结果：
```json
[
    {
        "afId":-1,
        "deposit":0.00,
        "divNum":1,
        "endTime":"09:00",
        "fdId":50,
        "money":3.50,
        "ordId":-1,
        "startTime":"08:30",
        "status":1
    },
    {
        "afId":-1,
        "deposit":0.00,
        "divNum":2,
        "endTime":"09:00",
        "fdId":51,
        "money":3.50,
        "ordId":-1,
        "startTime":"08:30",
        "status":0
    }
]
```
其中，`status=0`表示当前时间段**可能**可以预约，`status=1`表示不可预约；`ordID=-1`表示**可能**可以预约，`ordId=其他`表示有人正在预约；fdId是场地id（所有场馆统一编号）；money表示当前时间段的价格；divNum表示场地编号；可预约时间段需满足`status=0&&ordId=-1`
## 7. 提交订单
url：  http://gym.whu.edu.cn/OrderAction!bookOrder?deposit=0.00  
请求方式： post  
参数： `fdId=57&beginTime=2019-08-26+16%3A00%3A00&endTime=2019-08-26+17%3A00%3A00&ffId=7&ggId=4&usrId=10876&money=10.00&ordTime=2019-08-26+10%3A29%3A10&payType=2`  
返回结果：
```json
{
    "money":10.00,
    "ordId":30051,
    "payNo":"1566786550000108761",
    "piId":40887,
    "status":0,
    "type":1,
    "usrId":10876
}
```
其中，payNo的值1566786550000**10876**1加粗部分是usrId、之前是unix时间戳
