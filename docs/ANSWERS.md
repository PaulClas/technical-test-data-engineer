# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

### Étape 1: Installation des dépendances

#### Windows

1. **Installer PostgreSQL via Chocolatey**:
   - Ouvrez PowerShell en tant qu'administrateur et exécutez:
     ```sh
     choco install postgresql
     ```

2. **Démarrer le service PostgreSQL**:
   - Ouvrez l'invite de commande en tant qu'administrateur et exécutez:
     ```sh
     net start postgresql-x64-13
     ```

#### macOS

1. **Installer PostgreSQL via Homebrew**:
   - Ouvrez le terminal et exécutez:
     ```sh
     brew install postgresql
     ```

2. **Démarrer le service PostgreSQL**:
   - Exécutez:
     ```sh
     brew services start postgresql
     ```

#### Linux

1. **Installer PostgreSQL**:
   - Sur Ubuntu/Debian:
     ```sh
     sudo apt update
     sudo apt install postgresql postgresql-contrib
     ```
   - Sur Fedora:
     ```sh
     sudo dnf install postgresql-server postgresql-contrib
     ```

2. **Démarrer le service PostgreSQL**:
   - Sur Ubuntu/Debian:
     ```sh
     sudo systemctl start postgresql
     sudo systemctl enable postgresql
     ```
   - Sur Fedora:
     ```sh
     sudo systemctl start postgresql
     sudo systemctl enable postgresql
     ```

### Étape 1.1: Créer la base de données PostgreSQL

#### Windows, macOS, et Linux

1. **Ouvrir le terminal ou l'invite de commande**:
   - Utilisez le terminal pour exécuter les commandes suivantes.

2. **Se connecter à PostgreSQL**:
   - Utilisez la commande suivante pour vous connecter à PostgreSQL en tant qu'utilisateur `username`:
     ```sh
     psql -U username
     ```

3. **Créer la base de données `recommendation_db`**:
   - Exécutez la commande suivante pour créer la base de données:
     ```sql
     CREATE DATABASE recommendation_db;
     ```
   - Quittez PostgreSQL:
     ```sql
     \q
     ```

### Étape 1.2: Configurer l'environnement Python

#### Windows, macOS, et Linux

1. **Créer un environnement virtuel**:
   - Naviguez vers le répertoire de votre projet et créez un environnement virtuel:
     ```sh
     python -m venv venv
     ```

2. **Activer l'environnement virtuel**:
   - Sur Windows:
     ```sh
     venv\Scripts\activate
     ```
   - Sur macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

3. **Installer les dépendances**:
   - Installez les bibliothèques nécessaires en utilisant `pip`:
     ```sh
     pip install -r requirements.txt
     ```

### Étape 2: Exécuter le data pipeline avec  `data_pipeline.py`

1. **Configurer la base de données et les tables**:
   Le script data_pipeline.py contient des fonctions pour créer la base de données et les tables si elles n'existent pas. Vous pouvez exécuter ce script de deux manières différentes : avec l'option --run-once ou en mode interactif.

    **Option 1: Exécuter le script avec --run-once**
    Lorsque vous exécutez le script avec l'option --run-once, le script va configurer la base de données et les tables, puis exécuter le pipeline de données une seule fois. Voici comment procéder :

    ```
    python data_pipeline.py --run-once
    ```
    ***Ce que fait cette commande :***
    - Vérifie si la base de données recommendation_db existe. Si elle n'existe pas, elle la crée.
    - Crée les tables nécessaires si elles n'existent pas.
    - Exécute le pipeline de données une seule fois pour récupérer et enregistrer les données.

    **Option 2: Exécuter le script en mode interactif**
    Lorsque vous exécutez le script sans l'option --run-once, le script démarre en mode interactif. Dans ce mode, le script attend des commandes de l'utilisateur pour exécuter le pipeline de données. Voici comment procéder :

    ```
    python data_pipeline.py
    ```

    ***Ce que fait cette commande :***
    - Vérifie si la base de données recommendation_db existe. Si elle n'existe pas, elle la crée.
    - Crée les tables nécessaires si elles n'existent pas.
    - Démarre un serveur de métriques Prometheus.
    - Attend des commandes de l'utilisateur pour exécuter le pipeline de données.

    ***Comment utiliser le mode interactif :***
    - Une fois le script démarré, vous pouvez entrer la commande run dans le terminal pour exécuter le pipeline de données manuellement :

    ```
    Entrez 'run' pour déclencher manuellement le pipeline de données : run
    ```

    **Vérifier les logs**:
   - Consultez les logs générés par le script `data_pipeline.py` pour vérifier que les données ont été récupérées et enregistrées correctement dans la base de données en allant consulté le serveur des logs Prometheus à l'adresse ```127.0.0.1:8080``` ou dans le fichier ```data_pipeline.log``` qui se trouve dans le dossier ```src/moovitamix_fastapi/```
   

