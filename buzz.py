import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)

print("+-----------------------------------------------------------+")
print("|                 BUZZER -- Capteur HC-SR04                 |")
print("+-----------------------------------------------------------+")

Trig = 22   # input TRIG GPIO22
Echo = 23   # output ECHO GPIO23
Trig2 = 24  # input TRIG GPIO24
Echo2 = 25  # output ECHO GPIO25

button = 2  # input BUTTON GPIO2
led = 6     # output LED GPIO6
buzz = 18

GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(buzz,GPIO.OUT)
GPIO.setup(led,GPIO.OUT)
GPIO.output(6, False) # on init notre led en off car pas active

pwm = GPIO.PWM(buzz, 50)
rapport = 5


GPIO.setup(Trig,GPIO.OUT)   # definition des broches d'entree/sortie
GPIO.setup(Echo,GPIO.IN)
GPIO.setup(Trig2,GPIO.OUT)
GPIO.setup(Echo2,GPIO.IN)

GPIO.output(Trig, False)    # initialisation des sorties TRIG a l'etat bas
GPIO.output(Trig2, False)


try:
    while True:
        etat_btn = GPIO.input(button)

        if (etat_btn == 0):
            pwm.start(rapport)
            for l in range(3):
                GPIO.output(6, True)
                time.sleep(0.1)
                GPIO.output(6, False)
                time.sleep(0.1)
        pwm.stop(rapport)

        
except KeyboardInterrupt:
    print("+--- ARRET DU PROGRAMME ---")
    GPIO.cleanup()
