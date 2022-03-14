#coding = utf-8
import time
import ADS1256
import RPi.GPIO as GPIO
import requests
import queue
import datetime
import json
import dataControl
import self_Serial


# 采样系统
class adSampling:
    @staticmethod
    def init_AD():      # AD初始化
        ADC = ADS1256.ADS1256()
        ADC.ADS1256_init()
        time.sleep(2)
        print("init AD successfully")
        return ADC

    @staticmethod   # 从通道获取AD数据
    def Rdata_ins(ADC, CfleshTimes,adChannel1,adChannel2,sampling_time):  # 读取数据
        maxrt = datetime.timedelta(seconds=sampling_time)
        list_data1 = []  # AD数据1
        list_data2 = []  # AD数据2
        Times = 0        # 获取AD数据次数
        currentClock = 0
        stop = datetime.datetime.now() + maxrt
        gear = 3
        while datetime.datetime.now() < stop:
            ADC_Value = ADC.ADS1256_GetAll()
            # time.sleep(0.05)
            list_data1.append(ADC_Value[adChannel1] * 5.0 / 0x7fffff)
            list_data2.append(ADC_Value[adChannel2] * 5.0 / 0x7fffff)
            Times = Times + 1
            if Times % CfleshTimes == 0:
                averangeData1 = 0
                averangeData2 = 0
                for i in range(Times - CfleshTimes, Times):
                    averangeData1 = list_data1[i] + averangeData1
                    averangeData2 = list_data2[i] + averangeData2
                gear, currentClock = dataControl.get_gear_Clock(2.442451549663329,3.74975443876836, 2.4310209966922973,2.3892434306037513,averangeData1/CfleshTimes,averangeData2/CfleshTimes)
                # print(averangeData1/CfleshTimes, averangeData2/CfleshTimes)
            else:
                pass
        return gear, currentClock, list_data1, list_data2

    @staticmethod     # 将数据写入本地TXT
    def Wdata_Text(list_data):
        with open("AD_data.txt", "w") as file:
            file.close()  # 清空文件夹
        with open("AD_data.txt", "a+") as file:
            file.write(str(list_data))
        print("Write data successfully!")

    @staticmethod    # 将数据发到MT数据库中
    def send_mongodb(app_id,appName,ADdata,refreshTime,sampling_time,l_number,low):
        json_state = {
            "app_id":app_id,
            "appName":appName,
            "ADdata":ADdata,
            "refreshTime":refreshTime,
            "sampling_time":sampling_time,
            "l_number":l_number,
            "low":low
        }
        get_state_json = json.dumps(json_state)  #打包JSON格式
        try:
            requests.post("https://imooc.imitee.com:10086/set_ADdata", data=get_state_json)
        except:
            print("Fail")



if __name__ == "__main__":
    # app_id1 = "1"         # 设备号1
    # app_id2 = "2"         # 设备号2
    # sampling_time = 0.3   # 采样时间
    # l_number = 3          # 阶数
    # appName1 = "传感器x"
    # appName2 = "传感器y"
    # refreshTime = 1       #网页刷新时间
    # low = 25              #低通滤波器阈值
    adChannel1 = 3        #采样通道4
    adChannel2 = 2        #采样通道3
    CrefreshTimes = 2     #时钟更新间隔
    sampling_time = 0.3   #AD采样总间隔
    grand_clock = 0        #爷钟点
    father_clock = 0       #父钟点
    MaxSpeed = 4000       #最高速度
    ADC = adSampling().init_AD()           #ADC模块初始化
    ser = self_Serial.get_serial().get_usb_port() #串口初始化
    while True:
        # 获取挡位，当前钟点，俩通道数据
        gear, current_Clock, list_data1, list_data2 = adSampling().Rdata_ins(ADC, CrefreshTimes, adChannel1, adChannel2, sampling_time)
        # 通过钟点状态求得当前速度
        currentSpeed = dataControl.speed_control(gear, grand_clock, father_clock, current_Clock, MaxSpeed)
        # 封装成485数据发送出去
        # SendData = dataControl.clock_SendHex(ser, current_Clock, "00 06 00 66", currentSpeed)
        grand_clock = father_clock
        father_clock = current_Clock
        print("\r", current_Clock, end = "")
        # 云端显示采样数据
        # rate_test.send_mongodb(app_id1, appName1, list_data1,refreshTime,sampling_time,l_number,low)
        # rate_test.send_mongodb(app_id2, appName2, list_data2,refreshTime,sampling_time,l_number,low)