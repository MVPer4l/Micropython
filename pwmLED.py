from machine import Pin, PWM
from time import sleep

frequency = 250000
led = PWM(Pin(14), frequency)
MAXDUTY = 1023
PORCENT = 100
NEWDUTY = int(PORCENT*1023/100)  #regla de 3

while True:
  #for duty_cycle in range(0, 1024):
  led.duty(NEWDUTY)
  sleep(0.005)