# CHAT TPG

Planifier un voyage ne devrait pas être compliqué. Chat TPG est ton compagnon intelligent pour organiser tes déplacements, découvrir des destinations et construire ton itinéraire idéal en quelques messages

## Fonctionnalités

- Trouver un moyen de locomotion pour ce rendre à votre destination
- Connaitre la météo de votre destination
- Trouver un logement en fonction de votre budget et de votre destination

Chat TPG est un chatbot conçu pour vous accompagner dans l’organisation de vos voyages.

Il agit comme un véritable conseiller de voyage. Il vous pose des questions lorsque des informations supplémentaires sont nécessaires et peut également vous proposer des suggestions personnalisées en fonction de votre demande.

## Stack technique

- **Python** : développement du chatbot Discord et gestion de la logique conversationnelle  
- **React / TypeScript** : création de la landing page et de l’interface utilisateur  
- **Tailwind CSS** : conception et mise en place du design de l’application  
- **Docker** : containerisation du projet pour faciliter le déploiement et l’exécution  


## Architecture du projet

Le projet est organisé en plusieurs parties distinctes afin de séparer clairement le chatbot, la landing page et la documentation.

code/
├── bot/                          
│   ├── .env                     
│   ├── dockerfile               
│   └── requirements.txt         
│
├── landing/                     
│   ├── .vite/                   
│   ├── node_modules/            
│   ├── public/                  
│   ├── src/                     
│   ├── .gitignore
│   ├── dockerfile                 
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── README.md
│   ├── tsconfig.app.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│
├── docker-compose.yml             
│
└── doc/                         
    ├── Business.md
    ├── Chaine_de_valeur.md
    ├── Cible.md
    ├── Concept.md
    ├── Ethique.md

## Installation
Pour l'instalation du projet il suffit simplement de suivre ces étapes :

Clone le répertoire sur github

```
git clone <repo-url>
cd <repo-name>
```
Création d'un fichier  `.env` dans le dossier `bot/`

```
DISCORD_TOKEN=
WEATHER_API_KEY=
DISCORD_CHANNEL=
HUGGING_FACE_TOKEN=
SerpAPI=
SNCF_API_KEY=
```
**Description des variables**

**DISCORD_TOKEN** : token du bot Discord

**WEATHER_API_KEY** : clé API pour la météo

**DISCORD_CHANNEL** : ID du salon Discord utilisé pour les interactions

**HUGGING_FACE_TOKEN** : token pour télécharger ou utiliser des modèles Hugging Face

**SerpAPI** : clé API pour les recherches web

**SNCF_API_KEY** : clé api pour des recherches sur un trajet en train

## Crédits
This project was made by [ssamepi](https://github.com/ssamepi), and [Kenan-LCF](https://github.com/Kenan-LCF).