# 🌿 Aman — Intelligent Hydroponics Monitoring System

**Aman** (signifiant « Eau » en Tamazight) est une solution complète de monitoring et d'optimisation pour l'agriculture hydroponique et l'aquaculture. Alliant **IoT**, **Visualisation de données** et **Intelligence Artificielle**, Aman permet de surveillez en temps réel la santé de vos cultures tout en optimisant les ressources naturelles.

![Aman Dashboard Preview](/static/aman.jpeg)

## ✨ Fonctionnalités Clés

- **📊 Dashboard Temps Réel** : Visualisation dynamique (via Chart.js) du pH, de la température, de l'EC (conductivité) et de l'énergie solaire produite.
- **🤖 AmanBot (IA Expert)** : Un assistant intelligent intégré (propulsé par Groq & Llama 3.3) capable d'analyser vos données de capteurs et de vous donner des conseils agricoles précis.
- **🚨 Système d'Alertes Intelligent** : Notification immédiate en cas d'anomalies (pH critique, turbidité élevée, batterie faible).
- **🔋 Suivi Énergétique** : Monitoring de la production solaire et du niveau de batterie du système IoT.
- **💧 Économie d'Eau** : Calculateur en temps réel des litres d'eau économisés grâce au système.
- **🌗 Mode Sombre / Clair** : Interface moderne et responsive avec mode glassmorphism pour PC et mobile.

## 🛠️ Stack Technique

- **Backend** : Python 3.x, Flask (Framework web)
- **Base de données** : SQLite (via SQLAlchemy)
- **IA** : Groq API (Llama 3.3 70B) pour l'analyse prédictive
- **Data** : Pandas pour le traitement des données CSV/IoT
- **Frontend** : HTML5, CSS3 (Vanilla), JavaScript (ES6+), Chart.js
- **Design** : Glassmorphism, Responsive Web Design

## 🚀 Installation

1. **Cloner le repository** :
   ```bash
   git clone https://github.com/votre-username/Aman-HydroSmart-AI.git
   cd Aman-HydroSmart-AI
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer l'API IA** :
   Obtenez une clé API sur [Groq Console](https://console.groq.com/) et remplacez-la dans `app.py`.

4. **Lancer l'application** :
   ```bash
   python app.py
   ```
   L'application sera disponible sur `http://127.0.0.1:5000`.

## 📁 Structure du Projet

- `app.py` : Logique serveur, API et intégration IA.
- `static/` : Images (dont `aman.jpeg`), CSS et assets.
- `templates/` : Pages HTML (Dashboard, Login, Register).
- `water.csv` : Données historiques des capteurs utilisées pour la simulation.

---
*Développé pour une agriculture plus durable et intelligente. 🍃*
