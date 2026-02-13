📘 README – RAG Defense PFE
1️⃣ Présentation du projet

Ce projet implémente un système RAG (Retrieval-Augmented Generation) local destiné à l’automatisation de la recherche d’information en contexte simulé.

Caractéristiques principales :

Exécution 100 % locale

Compatible Windows

Fonctionne hors ligne

Base de données : SQLite

Architecture : Frontend + API REST locale

Rôles : ADMIN / USER

Recherche : Sémantique (Top-K = 5)

2️⃣ Prérequis

Avant de commencer, assurez-vous d’avoir :

✅ Windows 10 ou supérieur

✅ Python 3.10 ou supérieur

✅ pip installé

Vérification :

python --version
pip --version

3️⃣ Installation du projet
3.1 Cloner ou télécharger le projet

Placez-vous dans le dossier souhaité, puis :

cd rag-defense-pfe

3.2 Créer un environnement virtuel (recommandé)
python -m venv venv


Activer l’environnement :

venv\Scripts\activate


Vous devez voir (venv) apparaître dans votre terminal.

3.3 Installer les dépendances
cd backend
pip install -r requirements.txt
cd ..

4️⃣ Initialisation de la base de données
4.1 Lancer le script d'initialisation

Depuis la racine du projet :

python backend\db\init_db.py


Résultat attendu :

Création du fichier :

data/db/rag.db


Les tables suivantes doivent exister :

users

documents

chunks

query_logs

5️⃣ Lancer le serveur backend

Depuis la racine :

cd backend
python -m app.main


Le serveur démarre sur :

http://localhost:8000


Test rapide :

Ouvrir dans navigateur :

http://localhost:8000/health


Réponse attendue :

{ "status": "ok" }

6️⃣ Lancer le frontend

Deux possibilités :

Option simple (recommandée pour début)

Ouvrir directement :

frontend/login.html


dans votre navigateur.

Option propre (plus avancée)

Servir le frontend via le backend (configuration ultérieure).

7️⃣ Structure du projet
rag-defense-pfe/
  frontend/
  backend/
  data/

Backend

app/ → logique principale

db/ → connexion + script SQL

services/ → logique métier

utils/ → fonctions utilitaires

Data

db/ → base SQLite

docs/demo/ → documents de test

index/vector_store/ → index sémantique

logs/ → journaux applicatifs

8️⃣ Mode hors ligne

Le système est conçu pour fonctionner sans connexion Internet :

Pas d’appel API externe obligatoire

Base locale

Index local

Documents locaux

9️⃣ Problèmes fréquents
❌ Erreur : Python non reconnu

Ajouter Python au PATH Windows.

❌ Erreur : Module introuvable

Vérifier que l’environnement virtuel est activé.

❌ Erreur SQLite

Supprimer le fichier :

data/db/rag.db


Puis relancer :

python backend\db\init_db.py

🔟 Objectif de la phase actuelle

À ce stade :

La base de données est initialisée

Le serveur démarre

Le frontend est accessible

L’architecture est prête pour le développement des fonctionnalités