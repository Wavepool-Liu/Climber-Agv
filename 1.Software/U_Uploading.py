# -*- coding: utf-8 -*-
import oss2
import os


# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
auth = oss2.Auth('LTAI4G2NRbhj9MXBv7sqBUp8', 'TGy8O7FHKsDC4NJta4PQRCQu6RvEcj')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'imt-agv')


# # 必须以二进制的方式打开文件，因为需要知道文件包含的字节数。
# bucket.put_object_from_file('update/ADmodule.py', '/home/pi/AGV_Control/ADmodule.py')
# bucket.put_object_from_file('update/ADS1256.py', '/home/pi/AGV_Control/ADS1256.py')
# bucket.put_object_from_file('update/config.py', '/home/pi/AGV_Control/config.py')
# bucket.put_object_from_file('update/cWheel.py', '/home/pi/AGV_Control/cWheel.py')
# bucket.put_object_from_file('update/dataControl.py', '/home/pi/AGV_Control/dataControl.py')
# bucket.put_object_from_file('update/Func_Array.py', '/home/pi/AGV_Control/Func_Array.py')
# bucket.put_object_from_file('update/Gpio.py', '/home/pi/AGV_Control/Gpio.py')
# bucket.put_object_from_file('update/MainFunc.py', '/home/pi/AGV_Control/MainFunc.py')
# bucket.put_object_from_file('update/self_Serial.py', '/home/pi/AGV_Control/self_Serial.py')

bucket.put_object_from_file('update/U_Uploading.py', 'U_Uploading.py')
bucket.put_object_from_file('update/D_Downloading.py', 'D_Downloading.py')