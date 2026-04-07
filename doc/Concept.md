# Concept du chatbot

L'objectif de ce bot est de pouvoir répondre au question des utilisateur sur n'importe quel moment dans la journée dans le theme du voyage. Le chatbot va donc pouvoir intéragir avec ce dernier, lui faire des suggestions en fonction de ces réponses ainsi que lui poser des questions pour cibler plus précisement les besoins de son interlocuteur

## Fonctionnement
Pour ce qui est du fonctionnement, le bot fonctionnera différement en fonction des demandes de la personne. Il y a une fonction si :

- La personne à besoin de **renseignement**
- La personne veut effectuer un voyage **professionnel**
- La personne veut effectuer un voyage **personnel**

Le bot fonctionne sur l'application **Discord**, il a également une mémoire **locale** qui lui permettra, de garder en cache uniquement les informations données par la personne dans un chat.En cas de changement de chat, les données ne seront pas transférés sur le nouveau.

Lors de la connexion sur le serveur discord, l'utilisateur à la possibilité de se rendre dans une catégorie pour pouvoir créée un chat avec le bot et lui même pour rendre la conversation plus privée.

Une fois le chat créée, le bot va commencé par se présenter (son rôle, son objectif,...) puis va poser une seul question qui orientra la suite de la conversation.Après chaque message, le bot vous posera une question supplémentaire afin de l'aider dans la recherche d'idée en fonction de vos envies.

### renseignement :
Si l'objectif de la personne en face est uniquement d'avoir des renseignements pour par exemple uniquement des activités, sur le temps ou sur un logement, alors, une simple discussion aura lieu entre l'utilisateur et l'IA pour répondre simplement à la question de l'utilisateur.

### professionnel :
Si l'objectif de la personne en face est d'organiser un voyage professionnel, alors le bot va lui poser des questions en rapport à :

- La ville de départ
- La ville d'arrivée
- La date de départ
- La date de retour
- Moyen de transport pour arriver à destination
- Moyen de transport pour se déplacer durant le séjour
- Le logement
- Des activité, Si oui :
    - proposition d'activité (restaurant, musée, sport, ...)

### personnel :
Si l'objectif de la personne est de réaliser un voyage personnel, alors le bot va également lui poser des question en rapport à :

- La ville de départ
- La ville d'arrivée Si pas d'idée:
    - Choix de la destination (ville ou campagne)
    - Proposition d'idées de destination en fonction des choix, des envies de la personne

- La date de départ
- La date de retour
- Moyen de transport pour arriver à destination
- Moyen de transport pour se déplacer durant le séjour
- Le logement
- Proposition ou suggestion d'activité à faire durant le séjour

## Récapitulatif 
A la fin de la conversation avec vous et le bot ou lorsque vous souhaitez exécuté la commande  ```/recap```, vous avez la possibilité de voir un récapitulatif de votre conversation avec l'IA qui ressemble à ceci :


```- type de voyage 
- ville de départ
- ville d'arrivée
- date de départ
- date de retour
- transport pour y aller(voiture d'entreprise, perso, train... )
- logement
- transport pour se déplacer à l'endroit prévu
- activités si il y a
- Temps
- Temperature moyenne
```
    


