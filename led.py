import RPi.GPIO as GPIO
import time
from datetime import datetime

GPIO.setmode(GPIO.BCM)

print("+-----------------------------------------------------------+")
print("|                             LED                           |")
print("+-----------------------------------------------------------+")

Trig = 22   # input TRIG GPIO22
Echo = 23   # output ECHO GPIO23
Trig2 = 24  # input TRIG GPIO24
Echo2 = 25  # output ECHO GPIO25

button = 2  # input BUTTON GPIO2
led = 6     # output LED GPIO6

GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(led,GPIO.OUT)
GPIO.output(6, False) # on init notre led en off car pas active

GPIO.setup(Trig,GPIO.OUT)   # definition des broches d'entree/sortie
GPIO.setup(Echo,GPIO.IN)
GPIO.setup(Trig2,GPIO.OUT)
GPIO.setup(Echo2,GPIO.IN)

GPIO.output(Trig, False)    # initialisation des sorties TRIG a l'etat bas
GPIO.output(Trig2, False)

# main
GPIO.output(6, True)
time.sleep(0.2)
GPIO.output(6, False)
time.sleep(0.2)
GPIO.output(6, True)
time.sleep(0.2)
GPIO.output(6, False)
time.sleep(0.2)
GPIO.output(6, True)
time.sleep(0.2)
GPIO.output(6, False)
time.sleep(0.2)
GPIO.output(6, True)
time.sleep(0.2)
GPIO.output(6, False)
time.sleep(0.2)

cout = 0

try:
    while True:
        etat_btn = GPIO.input(button)
        cout = cout + 1
        print(cout)
        time.sleep(0.2)

        if (etat_btn == 0):
            GPIO.output(6, False)
            time.sleep(0.3)
        GPIO.output(6, True)

        if (cout == 1000):
            GPIO.output(6, False)
            break

except Exception as excep:
    print("--- ERREUR GLOBALE ---")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)
except KeyboardInterrupt:
    print("+--- ARRET DU PROGRAMME ---")
    GPIO.cleanup()

