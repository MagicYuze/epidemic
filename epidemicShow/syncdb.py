# -*- coding:UTF-8 -*-
# Linux中安装crontab 每天执行一次该文件 用于同步数据库
# 因为Django的定时任务没有搞定，所以暂时使用此方法
# Linux中定时任务的命令为：
# crontab -e
# 后添加定时任务 每天09：30执行一次
#               每天23：30执行一次
# 30 9 * * * /usr/local/bin/python3 /usr/docker/python3/epidemic_new/epidemicShow/syncdb.py
# 30 23 * * * /usr/local/bin/python3 /usr/docker/python3/epidemic_new/epidemicShow/syncdb.py

import urllib.request

url = "http://epidemic.magicy.fun/syncDataBase"
resp = urllib.request.urlopen(url)