### Étape 3: Exécuter les tests avec `pytest`

1. **Installer `pytest` et `pytest-dotenv`**:
   - Si ce n'est pas déjà fait avec l'installation du fichier `requirements.txt`, installez `pytest`:
    ```sh
    pip install pytest pytest-dotenv
    ```

2. **Configurer `pytest`**:
   - Créez un fichier file:///Users/paul.clas/GitHub/technical-test-data-engineer/pytest.ini dans le répertoire racine de votre projet avec le contenu suivant:
    ```
    [pytest]
    python_files = test/test_*.py
    ```

3. **Exécuter les tests**:
   - Utilisez la commande suivante pour exécuter les tests:
    ```
    pytest
    ```

4. **Vérifier les résultats des tests**:
   - Consultez les résultats des tests `pytest` pour vous assurer que tous les tests passent avec succès.

### Dépannage

1. **Problèmes de connexion à la base de données**:
   - Assurez-vous que PostgreSQL est en cours d'exécution et que les identifiants que vous utilisez sont bien `username` et `password`

2. **Problèmes de dépendances**:
   - Assurez-vous que toutes les dépendances sont installées correctement en utilisant `pip install -r requirements.txt`.

3. **Problèmes de configuration**:
   - Vérifiez `API_BASE_URL = "http://127.0.0.1:8000"` et `DATABASE_URL = "postgresql://username:password@localhost/recommendation_db?sslmode=disable"` soient les valeurs utilisés dans `data_pipeline.py`.

   - Vous pouvez spécifier votre `PYTHONPATH` pour etre en mesure de rouler les tests avec pytest en specifiant celui-ci dans votre console:

        ```export PYTHONPATH=$PYTHONPATH:~/technical-test-data-engineer/src``` 

        ou 

        ```export PYTHONPATH=$PYTHONPATH:VOTRE_CHEMIN_LOCAL_ICI/technical-test-data-engineer/src``` 

        en changeant ```VOTRE_CHEMIN_LOCAL_ICI``` avec votre chemin de fichier local. Voici en exemple le mien 

        ```export PYTHONPATH=$PYTHONPATH:/Users/paul.clas/GitHub/technical-test-data-engineer/src```


En suivant ces étapes, vous devriez être en mesure de créer la base de données PostgreSQL, exécuter le script `data_pipeline.py` et exécuter les tests avec `pytest`.


## Questions (étapes 4 à 7)

### Étape 4

### Schéma de la base de données

**RÉPONSE COURTE**: Pas besoin de se compliquer la vie avec un data lake ou d'autres solutions super fancy, PostgreSQL est notre meilleur ami dans le cas de ce projet vue les données que nous traitons.

