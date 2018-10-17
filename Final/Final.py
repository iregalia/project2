from picamera.array import PiRGBArray
from picamera import PiCamera
from gpiozero import Robot, DigitalInputDevice
import numpy as np
import imutils
import cv2
import time

# constants
width = 384
height = 288
mL = (23, 24)
mR = (5, 6)
satadj = 1.25
SLEEPTIME = 0.05
preturn = 2.5
turn = 0.5
base_spd = 0.1
turn_fact = 0.7
turn_spd = base_spd * turn_fact
adj_fact = 0.75
adj_spd = base_spd * adj_fact
turning = 0

# tuning camera params (to change)
size = 700
turn_size = 7000
gate_wid = 50
gate_dis = 60
gate_L = width/2 - gate_dis
gate_R = width/2 + gate_dis

# threshold variables #hsv 
greenLower = (29, 86, 40) 
greenUpper = (64, 255, 255)
white = (255, 255, 255)

# motor setup
r = Robot(mL, mR)

# m_speed = (mL_speed, mR_speed)
m_speed = (base_spd, base_spd)
r.value = m_speed

# initialize camera and grab reference
camera = PiCamera()
camera.resolution = (width, height)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(width, height))

# allow camera to warm up
time.sleep(0.1)

# grab an image
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
	
    # convert to hsv for colour thresh
    blur = cv2.GaussianBlur(image, (11, 11), 0)
    
    # saturation adjust
    hsv_im = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV).astype("float32")
    (h, s, v) = cv2.split(hsv_im)
    s = s*satadj
    s = np.clip(s, 0, 255)
    hsv_im = cv2.merge([h,s,v])
    
    mask = cv2.inRange(hsv_im, greenLower, greenUpper)
    
    # separating green
    imask = mask>0
    green_im = np.zeros_like(image, np.uint8)
    
    # thresholding
    green_im[imask] = white
    thresh = cv2.cvtColor(green_im, cv2.COLOR_BGR2GRAY)
    filt = cv2.medianBlur(thresh, 5)
#    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # contouring
    conts = cv2.findContours(filt.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    conts = conts[0] if imutils.is_cv2() else conts[1]
    # loop through all existing contours
    for c in conts:
	# compute the centre of the contour
        M = cv2.moments(c)
        print(M["m00"])
        
        if turning == 1:
            time.sleep(turn)
            if M["m00"] > size:
                m_speed = (base_spd, base_spd)
                r.value = m_speed
                turning = 0
                print("FOUND YA")
        
        elif M["m00"] > size:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            print ('cX = ', cX)
            if M["m00"] > turn_size:
                m_speed = (base_spd, base_spd)
                r.value = m_speed
                print("Start timer")
                time.sleep(preturn)
                #m_speed = (0, 0)
                m_speed = (turn_spd, base_spd)
                turning = 1
                print ('turning =', turning)
                print("Stop")
            elif M["m00"] > turn_size * 0.5:
                if cX > gate_L - 3 * gate_wid and cX < gate_L:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
                elif cX > gate_L:
                    m_speed = (base_spd, adj_spd)
                    print("Right")
                elif cX > 0 and cX < gate_L - 3 * gate_wid:
                    m_speed = (turn_spd, base_spd)
                    print("T Left")
                else:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
            elif M["m00"] > turn_size * 0.3:
                if cX > gate_L - 2 * gate_wid and cX < gate_L + 1 * gate_wid:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
                elif cX > gate_L + 1 * gate_wid:
                    m_speed = (base_spd, adj_spd)
                    print("Right")
                elif cX > 0 and cX < gate_L - 2 * gate_wid:
                    m_speed = (adj_spd, base_spd)
                    print("Left")
                else:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
            else:
                if cX > gate_L - gate_wid and cX < gate_L + 1.5 * gate_wid:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
                elif cX > gate_L + gate_wid:
                    m_speed = (base_spd, adj_spd)
                    print("Right")
                elif cX > 0 and cX < gate_L - gate_wid:
                    m_speed = (adj_spd, base_spd)
                    print("Left")
                else:
                    m_speed = (base_spd, base_spd)
                    print("Straight")
        else:
            cX, cY = 0, 0
				
    # update motor speed
    r.value = m_speed
    
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    time.sleep(SLEEPTIME)
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
