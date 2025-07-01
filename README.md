# Extracteur de Tableau d'Amortissement avec Langfuse

Cette application permet d'extraire automatiquement les tableaux d'amortissement depuis des fichiers PDF en utilisant Langfuse et de les convertir en format structuré (DataFrame/CSV).

## 🔧 Configuration

### Configuration Langfuse

L'application utilise maintenant Langfuse au lieu de Google Gemini. Vous devez configurer les paramètres suivants :

#### Option 1 - Fichier .env (Développement local)

Créez un fichier `.env` à la racine du projet avec :

```env
# Configuration pour Langfuse
AUTH_TOKEN=votre_auth_token_ici
LANGFUSE_PUBLIC_KEY=votre_langfuse_public_key_ici
API_URL=https://votre-api-url-langfuse.com/api/endpoint

# Variables pour Langfuse
PROMPT_NAME=tableau_amortissement_extraction
PROMPT_VERSION=1
```

#### Option 2 - Secrets Streamlit Cloud

Si vous déployez sur Streamlit Cloud, configurez les secrets dans l'interface :

```toml
AUTH_TOKEN = "votre_auth_token_ici"
LANGFUSE_PUBLIC_KEY = "votre_langfuse_public_key_ici"
API_URL = "https://votre-api-url-langfuse.com/api/endpoint"
PROMPT_NAME = "tableau_amortissement_extraction"
PROMPT_VERSION = 1
```

## 📦 Installation

1. Clonez le repository
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Configurez vos paramètres Langfuse (voir section Configuration)

## 🚀 Utilisation

### Interface Streamlit
```bash
streamlit run streamlit_app.py
```

### Utilisation directe
```python
from assurance import AmortizationExtractor

extractor = AmortizationExtractor()
df = extractor.process_pdf_to_dataframe("chemin/vers/votre/fichier.pdf")
```

## ⚠️ Points d'attention

### **Traitement en mémoire (RAM uniquement)**

✅ **Nouveau : Plus besoin de fichier temporaire !**

L'application traite maintenant les fichiers directement en mémoire :

```python
# Ancien code (avec fichier temporaire)
with tempfile.NamedTemporaryFile() as temp_file:
    temp_file.write(uploaded_file.getbuffer())  # ❌ Écriture sur disque
    result = extractor.extract_from_pdf(temp_file.name)

# Nouveau code (traitement en mémoire)
pdf_bytes = uploaded_file.getbuffer().tobytes()  # ✅ RAM uniquement
result = extractor.extract_from_bytes(pdf_bytes, filename)
```

### **Configuration de l'API Langfuse**

Pour activer/désactiver l'envoi direct vs URL, configurez dans `.env` :

```env
# true = envoi direct du PDF en base64 (recommandé)
# false = upload vers un service puis envoi de l'URL
LANGFUSE_SUPPORTS_DIRECT_UPLOAD=true
```

### **Structure attendue de la réponse Langfuse**

L'application s'attend à recevoir une réponse JSON de Langfuse. La méthode `extract_from_bytes()` tente d'extraire le contenu depuis plusieurs clés possibles :
- `content`
- `text`
- `response`

Adaptez cette logique selon la structure de réponse de votre API Langfuse.

## 📊 Fonctionnalités

- Extraction automatique de tableaux d'amortissement depuis des PDF
- **Traitement en mémoire (RAM uniquement)** - aucun fichier temporaire
- Conversion en DataFrame pandas
- Calcul de statistiques (total assurances, intérêts, nombre d'échéances)
- Export en CSV et Excel
- Interface web Streamlit conviviale
- **Compatible avec tous les environnements cloud** (Heroku, AWS, Azure, etc.)

## 🔒 Sécurité et Performance

### **Traitement en mémoire**
- ✅ **Aucun fichier stocké** sur le serveur
- ✅ **Données supprimées automatiquement** après traitement
- ✅ **Compatible cloud** : fonctionne sur Heroku, AWS Lambda, etc.
- ⚡ **Performance optimisée** : pas d'I/O disque

### **Limitations**
- 📏 **Taille maximale recommandée** : 50 MB par fichier
- 💾 **RAM requise** : ~3x la taille du fichier (fichier + base64 + variables)
- 👥 **Concurrence** : La RAM est partagée entre tous les utilisateurs

## 🔄 Migration depuis Google Gemini

Cette application a été migrée de Google Gemini vers Langfuse. Les principales modifications :

1. **Nouvelle configuration** : AUTH_TOKEN, LANGFUSE_PUBLIC_KEY, API_URL au lieu de GOOGLE_GENAI_API_KEY
2. **Nouveau processus** : Upload du fichier + appel API REST au lieu d'appel direct à l'API Gemini
3. **Prompt conservé** : Le prompt d'extraction reste identique
4. **Interface Streamlit** : Mise à jour des messages et de l'aide

## 📁 Structure du projet

```
├── assurance.py          # Module principal d'extraction
├── streamlit_app.py      # Interface web Streamlit
├── requirements.txt      # Dépendances Python
├── .env                 # Configuration locale (à créer)
├── README.md            # Ce fichier
└── start.ps1            # Script de démarrage PowerShell
```

## 🐛 Dépannage

1. **Erreur de configuration** : Vérifiez que tous les paramètres Langfuse sont correctement configurés
2. **Erreur d'upload** : Implémentez la méthode `_upload_file_to_service()` selon votre infrastructure
3. **Erreur de parsing** : Vérifiez que votre PDF contient un tableau d'amortissement lisible

## 📞 Support

Pour toute question ou problème, consultez les logs d'erreur dans l'interface Streamlit ou dans la console Python.