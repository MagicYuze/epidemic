from datetime import time

from django.http import HttpResponse
from django.test import TestCase

from django.utils.datastructures import MultiValueDictKeyError

from epidemicShow import models


class MyTests(TestCase):
    # 没有建测试数据库的权限，暂时没有解决……
    # 此处只是把代码搬过来了而已……
    def testDateBase(request):
        flag = True
        response = HttpResponse()
        response["Content-Type"] = "text/javascript"
        try:
            jsonpCallback = request.GET["jsonpCallback"]
        except MultiValueDictKeyError:
            flag = False

        obj = models.EpidemicInfo()
        obj.country_name = '美国'
        obj.add_num = 100
        obj.count_num = 100
        obj.cure_num = 100
        obj.death_num = 100
        obj.date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        obj.time = 10
        # 存数据
        # obj.save()

        data2 = models.EpidemicInfo.objects.filter(country_name = '美国') #取country_name为“美国”的数据集合
        for obj1 in data2:
            print(obj1.country_name)

        print(obj.country_name)

        json_str = 'test'
        if flag:
            response.write(jsonpCallback + "(" + json_str + ")")
        else:
            response.write(json_str)
        return response
