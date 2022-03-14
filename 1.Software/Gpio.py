#-- coding:utf8 --
import RPi.GPIO as GPIO
import time

class AGVGpio:
    # AGV1: B1
    # B1 = 5    # 检测模式切换按钮(In)      功能口：P21
    # B2 = 6    # 检测原地右转按钮（In)     功能口：P22
    # B3 = 12   # 检测紧急制动按钮（In)     功能口：P26
    # GTC = 26  # 检测原地左转按钮（In)     功能口：P25

    # D1 = 23  # 检测左前轮行程开关(In)     功能口： P4
    # D2 = 16  # 检测右前轮行程开关(In)     功能口： P27
    # D3 = 20  # 检测左后轮行程开关(In)     功能口： P28
    # D4 = 21  # 检测右后轮行程开关(In)     功能口： P29

    # M1 = 24   # 万向轮功能端复用      M1 M2: 01推出，02收缩，11启动重力推杆供电   00关闭重力推杆供电   功能口：P24
    # M2 = 25   # 功能口：P23

    # AGV2
    B1 = 26    # 检测模式切换按钮(In)      功能口：P25
    B2 = 12    # 检测原地右转按钮（In)     功能口：P26
    B3 = 5   # 检测紧急制动按钮（In)     功能口：P21
    GTC = 6  # 检测原地左转按钮（In)     功能口：P22

    M1 = 23  # 万向轮推杆控制1          功能口： P4
    M2 = 16  # 万向轮推杆控制2          功能口： P27
    GRAVETY = 24  # 重力传感器供电     功能口：P24

    D3 = 25  # 检测左后轮行程开关(In)     功能口： P23
    D4 = 20  # 检测右后轮行程开关(In)     功能口： P28
    D1 = 2  # 检测左前轮行程开关(In)     功能口： P
    D2 = 3  # 检测右前轮行程开关(In)     功能口： P
    ENA = 13  # 输出驱动盒供电(In)       功能口：P23
    BRK = 19  # 输出电机刹车按钮(In)     功能口： P24



    def __init__(self):
        pass

    # 1. Gpio 初始化
    def Gpio_Init(self):
        GPIO.setwarnings(False)       # 关闭警告
        GPIO.setmode(GPIO.BCM)        # 选择GPIO编码格式 BCM

        # 设置输入检测引脚  上拉
        In_GPIOS = (AGVGpio.B1, AGVGpio.B2, AGVGpio.B3, AGVGpio.GTC, AGVGpio.D1, AGVGpio.D2, AGVGpio.D3, AGVGpio.D4)
        # In_GPIOS = (AGVGpio.B1, AGVGpio.B2, AGVGpio.B3, AGVGpio.GTC)
        GPIO.setup(In_GPIOS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # 复用功能口默认关闭
        GPIO.setup(AGVGpio.M1, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(AGVGpio.M2, GPIO.OUT, initial=GPIO.HIGH)

        # # 驱动盒默认使能 1
        GPIO.setup(AGVGpio.ENA, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(AGVGpio.GRAVETY, GPIO.OUT, initial=GPIO.HIGH)
        #
        # # 刹车输出默认解除刹车 1
        GPIO.setup(AGVGpio.BRK, GPIO.OUT, initial=GPIO.LOW)


if __name__ == "__main__":
    # IO口测试
    IO = AGVGpio()
    IO.Gpio_Init()
    try:
        while True:
            GPIO.setup(AGVGpio.M1, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(AGVGpio.M2, GPIO.OUT, initial=GPIO.HIGH)
            time.sleep(5)
            GPIO.setup(AGVGpio.M1, GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(AGVGpio.M2, GPIO.OUT, initial=GPIO.LOW)
            time.sleep(5)
            # GPIO.output(IO.ENA, GPIO.LOW)
            # print("low")
            # time.sleep(5)
            # GPIO.output(IO.ENA, GPIO.HIGH)
            # print("HIGH")
            # time.sleep(5)
    except KeyboardInterrupt:
        GPIO.cleanup()