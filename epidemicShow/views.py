from django.shortcuts import redirect

import json

from django.http import HttpResponse
from django.shortcuts import render
import urllib.request

from django.utils.datastructures import MultiValueDictKeyError
from epidemicShow import models
from epidemicShow.utils import getTodayDate, handleDateTimeStr, getInfo, getUrl, str2date, getDateBefore7Days, date2str

global jsonpCallback


# 封装获取各种类型数据的全部数据的接口（未使用数据库版本）
def getAllNumOld(request):
    # 根据请求接口的地址 判断请求的数据类型
    requestPath = request.path_info.replace('/', '')
    value = ''  # 用于记录json数据中的某个字段
    if requestPath == "addNum":
        value = 'conadd'
    elif requestPath == "countNum":
        value = 'value'
    elif requestPath == "cureNum":
        value = 'cureNum'
    elif requestPath == "deathNum":
        value = 'deathNum'

    # 用于标记是不是Ajax使用Jsonp发送的异步请求 True为是
    flag = True
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    try:
        jsonpCallback = request.GET["jsonpCallback"]
    except MultiValueDictKeyError:
        flag = False

    json_data = getInfo()

    # 新建一个字典 提取爬取的json文件中的有用信息 并返回
    dictAll = {}
    for i in range(len(json_data['data']['worldlist'])):
        if requestPath == "addNum":
            # 中国的数据和外国的数据不太一样 在worldlist里没有中国的新增病例数据 所以分开设置
            if json_data['data']['worldlist'][i]['name'] == '\u4e2d\u56fd':
                allNum = int(json_data['data']['add_daily']['addcon_new'].split('+')[1])
            else:
                # 其他国家新增人数的数据
                allNum = int(json_data['data']['worldlist'][i][value])
        else:
            # 各种人数的数据
            allNum = int(json_data['data']['worldlist'][i][value])

            # 总的字典的 键为国名 值为各种人数的值
        dictAll[json_data['data']['worldlist'][i]['name']] = allNum
    # 字典数据排序 并 转化为json数据
    dictAll = sorted(dictAll.items(), key=lambda x: x[1], reverse=False)
    newDict = dict(dictAll)
    # 记录当前时间 前端处理时注意区分键为time的键值对
    newDict['time'] = json_data['data']['times']
    responseData = json.dumps(newDict)
    # print(responseData)

    if flag:
        response.write(jsonpCallback + "(" + responseData + ")")
    else:
        response.write(responseData)
    return response


# 封装获取各种类型数据的全部数据的接口（使用数据库版本）
def getAllNum(request):
    # 根据请求接口的地址 判断请求的数据类型
    requestPath = request.path_info.replace('/', '')
    # print(requestPath)

    # 记录请求的数据的日期 如果没带这个参数则查当天的记录
    try:
        reqDate = request.GET["date"]
    except MultiValueDictKeyError:
        reqDate = getTodayDate()

    # 用于标记是不是Ajax使用Jsonp发送的异步请求 True为是
    flag = True
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    try:
        jsonpCallback = request.GET["jsonpCallback"]
    except MultiValueDictKeyError:
        flag = False

    # 查数据库要查询的那天是否有记录 没有的话先更新数据库 然后在查，有的话直接保留这个结果
    searchData = models.EpidemicInfo.objects.filter(date=reqDate)
    # 理论上不会没数据，但是现在没有定时任务，所以在这里如果没数据就同步一下数据库
    if len(searchData) == 0:
        # 如果查询的不是今天的也没数据，那就说明是之前的数据。没有的话就也直接返回今天的
        if reqDate != getTodayDate():
            reqDate = getTodayDate()
        # print('执行到这里了')
        syncDataBase(request)
        searchData = models.EpidemicInfo.objects.filter(date=reqDate)

    # 新建一个字典 保存数据库中的信息 并返回
    dictAll = {}
    # 根据查询的类型获取字段的值
    for countryData in searchData:
        if requestPath == "addNum":
            allNum = countryData.add_num
        elif requestPath == "countNum":
            allNum = countryData.count_num
        elif requestPath == "cureNum":
            allNum = countryData.cure_num
        elif requestPath == "deathNum":
            allNum = countryData.death_num
        else:
            allNum = 0

        # 总的字典的 键为国名 值为各种人数的值
        dictAll[countryData.country_name] = allNum
    # 字典数据排序 并 转化为json数据
    dictAll = sorted(dictAll.items(), key=lambda x: x[1], reverse=False)
    newDict = dict(dictAll)
    # 记录当前时间 前端处理时注意区分键为time的键值对
    newDict['time'] = reqDate
    responseData = json.dumps(newDict)

    # 如果不是Ajax的jsonp的异步请求就正常返回Json数组，如果是Ajax就要加jsonpCallback
    if flag:
        response.write(jsonpCallback + "(" + responseData + ")")
    else:
        response.write(responseData)
    return response


