import MySQLdb
import time
import netifaces
from datetime import datetime

try:
    conn = MySQLdb.connect(host="192.168.10.12",
                           user="Administrateur",
                           passwd="Chute83",
                           db="Ehpad_Alerte")
except MySQLdb.Error as e:
    print("Connexion impossible %.1d : %s"% (e.args[0], e.args[1]))

try:
    try:
        netifaces.ifaddresses('wlan0') # recup des infos sur le wlan0
        ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr'] # on prend seulement l'addresse

        heure_now = 15

        for i in range(25):
            print("\n+--------------------------------------------------------------------+")
            # --- recuperation des horraires ---
            heure_now = heure_now + 1
            print("| Heure en cours : %i"% (heure_now))

            total_now = int(heure_now*3600)

            no_stop_hours = 0

            cursor = conn.cursor() 

            # -- recuperer l'idChambre en fonction de notre idBorne / adresse IP --
            cursor.execute(""" SELECT idChambre FROM Borne WHERE idBorne = 1 """)

            raw_idChambre = cursor.fetchone()
            print(raw_idChambre)

            idChambre_str = ''.join(map(str, raw_idChambre)) # convertion tuple to str
            print("| Cette borne est liee a la chambre d'ID : %s"% (idChambre_str))


            # -- recup seuil couche --
            cursor.execute(""" SELECT Couche FROM Resident WHERE idResident = 1 """)

            raw_couche = cursor.fetchone()
            print(raw_couche)
            # print(raw_couche[0].total_seconds()) # debug

            couche_str = ''.join(map(str, raw_couche)) # convertion tuple to str
            couche_str = couche_str.replace("(","").replace(")","").replace("'","").replace(",","") # on supprime les choses qu'on veut pas
            print("| L'heure du couche est : %s"% (couche_str))

            # -- recup seuil reveil --
            cursor.execute(""" SELECT Leve FROM Resident WHERE idResident = '%s' """% (raw_idChambre))

            raw_leve = cursor.fetchone()
            print(raw_leve)
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
                    print("| /!\ ALERTE : La plage d'activation de la borne est configuree pour toute la journee.\n\t--> L'alerte va etre envoye sur la base de donnee ! ")
                else:
                    print("| /!\ ALERTE : La plage d'activation de la borne est configuree de %s à %s.\n\t--> L'alerte va etre envoye sur la base de donnee ! "% (couche_str, leve_str))
                
                 # -- recup si la borne est en alerte ou non --
                cursor.execute(""" SELECT Status, MAX(idAlerte) FROM Alerte WHERE idBorne = '%s' """% (raw_idBorne))

                raw_status_id = cursor.fetchone()
                status_int = raw_status_id[0]

                date_now = datetime.date(datetime.now())
                time_now = datetime.time(datetime.now())

                # si 0 alors l'alerte na pas ete terminée donc on ne peut pas renvoyer

                if(status_int == 1): # si on recupere un status de 1 donc FALSE, la borne n'est pas en alerte donc on crée une alerte 
                    try:
                        #cursor.execute(""" UPDATE Borne SET Status = '1' WHERE idBorne = '%s' """% (idBorne_str))
                        cursor.excute(""" INSERT INTO Alerte (Date, Status, Compteur, DebutAlerte, FinAlerte, idBorne) 
                        VALUES ('%s', 0, 0, '%s', NULL, '%s') 
                        """% (date_now, time_now, raw_idBorne))
                        print("| \t--> Mise a jour du status de la borne sur la base de donnee !")

                    except MySQLdb.Error as exe:
                        print("| /!\ --> Erreur insertion de l'update du Status %.1d : %s"% (e.args[0], e.args[1]))

                else: # si TRUE, on passe car deja en alerte
                    print("\t--> Alerte deja en cours.. Temporisation..")
                    time.sleep(10)


    except MySQLdb.Error as e:
        print("Erreur %.1d : %s"% (e.args[0], e.args[1]))

except Exception as excep:
    print("+--- ERREUR GLOBALE ---")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)

conn.commit()
conn.close()

