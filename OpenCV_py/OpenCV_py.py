from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import numpy as np
import cv2
import time
import serial

# params
size = 200
width = 384
height = 288
bound_wid = 25
left_bound = width/2 - bound_wid

# construct argument parse and prase arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True, help="path to the input image")
# args = vars(ap.parse_args())

# initialize uart
ser = serial.Serial("/dev/serial0", 9600)

# initialize camera and grab reference
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(width, height))

# allow camera to warm up
time.sleep(0.1)

# threshold variables
greenLower = (29, 86, 100)
greenUpper = (64, 255, 255)
white = (255, 255, 255)

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
	filt = cv2.medianBlur(thresh, 5)
#	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# contouring
	conts = cv2.findContours(filt.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	conts = conts[0] if imutils.is_cv2() else conts[1]

	# loop through all existing contours
	for c in conts:
		# compute the centre of the contour
		M = cv2.moments(c)
		print(M["m00"])
		if M["m00"] > size/2:
			cX = int(M["m10"] / M["m00"])
			cY = int(M["m01"] / M["m00"])
		else:
			cX, cY = 0, 0
		#draw contour and centre of shape on image
                if cX>0:
                    cv2.drawContours(filt,[c],-1,(0, 255, 0),2)
                    cv2.circle(image, (cX, cY), 7, (0, 0, 255), -1)
                if M["m00"] > size:
                    if cX>0 and cX<left_bound:
                        ser.write("L")
                        print("Left")
                    elif cX > (width - left_bound):
                        ser.write("R")
                        print("Right")
                    else:
                        ser.write("S")
                        print("Straight")

	# show the frame
	cv2.imshow("Frame", image)
#	cv2.imshow("Frame", gray)
	cv2.imshow("Thresh", filt)
	key = cv2.waitKey(1) & 0xFF

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