# 封装获取各种类型数据的Top7国家数据的接口（为三维视图准备）
def getTopSevenData(request):
    # 根据请求接口的地址 判断请求的数据类型
    requestPath = request.path_info.replace('/', '')
    # print(requestPath)

    # 两个日期用于在数据库中查询记录
    # 获取当前日期
    endDate = getTodayDate()
    # 获取七天前的日期
    startDate = getDateBefore7Days(str2date(endDate))

    # 用于标记是不是Ajax使用Jsonp发送的异步请求 True为是
    flag = True
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    try:
        jsonpCallback = request.GET["jsonpCallback"]
    except MultiValueDictKeyError:
        flag = False

    # 查数据库要查询的那天是否有记录 没有的话先更新数据库 然后在查，有的话直接保留这个结果
    checkData = models.EpidemicInfo.objects.filter(date=endDate)
    # 理论上不会没数据，但是现在没有定时任务，所以在这里如果没数据就同步一下数据库
    if len(checkData) == 0:
        # 如果查询的不是今天的也没数据，那就说明是之前的数据。没有的话就也直接返回今天的
        if endDate != getTodayDate():
            endDate = getTodayDate()
        syncDataBase(request)

    # 测试用
    endDate = '2020-06-21'
    # 查询七天的所有记录
    searchData = models.EpidemicInfo.objects.filter(date__range=(startDate, endDate))

    # 迭代所有记录 求各国所查的7天数据的总和 存到一个dict中 为接下来排序 筛选top7做准备
    dictCountAllNum = {}  # 记录各国数据的7天总和
    for oneData in searchData:
        if oneData.country_name not in dictCountAllNum:
            if requestPath == "addNumTopSeven":
                dictCountAllNum[oneData.country_name] = oneData.add_num
            elif requestPath == "countNumTopSeven":
                dictCountAllNum[oneData.country_name] = oneData.count_num
                # if oneData.country_name == '美国':
                #   print(date2str(oneData.date) + str(dictCountAllNum[oneData.country_name]))
            elif requestPath == "cureNumTopSeven":
                dictCountAllNum[oneData.country_name] = oneData.cure_num
            elif requestPath == "deathNumTopSeven":
                dictCountAllNum[oneData.country_name] = oneData.death_num
        else:
            if requestPath == "addNumTopSeven":
                dictCountAllNum[oneData.country_name] += oneData.add_num
            elif requestPath == "countNumTopSeven":
                dictCountAllNum[oneData.country_name] += oneData.count_num
                # if oneData.country_name == '美国':
                #     print(date2str(oneData.date) + str(dictCountAllNum[oneData.country_name]))
            elif requestPath == "cureNumTopSeven":
                dictCountAllNum[oneData.country_name] += oneData.cure_num
            elif requestPath == "deathNumTopSeven":
                dictCountAllNum[oneData.country_name] += oneData.death_num

    # 字典数据排序 并 转化为json数据
    dictCountAllNum = sorted(dictCountAllNum.items(), key=lambda x: x[1], reverse=True)
    newDict = dict(dictCountAllNum)
    count = 0  # 要7个数据

    finalDict = {}  # 在新建一个dict存最终结果 先找出排序后的字典中的前7个key，依次存入新字典
    # 新建一个临时字典，用于后面存每天的数据
    tempDict = {}
    for k in newDict:
        # print(k+"-"+str(newDict[k]))
        finalDict[k] = tempDict
        count = count + 1
        if count == 7:
            break
    # print(finalDict)

    # 再次遍历查询到的记录 把每个国家每天的记录分别存储到字典中
    for countryName in finalDict:
        tempDict = {}
        for oneData in searchData:
            if oneData.country_name == countryName:
                if requestPath == "addNumTopSeven":
                    tempDict[date2str(oneData.date)] = oneData.add_num
                elif requestPath == "countNumTopSeven":
                    tempDict[date2str(oneData.date)] = oneData.count_num
                elif requestPath == "cureNumTopSeven":
                    tempDict[date2str(oneData.date)] = oneData.cure_num
                elif requestPath == "deathNumTopSeven":
                    tempDict[date2str(oneData.date)] = oneData.death_num
                finalDict[oneData.country_name] = tempDict
    # print(finalDict)
    responseData = json.dumps(finalDict)

    # 如果不是Ajax的jsonp的异步请求就正常返回Json数组，如果是Ajax就要加jsonpCallback
    if flag:
        response.write(jsonpCallback + "(" + responseData + ")")
    else:
        response.write(responseData)
    return response


