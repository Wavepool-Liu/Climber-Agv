import serial
import serial.tools.list_ports
import re
import time

class get_serial:
    @staticmethod
    def get_usb_port():  #获取串口
        port_list = list(serial.tools.list_ports.comports())
        if len(port_list) == 0:
            print('no port')
            return None
        else:
            for i in range(0, len(port_list)):
                # print("port",port_list[i])
                pattern = re.compile(r'\d+')        #正则表达式
                r = pattern.match(str(port_list[0]), 11, 13)
                usb = r.group(0)
                usb_port = '/dev/ttyUSB' + usb
                # print(usb_port)
                try:
                    # print(usb_port)
                    ser = serial.Serial(usb_port, 38400, timeout=0.5)
                    ser.close()
                    ser.open()
                    ser.flushInput()
                    # print("\r","Serial port connect successfully!", end = "")
                    return ser
                except:
                    # print("\r","Serial port connect error...", end = "")
                    return None

if __name__ == "__main__":
    ser = get_serial.get_usb_port()
    while True:
        send_data = bytes.fromhex("10 02 10 21")
        ser.write(send_data)
        time.sleep(1)