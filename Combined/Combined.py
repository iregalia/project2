from picamera.array import PiRGBArray
from picamera import PiCamera
import plotly.plotly as py
from plotly.graph_objs import Scatter, Layout, Figure
import argparse
import imutils
import numpy as np
import cv2
import time
import serial
import smbus
import math

username = 'phildor'
api_key = '3fuNcfX6aauP7jJk2dSB'
stream_token = 'ggoc88jwo2'

# construct argument parse and prase arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="path to the input image")
# args = vars(ap.parse_args())

# variables for maths
constpi = math.pi
conv = float(32768)

# threshold variables RBG not RGB
greenLower = (29, 86, 86)
greenUpper = (64, 255, 255)
white = (255, 255, 255)

# open I2C bus
bus = smbus.SMBus(1)
#address_1 = 0x1e     # magnetometer
address = 0x6b        # gyro + accelero

# IMU LSM check should be 105 , 0x69
print (bus.read_byte_data(address, 0x0f))

#CTRL1_XL
bus.write_byte_data(address,0x10,0x58)

# initialize camera and grab reference
camera = PiCamera()
camera.resolution = (384, 288)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(384, 288))

# allow camera to warm up
time.sleep(0.1)

# accel read
def read_x():
        read = byte_conv(bus.read_byte_data(address, 0x28),
                         bus.read_byte_data(address, 0x29))
        return read 

def read_y():
        read = byte_conv(bus.read_byte_data(address, 0x2a),
                         bus.read_byte_data(address, 0x2b))
        return read 

def read_z():
        read = byte_conv(bus.read_byte_data(address, 0x2c),
                         bus.read_byte_data(address, 0x2d))
        return read

def byte_conv(lower, upper):
        num = 256 * upper + lower
        if num >= 32768:
            num = num - 65536
        return num

# open UART ports
ser = serial.Serial ("/dev/serial0", 9600)    #Open port with baud rate

py.sign_in(username, api_key)

trace1 = Scatter(
        x=[],
        y=[],
        stream=dict(
            token=stream_token,
            maxpoints=200
        )
)

layout = Layout(
        title='Raspberry Pi Streaming Sensor Data'
)

fig = Figure(data=[trace1], layout=layout)

print py.plot(fig, filename='Raspberry Pi Streaming Example Values')

i = 0
stream = py.Stream(stream_token)
stream.open()

# grab an image
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	# grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
        image = frame.array

	# convert to hsv for colour thresh
        blur = cv2.GaussianBlur(image, (11, 11), 0)
        hsv_im = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_im, greenLower, greenUpper)

        # separating green
        imask = mask>0
        green_im = np.zeros_like(image, np.uint8)

	# thresholding
        green_im[imask] = white
        thresh = cv2.cvtColor(green_im, cv2.COLOR_BGR2GRAY)
#	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# contouring
        conts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        conts = conts[0] if imutils.is_cv2() else conts[1]

	# loop through all existing contours
        for c in conts:
            # compute the centre of the contour
            M = cv2.moments(c)
            if M["m00"] > 150:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
	    #draw contour and centre of shape on image
            if cX>0:
                cv2.drawContours(thresh,[c],-1,(0, 255, 0),2)
                cv2.circle(image, (cX, cY), 7, (0, 0, 255), -1)
            if cX>0 and cX<180:
                ser.write("L")
                print("Left")
            elif cX > 204:
                ser.write("R")
                print("Right")
            else:
                ser.write("S")
                print("Straight")
	# show the frame
        cv2.imshow("Frame", image)
        #cv2.imshow("Frame", gray)
        cv2.imshow("Thresh", thresh)
        key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
        rawCapture.truncate(0)
	# accel read x,y,z
        x_acc = float(read_x())
        y_acc = float(read_y())
        z_acc = float(read_z())

        # converter
        x_ang = 5 * math.asin(float(x_acc/conv)) * 180/constpi
        y_ang = 5 * math.asin(float(y_acc/conv)) * 180/constpi
        z_ang = 5 * math.asin(float(z_acc/conv)) * 180/constpi
        print ("X =")
        print (x_ang)
        print (float(x_acc))
        print ("Y =")
        print (y_ang)
        print (float(y_acc))
        print ("Z =")
        print (z_ang)
        print (float(z_acc))
        print (" ")
        
        sens_data = x_ang
        
        stream.write({'x': i, 'y': sens_data})
        i += 1
        
        if x_ang > 1:
            ser.write("F")
            print("Forward")
        elif x_ang < -1:
            ser.write("B")
            print("Back")
            
	# if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break