# 获取各国所有数据（新增、累积、治愈、死亡），并根据累计人数排序 筛选出Top5返回
# 此接口没有完成，暂时没有使用到
def getInfosByCountry(request):
    flag = True
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    try:
        jsonpCallback = request.GET["jsonpCallback"]
    except MultiValueDictKeyError:
        flag = False

    json_data = getInfo()
    # 新建一个字典 提取爬取的json文件中的有用信息 并返回
    dictAll = {}

    for i in range(len(json_data['data']['worldlist'])):
        # 记录新增人数的数据
        # 中国的数据和外国的数据不太一样 在worldlist里没有中国的新增病例数据 所以分开设置
        if json_data['data']['worldlist'][i]['name'] == '\u4e2d\u56fd':
            addNum = int(json_data['data']['add_daily']['addcon_new'].split('+')[1])
        else:
            # 其他国家新增人数的数据
            addNum = int(json_data['data']['worldlist'][i]['conadd'])

        # 记录累积人数的数据
        countNum = int(json_data['data']['worldlist'][i]['value'])

        # 记录治愈人数的数据
        cureNum = int(json_data['data']['worldlist'][i]['value'])

        # 记录死亡人数的数据
        deathNum = int(json_data['data']['worldlist'][i]['value'])

        # 记录各种数据的字典
        dictTemp = {}
        dictTemp['addNum'] = addNum
        dictTemp['countNum'] = countNum
        dictTemp['cureNum'] = cureNum
        dictTemp['deathNum'] = deathNum
        # 总的字典的 键为国名 值为各种类型的数值
        dictAll[json_data['data']['worldlist'][i]['name']] = dictTemp

    # ---------------------------------------------------------------
    # 根据四个值的和进行排序 并筛选出 前5个国家
    pass
    responseData = None
    # ---------------------------------------------------------------

    if flag:
        response.write(jsonpCallback + "(" + responseData + ")")
    else:
        response.write(responseData)
    return response


# 请求url获取json文件中的内容（测试用）
def getInfos(request):
    flag = True
    response = HttpResponse()
    response["Content-Type"] = "text/javascript"
    try:
        jsonpCallback = request.GET["jsonpCallback"]
    except MultiValueDictKeyError:
        flag = False
    url = getUrl()
    resp = urllib.request.urlopen(url)
    body = resp.read().decode('utf-8')
    json_str = body.split('(')[1].split(')')[0].strip()
    if flag:
        response.write(jsonpCallback + "(" + json_str + ")")
    else:
        response.write(json_str)
    return response


# 将数据同步至数据库中（但是这个没有做自动化实时调用 需要手动访问接口/syncDataBase）
# 简单来说就是Django的定时任务没整明白……
def syncDataBase(request):
    saveOrUpdate = False
    json_data = getInfo()
    # 获取json数据中“截至到……”中的日期
    dateStr = handleDateTimeStr(json_data['data']['times'])
    # 测试用
    # dateStr = '2020-06-21'
    # 查询数据库 看看当前记录的日期是否在数据库中
    checkTime = models.EpidemicInfo.objects.filter(date=dateStr)
    # 如果没有记录 则说明没有存到数据库中 则进行save 如果有记录则进行update
    if len(checkTime) == 0:
        saveOrUpdate = True
    for i in range(len(json_data['data']['worldlist'])):
        # 获取国家名称
        countryName = json_data['data']['worldlist'][i]['name']

        # 记录新增人数的数据
        # 中国的数据和外国的数据不太一样 在worldlist里没有中国的新增病例数据 所以分开设置
        if countryName == '\u4e2d\u56fd':
            addNum = int(json_data['data']['add_daily']['addcon_new'].split('+')[1])
        else:
            # 其他国家新增人数的数据
            addNum = int(json_data['data']['worldlist'][i]['conadd'])

        # 记录累积人数的数据
        countNum = int(json_data['data']['worldlist'][i]['value'])

        # 记录治愈人数的数据
        cureNum = int(json_data['data']['worldlist'][i]['cureNum'])

        # 记录死亡人数的数据
        deathNum = int(json_data['data']['worldlist'][i]['deathNum'])

        if saveOrUpdate:
            countryInfo = models.EpidemicInfo()
            countryInfo.country_name = countryName
        else:
            countryInfo = models.EpidemicInfo.objects.filter(date=dateStr).get(country_name = countryName)

        countryInfo.add_num = addNum
        countryInfo.count_num = countNum
        countryInfo.cure_num = cureNum
        countryInfo.death_num = deathNum
        countryInfo.date = dateStr

        countryInfo.save()

    return redirect('/')


# 显示首页
def showIndex(request):
    return render(request, 'index.html')