Pour stocker les informations récupérées des trois sources de données mentionnées (utilisateurs, pistes, historique d'écoute), voici un schéma de base de données relationnelle que nous pourrions utiliser :

#### Table [`users`]
Cette table stocke les informations sur les utilisateurs.

| Colonne          | Type       | Contraintes                |
|------------------|------------|----------------------------|
| id               | Integer    | PRIMARY KEY                |
| first_name       | String(255)| NOT NULL                   |
| last_name        | String(255)| NOT NULL                   |
| email            | String(255)| UNIQUE, NOT NULL           |
| gender           | String(50) |                            |
| favorite_genres  | String(255)|                            |
| created_at       | TIMESTAMP  | NOT NULL                   |
| updated_at       | TIMESTAMP  | NOT NULL                   |

#### Table [`tracks`]
Cette table stocke les informations sur les pistes musicales.

| Colonne          | Type       | Contraintes                |
|------------------|------------|----------------------------|
| id               | Integer    | PRIMARY KEY                |
| name             | String(255)| NOT NULL                   |
| artist           | String(255)| NOT NULL                   |
| songwriters      | String(255)|                            |
| duration         | String(50) |                            |
| genres           | String(255)|                            |
| album            | String(255)|                            |
| created_at       | TIMESTAMP  | NOT NULL                   |
| updated_at       | TIMESTAMP  | NOT NULL                   |

#### Table [`listen_history`]
Cette table stocke l'historique d'écoute des utilisateurs.

| Colonne          | Type       | Contraintes                |
|------------------|------------|----------------------------|
| id               | Integer    | PRIMARY KEY                |
| user_id          | Integer    | FOREIGN KEY (users.id)     |
| items            | JSON       |                            |
| created_at       | TIMESTAMP  | NOT NULL                   |
| updated_at       | TIMESTAMP  | NOT NULL                   |

### Recommandation du système de base de données

PostgreSQL est un bon choix pour un système de recommandation similaire à Spotify en raison de sa robustesse, de ses fonctionnalités avancées et de sa capacité à gérer des volumes de données importants tout en maintenant des performances élevées. Voici quelques raisons clés :

- **Support des types de données avancés** : PostgreSQL supporte nativement les types de données JSON, ce qui est utile pour stocker des structures de données complexes comme l'historique d'écoute.
- **Conformité ACID** : PostgreSQL garantit la fiabilité et la cohérence des transactions grâce à sa conformité aux propriétés ACID (Atomicité, Cohérence, Isolation, Durabilité).
- **Extensibilité** : PostgreSQL est hautement extensible avec des fonctionnalités telles que les extensions, les types de données définis par l'utilisateur, et les fonctions stockées.
- **Performance** : PostgreSQL offre de bonnes performances pour les opérations de lecture et d'écriture, et peut être optimisé pour des charges de travail spécifiques.
- **Communauté et support** : PostgreSQL a une grande communauté active et un support étendu, ce qui facilite la résolution des problèmes et l'accès aux ressources.


### Étape 5

### Méthode de Surveillance du Pipeline de Données

**RÉPONSE COURTE**: Il vaut mieux utiliser des outils comme Prometheus, Grafana ou Datadog à la place de ré-inventer la roue dans le cas de pipeline complexe en production. Dans notre cas, des métriques simples avec Prometheus et des logs vont faire l'affaire.

Pour suivre la santé du pipeline de données dans son exécution quotidienne, nous utilisons une combinaison de journaux (logs) et de métriques de surveillance. Voici comment nous avons procédés :

1. **Journaux (Logs)** :
   - **Configuration des logs** : Nous avons configuré le script data_pipeline.py pour enregistrer les logs à la fois dans un fichier (`data_pipeline.log`) et dans la console. Cela permet de suivre les événements importants et les erreurs en temps réel et de les consulter ultérieurement.
   - **Niveaux de logs** : Nous utilisons différents niveaux de logs (`INFO`, `ERROR`, etc.) pour catégoriser les messages et faciliter leur analyse.

2. **Métriques de Surveillance avec Prometheus** :
   - **Prometheus** : Nous utilisons Prometheus pour collecter et surveiller les métriques du pipeline de données. Prometheus est un système de surveillance et d'alerte open-source qui est bien adapté pour surveiller les applications et les infrastructures.
   - **Métriques Clés** : Nous avons défini plusieurs métriques clés pour surveiller la santé du pipeline de données :
     - **REQUEST_TIME** : Temps passé à traiter une requête. Cela nous permet de surveiller les performances du pipeline.
     - **ERROR_COUNT** : Nombre total d'erreurs dans le pipeline. Cela nous permet de détecter et de réagir rapidement aux problèmes.
     - **DATA_PROCESSED** : Quantité totale de données traitées. Cela nous permet de suivre le volume de données ingérées par le pipeline.
     - **CPU_USAGE** : Utilisation du CPU du pipeline. Cela nous permet de surveiller la charge du CPU et d'identifier les goulots d'étranglement.
     - **MEMORY_USAGE** : Utilisation de la mémoire du pipeline. Cela nous permet de surveiller la consommation de mémoire et d'optimiser les ressources.

D'autres métriques importantes seraient la latence des requêtes, le débit des données, taux de succès des opérations, longueur des files d'attentes(queue), les entrées-sorties (I/O) et le trafic sur le reseau.

La surveillance des pipelines de données est grandement facilitée par l'utilisation d'outils spécialisés comme Prometheus, Grafana ou Datadog.

### Étape 6

_votre réponse ici_

### Étape 7

_votre réponse ici_
