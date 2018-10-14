import serial
from time import sleep

ser = serial.Serial ("/dev/serial0", 9600)    #Open port with baud rate
while True:
	ser.write("L")
        print ("Left")
	sleep(10)
	ser.write("R")
        print ("Right")
	sleep(10)
#	ser.write(20)
#        received_data = ser.read()              #read serial port
#        sleep(0.03)
#        data_left = ser.inWaiting()             #check for remaining byte
#        received_data += ser.read(data_left)
#        print (received_data)                   #print received data
