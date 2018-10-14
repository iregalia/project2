from gpiozero import Robot, DigitalInputDevice
import time
import pigpio
import rotary_encoder

# constant define
SAMPLETIME = 10

# variable instantiate
pos = 0
r = Robot((5,6), (23, 24))

m1_speed = 0.4
m2_speed = 0.4

def callback(way):
    global pos
    pos += way
    print("pos={}".format(pos))

pi = pigpio.pi()

r.value = (m1_speed, m2_speed)

#while True:
decoder = rotary_encoder.decoder(pi, 27, 17, callback)
time.sleep(SAMPLETIME)
print(pos)