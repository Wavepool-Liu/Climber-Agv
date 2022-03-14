# -*- coding: utf-8 -*-
import cWheel
import Func_Array
import Gpio
import time, datetime
import RPi.GPIO as GPIO
import dataControl


class MainFunc:
    # 当前模式记录变量
    Mod_road = 1   # 平路模式
    Mod_climb = 0  # 爬坡模式

    # 对象初始化
    road = cWheel.cWheel()      # 平路模式行程开关检测
    climb = cWheel.cWheel()     # 爬坡模式行程开关检测
    tArray = Func_Array.ControlArray()
    state = f_state = 1         # 爬坡/平路模式下状态记录变量初始化

    # U_break刹车函数
    B_delay = 2               # 刹车延时时长
    B_break = 0                  # 刹车状态变量
    B_normal = 1                 # 正常状态变量
    B_val = B_fval = 1           # 状态记录
    B_start_tm = B_end_tm = 0    # 延时时间记录变量
    bflag = 0

    # U_FSwichMod函数
    FM_delay = 2                  # 切换延时时长
    FM_val = FM_fval = 1          # 状态记录
    FM_start_tm = FM_end_tm = 0   # 延时时间记录记录
    cflag = rflag = 0             # 当前模式记录

    def __init__(self):
        pass

    # 平路运行 函数
    @staticmethod
    def Func_road(gear, handle_speed, clock, D1, D2, D3, D4):
        """输入：D1: 左前行程开关检测  P4；
                D2: 右前行程开关检测  P27
                D3: 左后行程开关检测  P28
                D4: 右后行程开关检测  P29     输出：LSpeed, RSpeed"""
        # 向前检测
        speed_list = [500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000]
        handle_speed = speed_list[gear - 1]
        if MainFunc.tArray.inArray(clock, [10, 11, 12, 1, 2]):
            LSpeed, RSpeed = dataControl.Road_get_lorR_speed(clock, handle_speed)
            # MainFunc.state, LSpeed, RSpeed = MainFunc.road.wheel_stop(clock, handle_speed, MainFunc.f_state, D1, D2)

        # 向后检测
        elif MainFunc.tArray.inArray(clock, [4, 5, 6, 7, 8]):
            LSpeed, RSpeed = dataControl.Road_get_lorR_speed(clock, handle_speed)
            # MainFunc.state, LSpeed, RSpeed = MainFunc.road.wheel_stop(clock, handle_speed, MainFunc.f_state, D3, D4)
        # 不受行程开关影响
        else:  # 9 3
            LSpeed, RSpeed = dataControl.Road_get_lorR_speed(clock, handle_speed)
        MainFunc.f_state = MainFunc.state
        return LSpeed, RSpeed

    # 爬坡运行 函数
    @staticmethod
    def Func_climb(handle_speed, clock, D1, D2, D3, D4):
        """输入：D1: 左前行程开关检测  P4；
                        D2: 右前行程开关检测  P27
                        D3: 左后行程开关检测  P28
                        D4: 右后行程开关检测  P29     输出：LSpeed, RSpeed"""
        if MainFunc.tArray.inArray(clock, [10, 11, 12, 1, 2]):
            LSpeed, RSpeed = dataControl.climb_get_lorR_speed(clock, handle_speed)
            # MainFunc.state, LSpeed, RSpeed = MainFunc.climb.wheel_set0(clock, handle_speed, MainFunc.f_state,
            #                                                     D1, D2)
            # 向前检测
        elif MainFunc.tArray.inArray(clock, [4, 5, 6, 7, 8]):
            LSpeed, RSpeed = dataControl.climb_get_lorR_speed(clock, handle_speed)
            # MainFunc.state, LSpeed, RSpeed = MainFunc.climb.wheel_set0(clock, handle_speed, MainFunc.f_state,
            #                                                     D3, D4)
            # 向后检测
        else:  # 9 3
            LSpeed, RSpeed = dataControl.climb_get_lorR_speed(clock, handle_speed)
            # 不受行程开关影响
        MainFunc.f_state = MainFunc.state
        return LSpeed, RSpeed

    # 2. 刹车检测
    @staticmethod
    def U_break(B3, BRK, ENA, B_val):
        """ 输入:"B3 刹车按钮输入通道,BRK 刹车输出通道  ENA 输出驱动盒供电"      输出：“True“：开始刹车 ；”False“: 恢复正常”"""
        """ 备注：记得在检测到"刹车False"时，将全局变量 LSpeed = RSpeed = 0"""
        MainFunc.B_val = GPIO.input(B3)  # 检测电机刹车按钮

        if MainFunc.B_val == MainFunc.B_break:  # 检测到刹车
            if MainFunc.B_fval == MainFunc.B_normal:  # 第一次按下
                MainFunc.B_start_tm = datetime.datetime.now()
                GPIO.output(ENA, GPIO.HIGH)   # 驱动盒关闭
                MainFunc.bflag = 1
                print("刹车开始")
            else:
                if MainFunc.bflag == 1:  # 刹车延时开始
                    MainFunc.B_end_tm = datetime.datetime.now()
                    if (MainFunc.B_end_tm - MainFunc.B_start_tm).seconds >= MainFunc.B_delay:
                        MainFunc.bflag = 0
                        print("刹车结束")
                        GPIO.output(BRK, GPIO.LOW)
                else:           # 刹车延时结束
                    MainFunc.bflag = 0
                    pass
            MainFunc.B_fval = MainFunc.B_val
            return False

        if MainFunc.B_val == MainFunc.B_normal:  # 恢复到正常状态
            if B_val is True:
                GPIO.output(ENA, GPIO.LOW)  # 驱动盒开启
                GPIO.output(BRK, GPIO.LOW)  # 结束手刹
            else:
                GPIO.output(ENA, GPIO.LOW)  # 驱动盒开启
                GPIO.output(BRK, GPIO.HIGH)  # 开始手刹
            MainFunc.B_fval = MainFunc.B_val
            return True

    # 切换按钮延时过渡
    @staticmethod
    def U_FSwichMod(B1,M1,M2):
        """ 输入:"B1: 检测模式切换按钮"      输出：“False“：无检测到变化 ；”True“: 检测到电平变化”"""
        """ 备注：记得在检测"电平变化False"时，将全局变量 LSpeed = RSpeed = 0"""
        MainFunc.FM_val = GPIO.input(B1)  # 检测模式切换按钮(In)
        chan_list = [M1, M2]
        # print("进入")
        # GPIO.output(chan_list, (GPIO.LOW, GPIO.LOW))
        "重力调整系统供电"
        if MainFunc.FM_val == MainFunc.Mod_climb:  # 从平路切换到爬坡
            if MainFunc.FM_fval == MainFunc.Mod_road:  # 第一次切换
                print("开始切换")
                GPIO.output(chan_list, (GPIO.LOW, GPIO.HIGH))  # 分别输出不同电平
                "放下万向轮操作"
                MainFunc.FM_start_tm = datetime.datetime.now()
                MainFunc.cflag = 1
                MainFunc.FM_fval = MainFunc.FM_val
                return True
            else:
                if MainFunc.cflag == 1:
                    MainFunc.FM_end_tm = datetime.datetime.now()
                    if (MainFunc.FM_end_tm - MainFunc.FM_start_tm).seconds >= MainFunc.FM_delay:
                        print("从平路切换到爬坡完成")
                        GPIO.output(chan_list, (GPIO.LOW, GPIO.LOW))
                        "1.暂停万向轮操作   2.重力调整系统供电"
                        MainFunc.cflag = 0
                        MainFunc.FM_fval = MainFunc.FM_val
                        return False
                    return True
                else:
                    # print("-------爬坡模式--------")
                    MainFunc.cflag = 0
                    MainFunc.FM_fval = MainFunc.FM_val
                    return False

        if MainFunc.FM_val == MainFunc.Mod_road:  # 从爬坡切换到平路
            if MainFunc.FM_fval == MainFunc.Mod_climb:  # 第一次切换
                print("开始切换")
                "收起万向轮操作"
                GPIO.output(chan_list, (GPIO.HIGH, GPIO.LOW))  # 分别输出不同电平
                MainFunc.FM_start_tm = datetime.datetime.now()
                MainFunc.rflag = 1
                MainFunc.FM_fval = MainFunc.FM_val
                return True
            else:
                if MainFunc.rflag == 1:
                    MainFunc.FM_end_tm = datetime.datetime.now()
                    if (MainFunc.FM_end_tm - MainFunc.FM_start_tm).seconds >= MainFunc.FM_delay:
                        print("从爬坡切换到平路完成")
                        GPIO.output(chan_list, (GPIO.LOW, GPIO.LOW))
                        "1.暂停万向轮操作   2.重力调整系统供电"
                        MainFunc.rflag = 0
                        MainFunc.FM_fval = MainFunc.FM_val
                        return False
                    return True
                else:
                    # print("-------平路模式--------")
                    MainFunc.rflag = 0
                    MainFunc.FM_fval = MainFunc.FM_val
                    return False


