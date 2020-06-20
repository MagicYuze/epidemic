import time
from epidemicShow import models


def testDateBase():
    obj = models.EpidemicInfo()
    obj.country_name = '美国'
    obj.add_num = 100
    obj.count_num = 100
    obj.cure_num = 100
    obj.death_num = 100
    obj.date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    obj.time = 10
    # 存数据
    obj.save()

    data1 = models.EpidemicInfo.objects.get(id = 1) #取id为1的数据
    data2 = models.EpidemicInfo.objects.filter(country_name = '美国') #取country_name为“美国”的数据集合
    for obj1 in data2:
        print(obj1.country_name.decode('utf-8'))

    print(obj.country_name)
