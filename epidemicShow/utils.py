import datetime
import json
import re
import time
import urllib


# 切割"截至至x月x日x时x分"中的数字，返回年月日的变量
def handleDateTimeStr(dateTimeStr):
    numList = re.findall(r'\d+', dateTimeStr)
    dateStr = time.strftime('%Y-', time.localtime(time.time())) + numList[0] + '-' + numList[1]
    # print(dateStr)
    return dateStr


# 获取当天的日期 格式为YYYY-mm-dd
def getTodayDate():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


# 根据时间戳拼接生成请求新浪实施疫情json文件的url链接
def getUrl():
    t = time.time()
    num = int(round(t * 1000))
    url_temp = "https://gwpre.sina.cn/interface/fymap2020_data.json?_="+str(num)+"&callback=dataAPIData"
    return url_temp


# 请求url获取json文件中的内容
def getInfo():
    url = getUrl()
    resp = urllib.request.urlopen(url)
    body = resp.read().decode('utf-8')
    json_str = body.split('(')[1].split(')')[0].strip()
    json_data = json.loads(json_str)  # 将JSON 字符串解码为 Python 对象
    return json_data


# 字符串转日期
def str2date(dateStr):
    return datetime.datetime.strptime(dateStr,'%Y-%m-%d').date()


# 日期转字符串
def date2str(date):
    return date.strftime("%Y-%m-%d")  # date形式转化为str

# 获取含当前日期的七天前的日期
def getDateBefore7Days(date):
    now_time = date
    yes_time = now_time + datetime.timedelta(days=-6)
    yes_time_nyr = yes_time.strftime('%Y-%m-%d')
    return yes_time_nyr