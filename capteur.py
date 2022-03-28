import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

print("+-----------------------------------------------------------+")
print("|          Mesure de distance -- Capteur HC-SR04            |")
print("+-----------------------------------------------------------+")

Trig = 22   # input TRIG GPIO22
Echo = 23   # output ECHO GPIO23
Trig2 = 24  # input TRIG GPIO24
Echo2 = 25  # output ECHO GPIO25

GPIO.setup(Trig,GPIO.OUT)   # definition des broches d'entree/sortie
GPIO.setup(Echo,GPIO.IN)
GPIO.setup(Trig2,GPIO.OUT)
GPIO.setup(Echo2,GPIO.IN)

GPIO.output(Trig, False)    # initialisation des sorties TRIG a l'etat bas
GPIO.output(Trig2, False)

distance_lit = 0.0 # variable globale pour la distance de l'obstacle, recupere via le fichier data.txt
compteur = 0 # variable pour le compteur de detection avant declechement de l'alerte
nb_erreurs = 0 # variable globale pour le compteur d'erreur


# fonctions 
def getDatas(): # recuperation des donnees du fichier txt pour la distance du lit
    global distance_lit
    print("Recuperation des donnees...")
    time.sleep(1.5)

    try:
        with open("data.txt", "r") as f:
            val_lecture = float(f.readline())
            _val_lecture = float(f.readline())
            print("Lecture : OK")
    except IOError:
        print("/!\ --> Erreur, le fichier n'existe pas") 

    distance_lit = ((val_lecture + _val_lecture)/2)+0.5 # on ajoute 5cm de marge 

    print("Distance avec l'obstacle : %.1f"% (distance_lit))

def addError(): # compteur d'erreurs
    global nb_erreurs
    nb_erreurs = nb_erreurs + 1

def measure_capt(Trig, Echo): # mesure des capteurs
    try:
        GPIO.output(Trig, True)
        time.sleep(0.00001)  # envoie d'une impulsion de 10us pour declencher
        GPIO.output(Trig, False)

        try: # Erreur boucle WHILE
            temp_freeze_counter = 0
            while GPIO.input(Echo)==0:
                try: # Erreur Start_Pulse  
                    start_pulse = time.time() # emission
                    temp_freeze_counter = temp_freeze_counter + 1
                    #print("| Start |") # debug
                    if (temp_freeze_counter > 1000): # 1000 etant une unite arbitraire de temps pour l'execution du programme. En temps normal, l'emission est faite sous 300 unites
                        print("/!\ Perte de l'onde...")
                        time.sleep(3)
                        break

                except Exception as excep:
                    print("-- Erreur Start_Pulse --")
                    print("TYPE : ", excep.__class__)
                    print("MESSAGE : ", excep)

        except Exception as excep:
                print("-- Erreur WHILE --")
                print("TYPE : ", excep.__class__)
                print("MESSAGE : ", excep)

        try: # Erreur boucle WHILE
            while GPIO.input(Echo)==1:
                try: # Erreur Stop_Pulse
                    #print("| Stop  |") # debug
                    stop_pulse = time.time() # reception

                except Exception as excep:
                    print("-- Erreur Stop_Pulse --")
                    print("TYPE : ", excep.__class__)
                    print("MESSAGE : ", excep)

        except Exception as excep:
                print("-- Erreur WHILE --")
                print("TYPE : ", excep.__class__)
                print("MESSAGE : ", excep)

        distance = round((stop_pulse - start_pulse) * 340 * 100 / 2, 1) # calcule de la distance , avec 1 digit

        if (temp_freeze_counter > 1000):
            print("/!\ Correction de la perte de l'onde... \nTemporisation pour retablir et ignorer l'echec...")
            time.sleep(5)

        return distance
    
    except Exception as excep:
        print("-- Erreur DEF --")
        print("TYPE : ", excep.__class__)
        print("MESSAGE : ", excep)
        distance = 0
        print("Correction erreur --> 0")
        return distance

# main
try:
    getDatas() # recuperation des donnees

    try: # dans le cadre des tests, le programme n'est pas dans une boucle infinie
        repeat_times = int(input("Nombre de repetitions de la mesure de test : "))
    except (SyntaxError, ValueError):
        repeat_times = 10
        print("--> Erreur de saisie, valeur par defaut : 10")

    print("\n")

    for i in range(repeat_times):
        time.sleep(0.25) #0.25sec
        distance = [] # liste vide
        _distance = []
        j = 0
        
        for j in range(5): # bouclage pour etablir une moyenne de mesure 
            time.sleep(0.05) # pause de 50ms pour reduire le probleme hardware au maximum
            temp_dist = measure_capt(Trig, Echo)

            if(temp_dist>500.0): # si mesure superieure a 500 (donc invalide), on recommence
                temp_dist = measure_capt(Trig, Echo)
            elif(temp_dist<2.0): # si mesure inferieure a 2 (donc invalide), on recommence
                temp_dist = measure_capt(Trig, Echo)
            else: # mesure valide entre 2 et 500
                distance.append(temp_dist)
            
            time.sleep(0.05) # 50ms
            _temp_dist = measure_capt(Trig2, Echo2)

            if(_temp_dist>500.0):
                _temp_dist = measure_capt(Trig2, Echo2)
            elif(_temp_dist<2.0):
                _temp_dist = measure_capt(Trig2, Echo2)
            else:
                _distance.append(_temp_dist)

        if(len(distance)==0): # si division par 0
            moy_distance = sum(distance)/1
        else:
            moy_distance = sum(distance)/len(distance)

        if(len(_distance)==0):
            _moy_distance = sum(_distance)/1
        else:
            _moy_distance = sum(_distance)/len(_distance)
                
        print("+----- Distance Capteur : -----+")
        print("| Capteur 1 - Mesure : %.1f cm | Reelle : %.1f cm"% (moy_distance, distance_lit))
        print("| Capteur 2 - Mesure : %.1f cm | Reelle : %.1f cm"% (_moy_distance, distance_lit))
        print("| Nombre de mesure, i : %.1i"% (i))
        print("+------------------------------+")

        if(((moy_distance<distance_lit) and (moy_distance>(5))) and ((_moy_distance<distance_lit) and (_moy_distance>(5)))): 
            print("--> Statut : Detection\n")
            compteur = compteur + 1
        else:
            print("--> Statut : Pas de detection\n")
            compteur = 0

        if(compteur == 15):
            print("/!\ ALERTE LEVER /!\\")
            break

    print("+---- FIN DU TEST : ----")
    print("Nombre d'erreurs rencontrees : %.1i"% (nb_erreurs))

except IOError:
    print("/!\ --> Erreur, le fichier n'existe pas. Impossible d'etablir une distance avec l'obstacle")
except Exception as excep:
    print("--- ERREUR GLOBALE ---")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)

GPIO.cleanup()
