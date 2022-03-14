#-- coding:utf8 --
import dataControl
import time, datetime
import Gpio
import RPi.GPIO as GPIO

class cWheel:
    """
      #  A     B  #              逻辑
        #########           前进                                                 后退
        #   ↑   #     state -A---B-                                         state  -C---D-
        #  ↑↑↑  #       0    0   0   都碰到，若上一个状态也不为0，延时1s后无限制      0     0   0   都碰到，无限制
        # ↑ ↑ ↑ #       1    0   1   A碰，前进，左轮速度为0                       1     0   1    C碰，后退，左轮速度为0
        #   ↑   #       2    1   0   B碰，前进，右轮速度为0                       2     1   0    D碰，后退，右轮速度为0
        #   ↑   #       3    1   1   都没碰到， 无限制                           3     1   1   都碰到，(延时1s) 无限制
        #   ↑   #
        #########
       # C     D  #      """
    Wset0_start_tm = Wset0_end_tm = 1
    Wset0_delay = 1
    Wset0_setFlag = 1

    def __init__(self):
        pass

    # 爬坡模式 行程开关置0  该边速度为0
    def wheel_set0(self, clock, temp_speed, f_state, lchannel, rchannel):
        LSpeed, RSpeed = dataControl.climb_get_lorR_speed(clock, temp_speed)
        L = GPIO.input(lchannel)
        R = GPIO.input(rchannel)
        # print("有检测")
        state = int(str(L) + str(R), 2)
        if state == 0:        #都碰到
            if f_state is not 0:  # 第一次碰到  启动延时
                print("行程开关同时置0，开始延时")
                cWheel.Wset0_start_tm = datetime.datetime.now()
                LSpeed = RSpeed = 0  # 速度减为0
                cWheel.Wset0_setFlag = 0
                return state, LSpeed, RSpeed
            else:             # f_state = 0,  上一个状态也是0
                if cWheel.Wset0_setFlag is 0:
                    cWheel.Wset0_end_tm = datetime.datetime.now()
                    if int((cWheel.Wset0_end_tm - cWheel.Wset0_start_tm).seconds) >= cWheel.Wset0_delay:
                        print("延时结束，解除延时")
                        cWheel.Wset0_setFlag = 1
                        return state, LSpeed, RSpeed
                    else:
                        LSpeed = RSpeed = 0  # 速度保持为0
                        return state, LSpeed, RSpeed
                else:
                    return state, LSpeed, RSpeed
        else:
            if L ^ R:
                if L == 0:
                    LSpeed = 0
                if R == 0:
                    RSpeed = 0
                return state, LSpeed, RSpeed
            return state, LSpeed, RSpeed

    # 平路模式 行程开关置0  两侧都为0
    def wheel_stop(self, clock, temp_speed, f_state, lchannel, rchannel):
        LSpeed, RSpeed = dataControl.Road_get_lorR_speed(clock, temp_speed)
        L = GPIO.input(lchannel)
        R = GPIO.input(rchannel)
        state = int(str(L) + str(R), 2)
        # if state is 3:
        #     return state, LSpeed, RSpeed
        # else:
        #     LSpeed = RSpeed = 0  # 速度保持为0
        return state, LSpeed, RSpeed

    def check_LRbotton(self,Blift,Bright):
        L = GPIO.input(Blift)
        R = GPIO.input(Bright)
        state = str(L) + str(R)
        if state == "10":  # 右转
            return "10"
        elif state == "01":  # 左转
            return "01"
        else:
            return False

    # 旋转按钮测试
    def turn_L_R(self,Blift,Bright):
        L = GPIO.input(Blift)
        R = GPIO.input(Bright)
        state = str(L) + str(R)
        if state  == "10":  # 右转
            LSpeed = -100
            RSpeed = 100
        elif state == "01": # 左转
            LSpeed = 100
            RSpeed = -100
        else:
            LSpeed = 0
            RSpeed = 0
        return LSpeed, RSpeed


if __name__ == "__main__":
    test = cWheel()
    # 测试按钮：左转右转
    # GTC: 原地左转按钮 P25   B2:原地右转按钮 P22
    IO = Gpio.AGVGpio()
    IO.Gpio_Init()
    lspeed = rspeed = 0
    try:
        while True:
            if test.check_LRbotton(IO.GTC,IO.B2) is not False:
                lspeed, rspeed = test.turn_L_R(IO.GTC, IO.B2)
                print("lspeed:", lspeed, "   rspeed:", rspeed)
                continue
            else:
                lspeed = rspeed = 0
                # print("lspeed:", lspeed, "   rspeed:", rspeed)
            print("main")
    except KeyboardInterrupt:
        GPIO.cleanup()