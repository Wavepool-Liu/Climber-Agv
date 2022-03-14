import numpy as np
import math
import self_Serial
from binascii import *
import crcmod


# 配套函数：输入正负十进制，转4位16进制
def int_transform_4hex(intNums):
    # print("int_transform_4hex")
    if intNums < 0:  #如果是负数
        str_list_16nums = list(hex(intNums%65536))
        insert_num = 'f'
    else:           #如果是正数
        str_list_16nums = list(hex(intNums))
        insert_num = '0'
    #补位数
    if len(str_list_16nums) == 5:
        str_list_16nums.insert(2, insert_num)
    elif len(str_list_16nums) == 4:
        str_list_16nums.insert(2, insert_num)
        str_list_16nums.insert(2, insert_num)
    elif len(str_list_16nums) == 3:
        str_list_16nums.insert(2, insert_num)
        str_list_16nums.insert(2, insert_num)
        str_list_16nums.insert(2, insert_num)
    else:
        pass
    crc_data = "".join(str_list_16nums)  # 用""把数组的每一位结合起来  组成新的字符串
    hexNums = crc_data[2:4] + ' ' + crc_data[4:]
    return hexNums


# 配套函数：生成CRC16-MODBUS校验码
def crc16Add(read):
    # print("crc16Add")
    crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
    data = read.replace(" ", "") #消除空格
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')  # 位数不足补0，因为一般最少是5个
    crc_data = "".join(str_list) #用""把数组的每一位结合起来  组成新的字符串
    read = read.strip() + ' ' + crc_data[4:] + ' ' + crc_data[2:4] #把源代码和crc校验码连接起来
    return read


# 1：根据采样值获取挡位，钟点
def get_gear_Clock(dataA_x, dataA_y, dataB_x, dataB_y,dataC_x, dataC_y):
    # print("get_gear_Clock")

    # 获取12点 中点 及手柄位置三点的角度
    A = (dataA_x,dataA_y)
    B = (dataB_x,dataB_y)
    C = (dataC_x, dataC_y)
    # Convert the points to numpy latitude/longitude radians space
    a = np.radians(np.array(A))
    b = np.radians(np.array(B))
    c = np.radians(np.array(C))
    # Vectors in latitude/longitude space
    avec = a - b
    cvec = c - b
    lat = b[0]
    avec[1] *= math.cos(lat)
    cvec[1] *= math.cos(lat)
    if abs(dataB_x-dataC_x)<0.2 and abs(dataB_y -dataC_y)<0.2:
        angle2deg = 0  # 如果手柄的位置在中点
    elif dataC_x >= dataB_x:  # 手柄方向在南半球
        # print("手柄方向在南半球")
        angle2deg = np.degrees(
            math.acos(np.dot(avec, cvec) / (np.linalg.norm(avec) * np.linalg.norm(cvec))))
    else:                    # 手柄方向在北半球
        # print("手柄方向在北半球")
        angle2deg = 360.0-np.degrees(
            math.acos(np.dot(avec, cvec) / (np.linalg.norm(avec) * np.linalg.norm(cvec))))
    # print(angle2deg)
    # 通过角度判断时钟点数
    if angle2deg == 0:  # 如果为角度为0
        clock= 0
    else:
        for i in range(1, 13):  # 判断角度所在时钟区域
            if angle2deg > (15.0 + (i - 1) * 30.0) and angle2deg <= (45.0 + (i - 1) * 30.0):
                clock = i
                break
            else:
                clock = 12

    # 获得手柄距离中点的距离
    distance = math.sqrt( math.pow(dataB_x - dataC_x, 2) + math.pow(dataB_y - dataC_y, 2))
    Maxdistance = math.sqrt( math.pow(dataB_x - dataA_x, 2) + math.pow(dataB_y - dataA_y, 2))
    # 根据Max距离和当前距离分3个挡位

    if 0 <= distance <= Maxdistance/11:
        gear = 1  # 一档慢速
    elif  Maxdistance/11 < distance <= 2*Maxdistance/11:
        gear = 2  # 二档中速
    elif  2*Maxdistance/11 < distance <= 3*Maxdistance/11:
        gear = 3  # 三档高速
    elif  3*Maxdistance/11 < distance <= 4*Maxdistance/11:
        gear = 4  # 四档高速
    elif  4*Maxdistance/11 < distance <= 5*Maxdistance/11:
        gear = 5  # 五档高速
    elif  5*Maxdistance/11 < distance <= 6*Maxdistance/11:
        gear = 6  # 六档高速
    elif  6*Maxdistance/11 < distance <= 7*Maxdistance/11:
        gear = 7  # 七档高速
    elif  7*Maxdistance/11 < distance <= 8*Maxdistance/11:
        gear = 8  # 八档高速
    elif  8*Maxdistance/11 < distance <= 9*Maxdistance/11:
        gear = 9  # 九档高速
    elif  9*Maxdistance/11 < distance <= 10*Maxdistance/11:
        gear = 10  # 十档高速
    elif  10*Maxdistance/11 < distance <= Maxdistance:
        gear = 11  # 十一档高速
    else:
        gear = 11  # 超十一档
    return gear,clock


