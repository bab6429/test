# Guide de Configuration Google Sheets

## Configuration de l'authentification Google Sheets

### Option 1 : Service Account (Recommandée pour usage local)

#### Étape 1 : Créer un projet Google Cloud
1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Cliquez sur "Sélectionner un projet" → "Nouveau projet"
3. Donnez un nom à votre projet (ex: "extracteur-amortissement")
4. Cliquez sur "Créer"

#### Étape 2 : Activer les APIs nécessaires
1. Dans le menu de gauche : "APIs et services" → "Bibliothèque"
2. Recherchez et activez :
   - **Google Sheets API**
   - **Google Drive API**

#### Étape 3 : Créer un compte de service
1. "APIs et services" → "Identifiants"
2. "Créer des identifiants" → "Compte de service"
3. Nom du compte : `extracteur-amortissement-sa`
4. Cliquez sur "Créer et continuer"
5. Rôle : "Éditeur" (ou "Propriétaire" si vous voulez tous les droits)
6. Cliquez sur "Continuer" puis "Terminé"

#### Étape 4 : Télécharger le fichier de clés
1. Cliquez sur le compte de service créé
2. Onglet "Clés" → "Ajouter une clé" → "Créer une clé"
3. Format : **JSON**
4. Le fichier se télécharge automatiquement
5. **Important** : Renommez le fichier en `google-credentials.json` et placez-le dans votre dossier de projet

#### Étape 5 : Configurer l'accès à vos Google Sheets
1. Ouvrez le fichier `google-credentials.json`
2. Copiez la valeur du champ `"client_email"`
3. Dans votre Google Sheets :
   - Cliquez sur "Partager"
   - Collez l'email du service account
   - Donnez les permissions "Éditeur"
   - Cliquez sur "Envoyer"

### Option 2 : Authentification par défaut

#### Pour Google Colab
- L'authentification fonctionne automatiquement
- Utilisez le code suivant dans Colab :
```python
from google.colab import auth
auth.authenticate_user()
```

#### Pour usage local avec gcloud
1. Installez Google Cloud SDK
2. Exécutez : `gcloud auth application-default login`
3. Suivez les instructions pour vous connecter

## Utilisation dans le code

### Avec fichier de service account
```python
from assurance import GoogleSheetsUploader

# Spécifiez le chemin vers votre fichier de credentials
uploader = GoogleSheetsUploader(credentials_file="google-credentials.json")

# Vérifiez l'authentification
if uploader.is_authenticated():
    success = uploader.upload_to_sheets(df, "nom_de_votre_sheet")
```

### Avec authentification par défaut
```python
from assurance import GoogleSheetsUploader

# Utilise l'authentification par défaut
uploader = GoogleSheetsUploader()

if uploader.is_authenticated():
    success = uploader.upload_to_sheets(df, "nom_de_votre_sheet")
```

## Dépannage

### Erreur "SpreadsheetNotFound"
- Vérifiez que le nom du fichier Google Sheets est correct
- Assurez-vous d'avoir partagé le fichier avec le service account

### Erreur "Permission denied"
- Vérifiez que le service account a les permissions "Éditeur" sur le fichier
- Vérifiez que les APIs Google Sheets et Drive sont activées

### Erreur "Invalid credentials"
- Vérifiez le chemin vers le fichier `google-credentials.json`
- Assurez-vous que le fichier JSON n'est pas corrompu

## Sécurité

⚠️ **Important** :
- Ne jamais committer le fichier `google-credentials.json` dans git
- Ajoutez `google-credentials.json` à votre `.gitignore`
- Gardez ce fichier sécurisé car il donne accès à vos ressources Google Cloud

## Structure de fichiers recommandée

```
votre_projet/
├── .env                        # Clé API Gemini
├── .gitignore                 # Exclure les fichiers sensibles
├── google-credentials.json    # Credentials Google (ne pas commit)
├── assurance.py              # Module principal
├── streamlit_app.py          # Interface Streamlit
├── requirements.txt          # Dépendances
└── README.md                # Documentation
```

## Contenu du .gitignore

```
# Fichiers sensibles
.env
google-credentials.json
temp_*.json

# Cache Python
__pycache__/
*.pyc
```
