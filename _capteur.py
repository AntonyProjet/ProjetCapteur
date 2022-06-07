import RPi.GPIO as GPIO
import time
import MySQLdb
import netifaces
from datetime import datetime

GPIO.setmode(GPIO.BCM)

print("+-----------------------------------------------------------+")
print("|          Mesure de distance -- Capteur HC-SR04            |")
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

distance_lit = 0.0 # variable globale pour la distance de l'obstacle, recupere via le fichier data.txt
compteur = 0 # variable pour le compteur de detection avant declechement de l'alerte
nb_erreurs = 0 # variable globale pour le compteur d'erreur

try:
    conn = MySQLdb.connect(host="192.168.10.12",
                           user="Administrateur",
                           passwd="Chute83",
                           db="Ehpad_Alerte")
except MySQLdb.Error as e:
    print("Connexion impossible %.1d : %s"% (e.args[0], e.args[1]))

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

        if(compteur == 5):
            print("/!\ ALERTE LEVER /!\\")
            # --- event db --- 
            try:
                netifaces.ifaddresses('wlan0') # recup des infos sur le wlan0
                ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr'] # on prend seulement l'addresse

                print("\n+--------------------------------------------------------------------+")
                # --- recuperation des horraires ---
                time_now = time.strftime('%H:%M', time.localtime()) # recup de l'heure
                values_now = time_now.split(":")
                heure_now = (int(values_now[0]))*3600
                minute_now = (int(values_now[1]))*60
                total_now = minute_now + heure_now
                total_now = 22*3600

                cursor = conn.cursor() 

                # -- recuperer l'idBorne en fonction de notre adresse IP --
                cursor.execute(""" SELECT idBorne FROM Borne WHERE IP_Borne = '%s' """% (ip))

                raw_idBorne = cursor.fetchone()
                # print(raw_idBorne) # debug

                idBorne_str = ''.join(map(str, raw_idBorne)) # convertion tuple to str
                print("| Cette borne possède l'ID : %s"% (idBorne_str))

                # -- recuperer l'idChambre en fonction de notre idBorne / adresse IP --
                cursor.execute(""" SELECT idChambre FROM Borne WHERE idBorne = '%s' """% (raw_idBorne))

                raw_idChambre = cursor.fetchone()
                # print(raw_idChambre) # debug

                idChambre_str = ''.join(map(str, raw_idChambre)) # convertion tuple to str
                print("| Cette borne est liee a la chambre d'ID : %s"% (idChambre_str))


                # -- recup seuil couche --
                cursor.execute(""" SELECT Couche FROM Resident WHERE idChambre = '%s' """% (raw_idChambre))

                raw_couche = cursor.fetchone()
                # print(raw_couche) # debug
                # print(raw_couche[0].total_seconds()) # debug

                couche_str = ''.join(map(str, raw_couche)) # convertion tuple to str
                couche_str = couche_str.replace("(","").replace(")","").replace("'","").replace(",","") # on supprime les choses qu'on veut pas
                print("| L'heure du couche est : %s"% (couche_str))

                # -- recup seuil reveil --
                cursor.execute(""" SELECT Leve FROM Resident WHERE idChambre = '%s' """% (raw_idChambre))

                raw_leve = cursor.fetchone()
                # print(raw_leve) # debug
                # print(raw_leve[0].total_seconds()) # debug

                leve_str = ''.join(map(str, raw_leve)) # convertion tuple to str
                leve_str = leve_str.replace("(","").replace(")","").replace("'","").replace(",","") # on supprime les choses qu'on veut pas
                print("| L'heure du leve est : %s"% (leve_str))

                
                value_couche = couche_str.split(":") # on separe nos elements en une liste
                temps_couche = ((int(value_couche[0]))*3600) + ((int(value_couche[1]))*60) # on realise la conversion vers les secondes

                value_reveil = leve_str.split(":") # on separe nos elements en une liste
                temps_reveil = ((int(value_reveil[0]))*3600) + ((int(value_reveil[1]))*60) # on realise la conversion vers les secondes

                if((total_now > temps_reveil) and (total_now < temps_couche)): # on teste si on est dans la plage d'activation de la borne
                    print("| /!\ --> Impossible d'envoyer l'alerte, la borne n'est pas dans sa plage d'activation pre-configure\n")
                else:
                    if((temps_couche == 0) and (temps_reveil == 0)):
                        print("| /!\ ALERTE : La plage d'activation de la borne est configuree pour toute la journee.\n\t--> L'alerte va etre envoye sur la base de donnees ! ")
                    else:
                        print("| /!\ ALERTE : La plage d'activation de la borne est configuree de %s à %s.\n\t--> L'alerte va etre envoye sur la base de donnees ! "% (couche_str, leve_str))
                    
                        # -- recup si la borne est en alerte ou non --
                    cursor.execute(""" SELECT MAX(idAlerte) FROM Alerte WHERE idBorne = '%s' """% (raw_idBorne))

                    raw_idAlerte = cursor.fetchone()
                    
                    cursor.execute(""" SELECT Status FROM Alerte WHERE idAlerte = '%s' """% (raw_idAlerte))
                    
                    raw_statut = cursor.fetchone()
                    
                    print("| ----------")
                    print("| Dernier statut relevé : %s"% (raw_statut[0]))

                    date_now = datetime.date(datetime.now())
                    time_now = datetime.time(datetime.now())

                    # si 1 alors l'alerte n'a pas ete terminée donc on ne peut pas renvoyer

                    if(raw_statut[0] == 0): # si on recupere un status de 0 donc FALSE, la borne n'est pas en alerte donc on crée une alerte 
                        print("| Génération d'une nouvelle alerte...")
                        try:
                            cursor.execute(""" INSERT INTO Alerte (Date, Status, Compteur, DebutAlerte, FinAlerte, idBorne) 
                            VALUES ('%s', 1, 0, '%s', NULL, '%s') 
                            """% (date_now, time_now, idBorne_str))
                            print("| --> Mise a jour du status de la borne sur la base de donnee !")
                            GPIO.output(6, True)
                            lastId = cursor.lastrowid
                            cursor.execute(""" SELECT * FROM Alerte WHERE idAlerte = '%s' """% (lastId))

                            myresult = cursor.fetchall()

                            for x in myresult:
                                print(x)
                            
                            conn.commit()

                        except MySQLdb.Error as exe:
                            print("| /!\ --> Erreur insertion de l'update du Status %.1d : %s"% (exe.args[0], exe.args[1]))

                    else: # si TRUE, on passe car deja en alerte
                        print("\t--> Alerte deja en cours.. Temporisation..")
                        GPIO.output(6, True)
                        time.sleep(0.2)
                        GPIO.output(6, False)
                        time.sleep(0.2)
                        GPIO.output(6, True)
                        time.sleep(0.2)
                        GPIO.output(6, False)
                        time.sleep(0.2)
                        GPIO.output(6, True)

                    while True:
                        print("--> Attente de la désactivation.. Appuyer sur le bouton pour désactiver")

                        etat_btn = GPIO.input(button)

                        if (etat_btn == 0):
                            print("/!\ --> Alerte désactivée !")
                            GPIO.output(6, False)
                            # requete pour mettre à jour le statut de l'alerte
                            cursor.execute(""" SELECT MAX(idAlerte) FROM Alerte WHERE idBorne = '%s' """% (raw_idBorne))
                            raw_idAlerte = cursor.fetchone()
                            print(raw_idAlerte)

                            time_now = datetime.time(datetime.now())
                            cursor.execute(""" UPDATE Alerte SET Status = '0', FinAlerte = '%s' WHERE idAlerte = '%s' """% (time_now, raw_idAlerte[0]))
                            
                            conn.commit()
                            
                            cursor.execute(""" SELECT * FROM Alerte WHERE idAlerte = '%s' """% (raw_idAlerte))

                            myresult = cursor.fetchall()

                            for x in myresult:
                                print(x)
                                
                            break

                        time.sleep(2)
                        
            except MySQLdb.Error as e:
                print("Erreur %.1d : %s"% (e.args[0], e.args[1]))

            break # sortir du compteur d'alerte

    print("+---- FIN DU TEST : ----")
    print("| Nombre d'erreurs rencontrees : %.1i"% (nb_erreurs))

except IOError:
    print("/!\ --> Erreur, le fichier n'existe pas. Impossible d'etablir une distance avec l'obstacle")
except Exception as excep:
    print("--- ERREUR GLOBALE ---")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)

GPIO.cleanup()
conn.commit()
conn.close()