from ACCEL import Accel_Calibration

if __name__ == "__main__":
    AC = Accel_Calibration('COM4',115200,100)
    AC.Calibration()