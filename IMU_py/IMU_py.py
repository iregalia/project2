import smbus
import time
import math

constpi = math.pi
conv = float(32768)
bus = smbus.SMBus(1)
#address_1 = 0x1e     # magnetometer
address = 0x6b        # gyro + accelero

print bus.read_byte_data(address, 0x0f)

#CTRL1_XL
bus.write_byte_data(address,0x10,0x58)

#CTRL2_G 
bus.write_byte_data(address,0x11,0x58)

#CTRL5_C 
#bus.write_byte_data(address,0x14,0b01100100)

#CTRL6_C 
#bus.write_byte_data(address,0x15,0b00100000)

#CTRL7_G 
#bus.write_byte_data(address,0x16,0x44)
mov_avg = [0, 0, 0, 0, 0]

def read_x():
        read = gyro_conv(bus.read_byte_data(address, 0x28),
                         bus.read_byte_data(address, 0x29))
        return read 

def read_y():
        read = gyro_conv(bus.read_byte_data(address, 0x2a),
                         bus.read_byte_data(address, 0x2b))
        return read 

def read_z():
        read = gyro_conv(bus.read_byte_data(address, 0x2c),
                         bus.read_byte_data(address, 0x2d))
        return read
    
def gyro_conv(lower, upper):
        num = 256 * upper + lower
        if num >= 32768:
            num = num - 65536
        return num

while True:
        x_gyro = float(read_x())      #this returns the value as a byte between 0 and 255. 
        y_gyro = float(read_y())
        z_gyro = float(read_z())
#        mov_avg[5] = mov_avg[4]
#        mov_avg[4] = mov_avg[3]
#        mov_avg[3] = mov_avg[2]
#        mov_avg[2] = mov_avg[1]
#        mov_avg[1] = 
            
        x_ang = math.asin(float(x_gyro/conv)) * 180/constpi
        y_ang = math.asin(float(y_gyro/conv)) * 180/constpi
        z_ang = math.asin(float(z_gyro/conv)) * 180/constpi
        print ("X =")
        print (x_ang)
        print (float(x_gyro))
        print ("Y =")
        print (y_ang)
        print (float(y_gyro))
        print ("Z =")
        print (z_ang)
        print (float(z_gyro))
        print (" ")
        time.sleep(0.5)