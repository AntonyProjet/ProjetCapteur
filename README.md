![badge](https://forthebadge.com/images/badges/made-with-python.svg)

# Bienvenue sur le projet de Prévention de Chute

Projet de borne de Prévention de Chute dans le cadre d'un projet de fin de 2ème année de BTS SNIR

---

## A propos...

Le projet a pour but de créer une borne de prévention de chute afin de prévenir d'une éventuelle chute.  
Cette borne est pilotée par un Raspberry Pi 3 relié à deux capteurs Ultrasons HC-SR04.

---

### Pré-requis

Il est nécessaire de posséder l'ensemble des programmes du dépôt ainsi que 2 capteurs HC-SR04 et également une Raspberry Pi 3

## Démarrage

* Lancer le programme seuils.py via la commande : 
```
sudo python3 seuils.py
```
Une fois le programme terminé, les seuils seront alors enregistrés sur le fichier texte "data.txt".  
* Vous pourrez alors lancer le programme principal :
```
sudo python3 capteur.py
```

## Langages utilisés
* Python - 3.7.3
* MySQL


### Auteurs
* Antony Decroix
* Jean-Matthias Leroy
* Baptiste Louvel

---
