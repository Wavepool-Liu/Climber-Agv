# -*- coding: utf-8 -*-
import oss2


# 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录RAM控制台创建RAM账号。
auth = oss2.Auth('LTAI4G2NRbhj9MXBv7sqBUp8', 'TGy8O7FHKsDC4NJta4PQRCQu6RvEcj')
# Endpoint以杭州为例，其它Region请按实际情况填写。
bucket = oss2.Bucket(auth, 'http://oss-cn-beijing.aliyuncs.com', 'imt-agv')
# 下载OSS文件到本地文件。如果指定的本地文件存在会覆盖，不存在则新建。

bucket.get_object_to_file('update/ADS1256.py', 'ADS1256.py')
bucket.get_object_to_file('update/config.py', 'config.py')
bucket.get_object_to_file('update/cWheel.py', 'cWheel.py')
bucket.get_object_to_file('update/dataControl.py', 'dataControl.py')
bucket.get_object_to_file('update/Func_Array.py', 'Func_Array.py')
bucket.get_object_to_file('update/Gpio.py', 'Gpio.py')
bucket.get_object_to_file('update/MainFunc.py', 'MainFunc.py')
bucket.get_object_to_file('update/self_Serial.py', 'self_Serial.py')

bucket.get_object_to_file('update/main.py', 'main.py')