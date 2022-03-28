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
    netifaces.ifaddresses('wlan0') # recup des infos sur le wlan0
    ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr'] # on prend seulement l'addresse

    # test des horraires
    time_now = time.strftime('%H:%M', time.localtime()) # recup de l'heure
    values_now = time_now.split(":")
    heure_now = int(values_now[0])
    minute_now = int(values_now[1]) 

    cursor = conn.cursor() 

    # recup id borne
    cursor.execute(""" SELECT idBorne FROM Borne WHERE IP_Borne = '%s' """ % (ip))

    idBorne = cursor.fetchone()
    
    idBorne_str = ''.join(map(str, idBorne)) # convert tuple to str
    print(idBorne_str)

    # recup seuil couche
    cursor.execute(""" 
    SELECT DATE_FORMAT(Couche_Resident, "%H:%i:%s") FROM Resident WHERE idResident = '1'
    """)

    couche_heure = cursor.fetchall()

    couche_str = ''.join(map(str, couche_heure)) # convert tuple to str
    couche_str = couche_str.replace("(","").replace(")","").replace("'","").replace(",","") # on supprime les choses qu'on veut pas
    print(couche_str)

    # recup seuil reveil
    cursor.execute(""" 
    SELECT DATE_FORMAT(Leve_Resident, "%H:%i:%s") FROM Resident WHERE idResident = '1'
    """)

    reveil_heure = cursor.fetchall()

    reveil_str = ''.join(map(str, reveil_heure)) # convert tuple to str
    reveil_str = reveil_str.replace("(","").replace(")","").replace("'","").replace(",","") # on supprime les choses qu'on veut pas
    print(reveil_str)
    
    value_couche = couche_str.split(":") # get heure
    heure_couche = int(value_couche[0])

    value_reveil = reveil_str.split(":") # get heure
    heure_reveil = int(value_reveil[0])

    if((heure_now > heure_reveil) and (heure_now < heure_couche)):
        print("Pas activee")
    else:
        print("Activee")



except MySQLdb.Error as e:
    print("Erreur %.1d : %s"% (e.args[0], e.args[1]))

conn.commit()
conn.close()