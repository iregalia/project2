from gpiozero import Robot, DigitalInputDevice
from time import sleep

SAMPLETIME = 0.1

r = Robot((5,6), (23, 24))

m1_speed = 0.12
m2_speed = 0.12

while True:
    r.value = (m1_speed, m2_speed)
    sleep(SAMPLETIME)