# 2：手柄通过三个状态判断下一个状态的速度取值 return:speed
def speed_control(gear, grandClock, fatherClock, clock, speed):
    # print("speed_control")
    # print("888888888888888888888")
    # speed = speed/(4-gear)  # 通过三个挡位，改变基础速度
    if (clock >=9 or 0< clock <=3) and (not(4<= fatherClock <=8)):  #前进
        if grandClock == 0 and fatherClock == 0 and (clock >=9 or 0< clock <=3):
            speed = speed/3   #停停前
        elif grandClock == 0 and (fatherClock >=9 or 0< fatherClock <=3) and (clock >=9 or 0< clock <=3):
            speed = 2*speed/3 #停前前
        elif (grandClock >=9 or 0< grandClock <=3) and (fatherClock >=9 or 0< fatherClock <=3) and (clock >=9 or 0< clock <=3):
            speed = speed     #前前前
        elif 4<= grandClock <= 8 and (fatherClock >=9 or 0< fatherClock <=3) and (clock >=9 or 0< clock <=3):
            speed = speed     #后前前
        elif (grandClock >=9 or 0< grandClock <=3) and 4<= fatherClock <= 8 and (clock >=9 or 0< clock <=3):
            speed = speed     #前后前
        elif (grandClock >=9 or 0< grandClock <=3) and fatherClock == 0 and (clock >=9 or 0< clock <=3):
            speed = speed     #前停前
        elif 4<= grandClock <= 8 and fatherClock == 0 and (clock >=9 or 0< clock <=3):
            speed = speed     #后停前
        else:
            speed = 0
            pass
    elif clock == 0 :         #停止（X,X,停）
        speed = 0
    elif (grandClock == 0 or (grandClock >=9 or 0< grandClock <=3)) and (fatherClock >=9 or 0< fatherClock <=3) and 4<= clock <= 8:
        speed = 0             #停止（X,前,后）
    elif (grandClock == 0 or 4<= grandClock <=8) and 4<= fatherClock <=8 and (clock >=9 or 0< clock <=3):
        speed = 0             #停止（X,后,前）
    elif clock == 6:
        if grandClock == 0 and fatherClock == 0 and clock == 6:
            speed = speed   #停停后6
        elif grandClock == 0 and 4<= fatherClock <=8 and clock == 6:
            speed = speed   #停后后6
        elif 4<= grandClock <=8 and 4<= fatherClock <=8 and clock == 6:
            speed = speed   #后后后6
        elif 4<= grandClock <=8 and (fatherClock >=9 or 0< fatherClock <=3) and clock == 6:
            speed = speed   #后前后6
        elif (grandClock >=9 or 0< grandClock <=3) and 4<= fatherClock <=8 and clock == 6:
            speed = speed   #前后后6
        elif (grandClock >=9 or 0< grandClock <=3) and fatherClock == 0 and clock == 6:
            speed = speed   #前听后6
        elif 4<= grandClock <=8 and fatherClock == 0 and clock == 6:
            speed = speed   #后停后6
        else:
            speed = 0
            pass
    elif 4<= clock <= 8 and (not(clock==6)):  #后退
        if grandClock == 0 and fatherClock == 0 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed #停停后
        elif grandClock == 0 and 4<= fatherClock <=8 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #停后后
        elif 4<= grandClock <=8 and 4<= fatherClock <=8 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #后后后
        elif 4<= grandClock <=8 and (fatherClock >=9 or 0< fatherClock <=3) and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #后前后
        elif (grandClock >=9 or 0< grandClock <=3) and 4<= fatherClock <=8 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #前后后
        elif (grandClock >=9 or 0< grandClock <=3) and fatherClock == 0 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #前听后
        elif 4<= grandClock <=8 and fatherClock == 0 and (4<= clock <= 8 and (not(clock==6))):
            speed = speed   #后停后
        else:
            speed = 0
            pass
    return speed


