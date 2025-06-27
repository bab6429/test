# Script de démarrage pour l'application d'extraction de tableaux d'amortissement
# Exécuter avec : powershell -ExecutionPolicy Bypass -File start.ps1

Write-Host "🚀 Démarrage de l'application d'extraction de tableaux d'amortissement" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Blue

# Vérification de Python
Write-Host "🔍 Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python détecté : $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python depuis https://python.org" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour quitter"
    exit 1
}

# Vérification du fichier .env
Write-Host "🔍 Vérification du fichier .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Fichier .env trouvé" -ForegroundColor Green
} else {
    Write-Host "❌ Fichier .env non trouvé" -ForegroundColor Red
    Write-Host "Création du fichier .env..." -ForegroundColor Yellow
    
    $apiKey = Read-Host "Entrez votre clé API Google Gemini"
    "GOOGLE_GENAI_API_KEY=$apiKey" | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Fichier .env créé" -ForegroundColor Green
}

# Installation des dépendances
Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt --quiet
    Write-Host "✅ Dépendances installées avec succès" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
    Write-Host "Erreur : $_" -ForegroundColor Red
    Read-Host "Appuyez sur Entrée pour continuer quand même"
}

# Lancement de l'application Streamlit
Write-Host "🌐 Lancement de l'application Streamlit..." -ForegroundColor Yellow
Write-Host "L'application va s'ouvrir dans votre navigateur par défaut" -ForegroundColor Cyan
Write-Host "Pour arrêter l'application, utilisez Ctrl+C" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Blue

try {
    streamlit run streamlit_app.py
} catch {
    Write-Host "❌ Erreur lors du lancement de l'application" -ForegroundColor Red
    Write-Host "Erreur : $_" -ForegroundColor Red
    Write-Host "Vérifiez que streamlit est installé : pip install streamlit" -ForegroundColor Yellow
    Read-Host "Appuyez sur Entrée pour quitter"
}
