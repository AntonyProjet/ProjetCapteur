import MySQLdb
import time
import netifaces

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
        print(ip)

        print("\n+--------------------------------------------------------------------+")

        cursor = conn.cursor() 

        # -- send insert request --
        cursor.execute(""" INSERT INTO Borne (IP_Borne, idChambre) VALUES ('192.168.10.69', (SELECT idChambre FROM Chambre WHERE NumChambre = 101)) """)
        
        #INSERT INTO Borne (IP_Borne, idChambre) VALUES ((SELECT idChambre FROM Chambre WHERE NumChambre = '1'))
        
        #cursor.commit()

        print(cursor.rowcount, "was inserted")

    except MySQLdb.Error as e:
        print("Erreur %.1d : %s"% (e.args[0], e.args[1]))

except Exception as excep:
    print("+--- ERREUR GLOBALE ---")
    print("TYPE : ", excep.__class__)
    print("MESSAGE : ", excep)

conn.commit()
conn.close()