# 3：根据钟点方向发送485协议数据
def clock_SendHex(ser,Clock,StrHead,Speed):#先测试前进12和后退6
    # print("clock_SendHex")
    # print("Speed: ",str(Speed))
    if Clock == 12:
        LSpeed = Speed
        RSpeed = -Speed
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    if Clock == 1:
        LSpeed = 3*Speed/4
        RSpeed = -2*Speed/4
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    if Clock == 2:
        LSpeed = Speed/2
        RSpeed = -Speed/4
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    if Clock == 3:
        LSpeed = Speed/4
        RSpeed = 0
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    if Clock == 4:
        LSpeed = 0
        RSpeed = -Speed/2
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    if Clock == 5:
        LSpeed = 3*Speed/4
        RSpeed = -Speed/2
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 6:
        LSpeed = -Speed
        RSpeed = Speed
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 7:
        LSpeed = -3*Speed/4
        RSpeed = Speed/2
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 8:
        LSpeed = -2*Speed/4
        RSpeed = 0
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 9:
        LSpeed = 0
        RSpeed = Speed/4
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 10:
        LSpeed = -Speed/4
        RSpeed = Speed/2
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    elif Clock == 11:
        LSpeed = -Speed/2
        RSpeed = 3*Speed/4
        send_data = bytes.fromhex(crc16Add(StrHead+int_transform_4hex(int(LSpeed))+int_transform_4hex(int(RSpeed))))
        ser.write(send_data)
        ser.flush()
        return send_data
    else:
        send_data = bytes.fromhex(crc16Add(StrHead + int_transform_4hex(0) + int_transform_4hex(0)))
        ser.write(send_data)
        ser.flush()
        return send_data


# 5：获取平路模式左轮右轮速度
def Road_get_lorR_speed(Clock,speed):
    # speed 最小值不能超过 400
    V_STOP = 0
    V_FULL = int(speed)
    V_HIG = int(3 * speed / 4)
    V_MID = int(2 * speed / 4)
    V_LOW = int(1 * speed / 4)
    # V_FULL = int(13 * speed / 10)
    # V_HIG = int(speed )
    # V_MID = int(speed )
    # V_LOW = int(speed )
    # V_HIG = int(12 * speed / 10)
    # V_MID = int(11 * speed / 10)
    # V_LOW = int(10 * speed / 10)
    if 0 < V_LOW < 99:
        V_LOW = 0
    ASPECT_VECTOP = [
        [V_STOP, V_STOP],  # 0
        [-V_MID, V_STOP],  # 1
        [-V_MID, V_STOP],  # 2
        [-V_MID, V_STOP],  # 3
        [V_STOP, V_MID],  # 4
        [V_STOP, V_MID],  # 5
        [V_FULL, V_FULL],  # 6
        [V_MID, V_STOP],  # 7
        [V_MID, V_STOP],  # 8
        [V_STOP, -V_MID],  # 9
        [V_STOP, -V_MID],  # 10
        [V_STOP, -V_MID],  # 11
        [-V_FULL, -V_FULL]  # 12
    ]
    LSpeed, RSpeed = ASPECT_VECTOP[Clock]
    return LSpeed, RSpeed


# 5：获取爬坡模式左轮右轮速度
def climb_get_lorR_speed(Clock,speed):
    # speed 最小值不能超过 400
    V_STOP = 0
    V_FULL = int(speed)
    V_HIG = int(3 * speed / 4)
    V_MID = int(2 * speed / 4)
    # V_LOW = int(1 * speed / 4)
    ASPECT_VECTOP = [
        [V_STOP, V_STOP],  # 0
        [-V_MID, V_STOP],  # 1
        [-V_MID, V_STOP],  # 2
        [-V_MID, V_STOP],  # 3
        [V_STOP, V_MID],   # 4
        [V_STOP, V_MID],   # 5
        [V_HIG, V_HIG],  # 6
        [V_MID, V_STOP],  # 7
        [V_MID, V_STOP],  # 8
        [V_STOP, -V_MID],  # 9
        [V_STOP, -V_MID],  # 10
        [V_STOP, -V_MID],  # 11
        [-V_MID, -V_MID]  # 12
    ]
    LSpeed, RSpeed = ASPECT_VECTOP[Clock]
    return LSpeed, RSpeed

# 5:发送485数据
def Send_485Hex(ser,StrHead,LSpeed,RSpeed):
    send_data = bytes.fromhex(
        crc16Add(StrHead + int_transform_4hex(int(LSpeed)) + int_transform_4hex(int(RSpeed))))
    ser.write(send_data)
    ser.flush()
    return send_data


if __name__ == "__main__":
    Tclock = 6
    LSpeed,RSpeed = Road_get_lorR_speed(Tclock,2000)
    print("LSpeed: ", LSpeed, "RSpeed: ", RSpeed)
    # gear = 1
    # grandClock = fatherClock = clock = 6
    # Max_speed = 2000
    # currentspeed = speed_control(gear, grandClock, fatherClock, clock, Max_speed)
    # print(currentspeed)
    # gear,clock = get_gear_Clock(2.442451549663329,3.74975443876836, 2.4310209966922973,2.3892434306037513,
    #                2.502759784789059, 3.2011835814933276)
    # print(clock)

    LSpeed, RSpeed = climb_get_lorR_speed(Tclock, 200)
    print("LSpeed: ", LSpeed, "RSpeed: ", RSpeed)
