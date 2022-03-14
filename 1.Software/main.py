# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO
import time, datetime
import threading
import self_Serial
import dataControl
import ADmodule
import Func_Array
import cWheel
import Gpio
import MainFunc
import os


# 线程1  检测串口插拔恢复程序(ser)
def D_Serial():
    global ser
    while True:
        if ser is None:   # 串口拔出后尝试重连
            print("error")
            ser = self_Serial.get_serial().get_usb_port()
            continue
        else:
            ser = self_Serial.get_serial().get_usb_port()
            continue


# 线程2  循环发送485协议数据                   (ser, LSpeed, RSpeed, sampling_time)
def S_485Hex():
    global ser
    global LSpeed, RSpeed,SendData
    while True:
        if ser is None:
            continue
        else:
            SendData = dataControl.Send_485Hex(ser, "00 06 00 66", LSpeed, RSpeed)
            time.sleep(sampling_time)


# 线程3  持续从手柄获取                       (handle_speed=Func(Maxspeed), C_Clock, gear)
def G_ADhandle():
    global ADC, CrefreshTimes, adChannel1, adChannel2, sampling_time  # 输入参数
    global ADgear, ADclock, list_data1, list_data2,Clock,handle_speed
    global ADgrand_clock, ADfather_clock, ADhandle_speed, Maxspeed, appENA
    adChannel1 = 3
    adChannel2 = 2
    CrefreshTimes = 8
    ADhandle_speed = 0
    ADclock = ADfather_clock = ADgrand_clock = ADhandle_speed = 0  # 赋初值
    while True:
        ADgear, ADclock, list_data1, list_data2 = ADmodule.adSampling().Rdata_ins(ADC, CrefreshTimes, adChannel1, adChannel2, sampling_time)
        ADgrand_clock = ADfather_clock
        ADfather_clock = ADclock
        ADhandle_speed = dataControl.speed_control(ADgear, ADgrand_clock, ADfather_clock, ADclock, Maxspeed)
        handle_speed = ADhandle_speed
        Clock = ADclock
        # print("handle_speed: ", handle_speed, "clock: ", ADclock)




# MQTT: 当收到关于客户订阅的主题的消息时调用。    (handle_speed=Func(Maxspeed), C_Clock, gear)
def on_message(client, userdata, msg):
    global data,state
    MSG = str(msg.payload, encoding='utf-8')
    if MSG[0:3] == "os-":
        try:
            data = os.popen(MSG[3:]).read()
            client.publish("AgvServer", "OS:  " + str(data))
        except:
            client.publish("AgvServer", "OS Error")
    else:
        try:
            if MSG == "gpio":
                IOstate = "Gpio: B1(模式切换）:"+ str(GPIO.input(IO.B1))+", B2(原地右转): "+ str(GPIO.input(IO.B2))+", B3(紧急制动): "+ str(GPIO.input(IO.B3))+", GTC(原地左转): "+ str(GPIO.input(IO.GTC))
                client.publish("AgvServer", state + "   " + IOstate)
                IOstate = "Gpio: M1:" + str(GPIO.input(IO.M1)) + ", M2: " + str(GPIO.input(IO.M2)) + ", GRAVETY(重力传感供电): " + str(GPIO.input(IO.GRAVETY))
                client.publish("AgvServer", IOstate)
                pass
            elif MSG in globals():
                client.publish("AgvServer", MSG + ": " + str(eval(MSG)))
            else:
                client.publish("AgvServer", "error")
        except:
            pass


# MQTT: 当代理响应连接请求时调用。
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("AgvClient", qos=0) # 订阅主题
    client.publish("AgvICU", "Agv1 Connected")

