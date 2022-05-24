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
    
netifaces.ifaddresses('wlan0') # recup des infos sur le wlan0
ip = netifaces.ifaddresses('wlan0')[netifaces.AF_INET][0]['addr'] # on prend seulement l'addresse

cursor = conn.cursor() 

# -- recuperer l'idBorne en fonction de notre adresse IP --
cursor.execute(""" SELECT idBorne FROM Borne WHERE IP_Borne = '%s' """% (ip))

raw_idBorne = cursor.fetchone()
print(raw_idBorne)

idBorne_str = ''.join(map(str, raw_idBorne)) # convertion tuple to str
print("| Cette borne possède l'ID : %s"% (idBorne_str))

# -- recup si la borne est en alerte ou non --
#cursor.execute(""" SELECT Date FROM Alerte WHERE idBorne = '%s' """% (raw_idBorne))
cursor.execute(""" SELECT Status, MAX(idAlerte) FROM Alerte WHERE idBorne = '%s' """% (raw_idBorne))
raw_date = cursor.fetchone()

print(raw_date)
print(raw_date[0])
print(type(raw_date))