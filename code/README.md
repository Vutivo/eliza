# CHAT TPG

L’objectif de ce README est de nous permettre d’expliquer davantage certains choix effectués dans le cadre du projet Eliza.

Ce document a pour but de justifier les choix techniques et fonctionnels afin de faciliter la compréhension du projet pour des personnes extérieures.

## Pourquoi Discord ?

Nous avons choisi Discord à la suite d’un bootstrap (exercices en lien avec le projet à réaliser), au cours duquel nous, les deux développeurs du projet, avons utilisé cette plateforme.

De plus, Discord est un outil que nous utilisons au quotidien, ce qui rend cette application plus intéressante qu’une autre dans le cadre de notre projet.

## Pourquoi ce modèle ?

Dans le cadre du projet, nous devions utiliser un modèle local et gratuit, sans limite de tokens. Le modèle que nous avons choisi correspond à ces critères.

De plus, il s’agit d’un modèle léger et pré-entraîné, capable de converser naturellement avec les utilisateurs.

Il peut également retourner des formats JSON, ce qui est particulièrement intéressant dans notre cas, car cela permet d’activer des fonctions de manière automatisée.

## Pourquoi ces langages de programation ?

Pour le projet en général, nous utilisons Docker. Cela permet de mettre en place rapidement l’environnement de développement et de gérer plus facilement les deux parties du projet dans des conteneurs distincts.

### bot discord

Pour le bot Discord, nous avons fait le choix d’utiliser Python. Il s’agit d’un langage de programmation que nous avons déjà eu l’occasion d’utiliser lors de projets précédents.

Il nous a également semblé le plus adapté comparé à JavaScript, notamment parce que le projet intègre de l’intelligence artificielle, et que Python est souvent plus performant et mieux adapté pour ce type d’usage.

### landing page

Pour la landing page, nous avons utilisé plusieurs technologies : Vite, qui nous a permis de démarrer plus rapidement le projet, React ainsi que TypeScript, qui nous ont permis de réaliser la landing page et de rendre le code plus robuste, avec plus de sécurité et moins de bugs qu’avec du HTML classique.

Pour le design, nous avons utilisé Tailwind CSS, qui rend la création de l’interface plus simple et plus rapide.

L’utilisation de ces technologies était voulue pour la landing page, étant donné que la priorité du projet restait le chatbot, d’où le fait qu’aucune nouvelle technologie n’a été ajoutée au projet.

## Pourquoi utilisé des APIs externes ?

Pour rendre notre projet plus complet, nous avons choisi d’utiliser des APIs de plusieurs sites pour pouvoir proposer plusieurs choix aux utilisateurs.

Les APIs concernées sont principalement celles des entreprises de transport (SNCF, aéroports) et de logement (Airbnb, Booking).

## Pourquoi un chatbot de voyage ?

Nous souhaitions innover sur ce projet, avec un chatbot sur le thème du voyage. Il existe plein de chatbots avec des thèmes plus ou moins différents. Le nôtre, quant à lui, est spécialisé uniquement dans les voyages.

Nous souhaitons que notre chatbot soit utilisable par tous (particuliers, entreprises, agences de voyage).