if __name__ == "__main__":  # 模块测试
    IO = Gpio.AGVGpio()
    IO.Gpio_Init()
    test = MainFunc()
    lspeed = rspeed = 0
    B_val = True
    # 刹车测试(成功）
    # B3 :P26   BRK:  P24    ENA:  P23
    try:
        while True:
            print("lspeed:", lspeed, "   rspeed:", rspeed)
            if test.U_break(IO.B3, IO.BRK, IO.ENA, B_val) is False:
                lspeed = rspeed = 0
                B_val = False
                continue
            else:
                lspeed = rspeed = 2000
                pass
    except KeyboardInterrupt:
        GPIO.cleanup()


    # # 模式切换测试（成功）
    # # B1:P21
    # try:
    #     while True:
    #         if test.U_FSwichMod(IO.B1, IO.M1, IO.M2) is True:
    #             lspeed = rspeed = 0
    #             continue
    #         else:
    #             lspeed = rspeed = 2000
    #             pass
    #         print("lspeed:", lspeed, "   rspeed:", rspeed)
    # except KeyboardInterrupt:
    #     GPIO.cleanup()

    # # 平路模式函数测试(成功）
    # # D1: 左前行程开关检测  P4；
    # # D2: 右前行程开关检测  P27
    # # D3: 左后行程开关检测  P28
    # # D4: 右后行程开关检测  P29
    # try:
    #     handle_speed = 2000
    #     clock = 6
    #     while True:
    #         lspeed ,rspeed = test.Func_road(handle_speed,clock,IO.D1,IO.D2,IO.D3,IO.D4)
    #         print("lspeed:", lspeed, "   rspeed:", rspeed)
    # except KeyboardInterrupt:
    #     GPIO.cleanup()

    # 爬坡模式函数测试(成功）
    # D1: 左前行程开关检测  P4；
    # D2: 右前行程开关检测  P27
    # D3: 左后行程开关检测  P28
    # D4: 右后行程开关检测  P29
    # try:
    #     handle_speed = 2000
    #     clock = 12
    #     while True:
    #         lspeed ,rspeed = test.Func_climb(handle_speed,clock,IO.D1,IO.D2,IO.D3,IO.D4)
    #         print("lspeed:", lspeed, "   rspeed:", rspeed)
    # except KeyboardInterrupt:
    #     GPIO.cleanup()
