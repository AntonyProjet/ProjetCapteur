import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

print("+----------------------------------------------------------+")
print("|          Mesure des seuils -- Capteur HC-SR04            |")
print("+----------------------------------------------------------+")

Trig = 22   # input TRIG GPIO22
Echo = 23   # output ECHO GPIO23
Trig2 = 24  # input TRIG GPIO24
Echo2 = 25  # output ECHO GPIO25

GPIO.setup(Trig,GPIO.OUT)   # set pins input/output
GPIO.setup(Echo,GPIO.IN)
GPIO.setup(Trig2,GPIO.OUT)
GPIO.setup(Echo2,GPIO.IN)

GPIO.output(Trig, False)    # init les TRIG a l'etat bas
GPIO.output(Trig2, False)

nb_erreurs = 0
distance_retenue = 0.0
_distance_retenue = 0.0

# fonctions 
def addError():
    global nb_erreurs
    nb_erreurs = nb_erreurs + 1

def measure_capt(Trig, Echo):
    try:
        GPIO.output(Trig, True)
        time.sleep(0.00001)  # send 10us pulse to triggerGPIO.output(Trig, False)
        GPIO.output(Trig, False)

        try: # Erreur WHILE
            temp_freeze_counter = 0
            while GPIO.input(Echo)==0:
                try: # Erreur Start_Pulse  
                    start_pulse = time.time() # emission
                    temp_freeze_counter = temp_freeze_counter + 1
                    #print("| Start |") # debug
                    if (temp_freeze_counter > 1000):
                        print("FREEZEEEEEEEEEEEE")
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

        try: # Erreur WHILE
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

        distance = round((stop_pulse - start_pulse) * 340 * 100 / 2, 1) # calc distance , with 1 digit

        if (temp_freeze_counter > 1000):
            print("Correction du FREEZE")
            time.sleep(5)

        return distance
    
    except Exception as excep:
        print("-- Erreur DEF --")
        print("TYPE : ", excep.__class__)
        print("MESSAGE : ", excep)
        distance = 0
        print("Correction erreur --> 0")
        return distance

try:
    try:
        choix_mesure = int(input("Voulez-vous imposer la distance ? (Oui = 1 / Non = 0) : "))
        print("Choix mesure : %.1i"% (choix_mesure)) # debug
    except SyntaxError:
        choix_mesure = 0 # 0 = calcul de la mesure automatique
        print("/!\ --> Erreur de saisie, distance imposee : NON")

    if(choix_mesure == 1): # si on veut imposer la distance
        choix_ok = 0
        while(choix_ok != 1):
            try:
                real_dist = int(input("Entrer la valeur de la distance imposee (entre 2 et 500cm) : "))
                distance_retenue = real_dist
                _distance_retenue = real_dist
                choix_ok = 1
                
                if((real_dist > 500) or (real_dist < 5)):
                    print("/!\ --> Erreur de saisie, merci de reessayer en indiquant un nombre entre 2 et 500 !")
                    choix_ok = 0 
                    
            except SyntaxError:
                print("/!\ --> Erreur de saisie, merci de reessayer en indiquant un nombre !")
    
    else: # si on ne veut pas donc on calcule et teste
        res_moyenne = [] # liste pour recueillir les 10 valeurs de moyenne calculee
        _res_moyenne = []

        for i in range(3): # 10
            time.sleep(0.25) #0.25sec
            distance = [] # liste pour recueillir la moyenne des calculs de mesure
            _distance = []
            j = 0
            
            for j in range(10): # bouclage pour etablir une moyenne de mesure 
                time.sleep(0.05) # 50ms pour reduire le probleme hardware au maximum
                temp_dist = measure_capt(Trig, Echo)

                if(temp_dist>500.0): # mesure superieure a 500 (donc invalide)
                    temp_dist = measure_capt(Trig, Echo)
                elif(temp_dist<2.0): # mesure inferieure a 2 (donc invalide)
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

            if(len(distance)==0): # calcul d'une moyenne de mesure
                moy_distance = sum(distance)/1 # cas de division par 0
            else:
                moy_distance = sum(distance)/len(distance)

            if(len(_distance)==0):
                _moy_distance = sum(_distance)/1
            else:
                _moy_distance = sum(_distance)/len(_distance)
                    
            print("\n+----- Mesure %.1i Distance Capteur : -----+"% (i))
            print("| Capteur 1 - Mesure moyenne : %.1f cm  |"% (moy_distance))
            print("| Capteur 2 - Mesure moyenne : %.1f cm  |"% (_moy_distance))
            print("+---------------------------------------+")

            res_moyenne.append(moy_distance) # ajout des moyennes dans la liste des moyennes 
            _res_moyenne.append(_moy_distance)
        
        if(len(res_moyenne)==0): # calcul de la moyenne des mesures moyennes
            distance_retenue = sum(res_moyenne)/1 # cas de division par 0
        else:
            distance_retenue = sum(res_moyenne)/len(res_moyenne)
        
        if(len(_res_moyenne)==0):
            _distance_retenue = sum(_res_moyenne)/1
        else:
            _distance_retenue = sum(_res_moyenne)/len(_res_moyenne)


    print("\n+---- FIN DE LA MESURE DES SEUILS : ----+")
    print("| Nombre d'erreurs rencontrees : %.1i"% (nb_erreurs))
    print("| Distances retenues : %.1f cm | %.1f cm"% (distance_retenue, _distance_retenue))
    print("+----\n")
    
    print("Ecriture des donnees dans le fichier texte...")

    with open("data.txt", "w") as f1:
        f1.write(str("%.1f \n"% (distance_retenue)))
        f1.write(str("%.1f"% (_distance_retenue)))
        print("--> Ecriture : OK")
        
    print("Test de lecture...")
    
    with open("data.txt", "r") as f2:
        val_lecture = float(f2.readline())
        _val_lecture = float(f2.readline())

        print("| --> Capteur 1 : %.1f cm"% (val_lecture))
        print("| --> Capteur 2 : %.1f cm"% (_val_lecture))
        print("--> Lecture : OK")
        
except IOError:
    print("/!\ --> Erreur, le fichier n'existe pas")      
except Exception as excep:
    print("-- ERREUR GLOBALE --")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)

GPIO.cleanup()