# MQTT: 当与代理断开连接时调用
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# MQTT: 初始化客户端函数
def client_main():
    HOST = "47.107.148.165"  # 设置Ip
    PORT = 1883  # 设置端口号
    client_id = "AGV1"
    client = mqtt.Client(client_id)
    client.on_connect = on_connect  # 启动订阅模式
    client.on_disconnect = on_disconnect  # 启动订阅模式
    client.on_message = on_message  # 接收消息

    # 设置要发送给代理的遗嘱。 如果客户端断开而没有调用disconnect（），代理将代表它发布消息。
    client.will_set(topic="AgvICU", payload="Agv1 already dissconnected", qos=0, retain=True)
    client.connect(HOST, PORT, 1)  # 链接
    # client.loop_forever()            # 以forever方式阻塞运行
    client.loop_start()  # 若主线程死循环，则采用这种方式


# Main
if __name__ == "__main__":
    # 启动Mqtt Client端
    try:
        client_main()
    except:
        pass
    # 全局变量初始化
    APPgear = ADgear = Maxspeed = ADhandle_speed = handle_speed = APPhandle_speed = LSpeed = RSpeed = ADclock = APPclock = Clock = father_clock = grand_clock = 0
    Max_Cspeed = 200     # 最大爬坡速度
    Max_Rspeed = 3000    # 最大平路速度
    sampling_time = 0.3  # 采样发送时间
    state = "系统刚启动"
    # 模式变量初始化
    Mod_road = 1   # 平路模式
    Mod_climb = 0  # 爬坡模式

    # 刹车变量初始化
    B_val = True


    # Gpio/Ser/手柄初始化
    ser = self_Serial.get_serial().get_usb_port()  # 串口初始化
    ADC = ADmodule.adSampling.init_AD()  # ADC模块初始化
    Mqttstart = datetime.datetime.now()

    # 面向对象初始化
    Fmain = MainFunc.MainFunc()
    Botton = cWheel.cWheel()
    IO = Gpio.AGVGpio()
    IO.Gpio_Init()

    # 启动线程1 2 3
    t1 = threading.Thread(target=D_Serial).start()
    t2 = threading.Thread(target=S_485Hex).start()
    t3 = threading.Thread(target=G_ADhandle).start()
    # t4 = threading.Thread(target=MqttClient).start()
    while True:
        try:
            if Fmain.U_break(IO.B3, IO.BRK, IO.ENA, B_val) is False:
                Maxspeed = 0
                LSpeed = RSpeed = 0
                state = "刹车状态"
                # print("刹车状态")
                B_val = False
                continue
            else:
                if B_val is True:
                    Maxspeed = 0
                    continue
                else:
                    pass
                pass
            if Fmain.U_FSwichMod(IO.B1, IO.M1, IO.M2) is True:
                state = "模式转换"
                # print("模式转换")
                Maxspeed = 0
                LSpeed = RSpeed = 0
                continue
            if GPIO.input(IO.B1) is GPIO.HIGH:
                if Botton.check_LRbotton(IO.GTC, IO.B2) is not False:
                    # 原地左转右转按钮
                    Maxspeed = 0
                    LSpeed, RSpeed = Botton.turn_L_R(IO.GTC, IO.B2)
                    state = "原地左右转，左轮："+str(LSpeed)+",右轮："+str(RSpeed)
                    # print("左右转")
                    continue
                else:
                    # 平路操作
                    # print("平路")
                    if B_val is True:
                        Maxspeed = 0
                    else:
                        Maxspeed = Max_Rspeed
                    state = "平路模式，左轮："+str(LSpeed)+",右轮："+str(RSpeed)
                    LSpeed, RSpeed = Fmain.Func_road(ADgear, handle_speed, Clock, IO.D1, IO.D2, IO.D3, IO.D4)
                    continue
            if GPIO.input(IO.B1) is GPIO.LOW:
                # 爬坡操作
                # print("爬坡模式")
                if B_val is True:
                    Maxspeed = 0
                else:
                    Maxspeed = Max_Cspeed
                state = "爬坡模式，左轮：" + str(LSpeed) + ",右轮：" + str(RSpeed)
                LSpeed, RSpeed = Fmain.Func_climb(handle_speed, Clock, IO.D1, IO.D2, IO.D3, IO.D4)
                continue
            # print("主函数")
        except KeyboardInterrupt:
            GPIO.cleanup()