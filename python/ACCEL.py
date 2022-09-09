import serial
import numpy as np
import struct

MPU6050_ACCEL_SEN0 = 0.00059814453125
MPU6050_ACCEL_SEN1 = 0.0011962890625
MPU6050_ACCEL_SEN2 = 0.002392578125
MPU6050_ACCEL_SEN3 = 0.00478515625
G =9.8

class Accel_Calibration:
    def __init__(self,port,bsp,num):
        self.ser = serial.Serial(port,bsp,timeout=1)
        self.ar = np.array([],np.float32)
        self.flag = self.ser.is_open
        self.ser.setRTS(False)
        self.ser.setDTR(False)
        self.pointNum = num
        self.mode = 0
        self.count = 0

    def GetCommand(self):
        while 1:
            command = input("请输入命令：")
            if command == 'start' or command == 'next':
                self.mode = 1
                break
            elif command == 'end':
                self.mode = 0
                break
            else:
                self.mode = 0
                print("输入错误！！！")

    def Calibration(self):
        self.GetCommand()
        while self.mode:
            if self.flag:
                self.ser.flushInput()
                number = self.ser.inWaiting()
                while number < self.pointNum * 3 * 2:
                    number = self.ser.inWaiting()
                    print(number)
                list = [0,0,0]
                for i in range(0,self.pointNum):
                    for j in range(0,3):
                        accel = self.ser.read(2)
                        accel = accel[::-1]
                        short = struct.unpack('h',accel)
                        list[j] = short[0]*MPU6050_ACCEL_SEN1
                    self.ar = np.append(self.ar,list)
                self.count = self.count + 1
            else:
                print("串口初始初始化失败")
                break
            self.GetCommand()
        print(self.ar)
        self.Calc()
        self.ser.close()

    def Calc(self):
        self.ar = self.ar.reshape((self.count*self.pointNum,3))
        K = np.array([])
        Y = np.array([])
        list = [0,0,0,0,0,0]
        for i in range(self.count*self.pointNum):
            list[0] = self.ar[i][1] ** 2
            list[1] = self.ar[i][2] ** 2
            list[2] = self.ar[i][0]
            list[3] = self.ar[i][1]
            list[4] = self.ar[i][2]
            list[5] = 1
            K = np.append(K, list)
            Y = np.append(Y, -self.ar[i][0] ** 2)
        K = K.reshape((self.count*self.pointNum, 6))
        Y = Y.reshape((self.count*self.pointNum, 1))
        K = np.mat(K)
        Y = np.mat(Y)
        KT = K.T
        KKT = KT * K
        KTKI = KKT.I
        X = KTKI * KT * Y
        X = X.getA()
        A = X[0][0]
        B = X[1][0]
        C = X[2][0]
        D = X[3][0]
        E = X[4][0]
        F = X[5][0]
        OX = -C / 2
        OY = -D / 2 / A
        OZ = -E / 2 / B
        RX = (OX ** 2 + A * OY ** 2 + B * OZ ** 2 - F) ** 0.5
        RY = (RX ** 2 / A) ** 0.5
        RZ = (RX ** 2 / B) ** 0.5
        A1 = G / RX
        A2 = G / RY
        A3 = G / RZ
        B1 = -OX * A1
        B2 = -OY * A2
        B3 = -OZ * A3
        print(A1)
        print(A2)
        print(A3)
        print(B1)
        print(B2)
        print(B3)

if __name__ == "__main__":
    print("hello world")

