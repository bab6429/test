import streamlit as st
import pandas as pd
import os
from io import BytesIO
from assurance import AmortizationExtractor

# Configuration de la page
st.set_page_config(
    page_title="Extracteur de Tableau d'Amortissement",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Extracteur de Tableau d'Amortissement")
st.markdown("---")

# Description
st.markdown("""
Cette application permet d'extraire automatiquement les tableaux d'amortissement depuis des fichiers PDF 
en utilisant l'API Google Gemini et de les convertir en format structuré (DataFrame/CSV).
""")

# Sidebar pour la configuration
st.sidebar.header("⚙️ Configuration")

# Vérification de la disponibilité de la clé API
def check_api_key_availability():
    """Vérifie si la clé API est disponible dans les secrets ou le fichier .env"""
    # Vérifier les secrets Streamlit
    try:
        api_key_from_secrets = st.secrets.get("GOOGLE_GENAI_API_KEY")
        if api_key_from_secrets:
            return True, "secrets"
    except (AttributeError, FileNotFoundError, KeyError):
        pass
    
    # Vérifier le fichier .env
    env_file_exists = os.path.exists('.env')
    if env_file_exists:
        from dotenv import load_dotenv
        load_dotenv()
        api_key_from_env = os.getenv('GOOGLE_GENAI_API_KEY')
        if api_key_from_env:
            return True, "env"
    
    return False, None

api_available, source = check_api_key_availability()

if api_available:
    if source == "secrets":
        st.sidebar.success("✅ Clé API configurée (Secrets Streamlit)")
    else:
        st.sidebar.success("✅ Clé API configurée (Fichier .env)")
else:
    st.sidebar.error("❌ Clé API non trouvée")
    st.sidebar.markdown("Configurez la clé API dans les secrets Streamlit ou créez un fichier `.env`")

# Interface principale
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Upload du fichier PDF")
    
    # Upload de fichier
    uploaded_file = st.file_uploader(
        "Choisissez un fichier PDF contenant un tableau d'amortissement",
        type=['pdf'],
        help="Le fichier doit contenir un tableau d'amortissement lisible"
    )
    
    if uploaded_file is not None:
        st.success(f"Fichier uploadé : {uploaded_file.name}")
        
        # Bouton pour lancer l'extraction
        if st.button("🚀 Extraire le tableau d'amortissement", type="primary"):
            if not api_available:
                st.error("❌ Impossible de continuer sans la clé API configurée")
            else:
                # Sauvegarde temporaire du fichier
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                try:
                    # Initialisation de l'extracteur
                    with st.spinner("🔄 Initialisation de l'extracteur..."):
                        extractor = AmortizationExtractor()
                    
                    # Extraction des données
                    with st.spinner("🔍 Extraction des données du PDF..."):
                        df = extractor.process_pdf_to_dataframe(temp_path)
                    
                    # Nettoyage du fichier temporaire
                    os.remove(temp_path)
                    
                    if df is not None:
                        st.session_state['dataframe'] = df
                        
                        # Calcul des statistiques
                        stats = extractor.calculer_statistiques(df)
                        st.session_state['stats'] = stats
                        
                        st.success("✅ Extraction réussie !")
                    else:
                        st.error("❌ Échec de l'extraction. Vérifiez le format du PDF.")
                        
                except Exception as e:
                    # Nettoyage du fichier temporaire en cas d'erreur
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    st.error(f"❌ Erreur lors de l'extraction : {str(e)}")

with col2:
    st.header("📊 Résultats")
    
    # Affichage des résultats si disponibles
    if 'dataframe' in st.session_state and 'stats' in st.session_state:
        df = st.session_state['dataframe']
        stats = st.session_state['stats']
        
        # Statistiques principales demandées
        st.subheader("� Statistiques principales")
        
        col_stat1, col_stat2 = st.columns(2)
        col_stat3, col_stat4 = st.columns(2)
        
        with col_stat1:
            st.metric(
                "💰 Total Assurances", 
                f"{stats['total_assurances']:,.2f} €",
                help="Somme de toutes les valeurs du champ 'Assurances'"
            )
        
        with col_stat2:
            st.metric(
                "💸 Total Intérêts", 
                f"{stats['total_interets']:,.2f} €",
                help="Somme de tous les intérêts"
            )
        
        with col_stat3:
            st.metric(
                "📅 Première échéance", 
                stats['premiere_echeance'],
                help="Date de la première échéance du tableau"
            )
        
        with col_stat4:
            st.metric(
                "📊 Nombre d'échéances", 
                stats['nombre_echeances'],
                help="Nombre total d'échéances dans le tableau"
            )
        
        # Affichage du tableau
        st.subheader("📋 Tableau d'amortissement")
        st.dataframe(df, use_container_width=True)
        
        # Options d'export
        st.subheader("💾 Export des données")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger en CSV",
                data=csv,
                file_name="tableau_amortissement.csv",
                mime="text/csv"
            )
        
        with col_export2:
            # Export Excel - avec gestion d'erreur pour openpyxl
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Amortissement')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 Télécharger en Excel",
                    data=excel_data,
                    file_name="tableau_amortissement.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.error("❌ Module openpyxl manquant. Installez-le avec : pip install openpyxl")
            except Exception as e:
                st.error(f"❌ Erreur lors de la création du fichier Excel : {str(e)}")
    
    else:
        st.info("👆 Uploadez un fichier PDF pour voir les résultats ici")

# Section d'aide
st.markdown("---")
st.header("❓ Aide")

with st.expander("🔧 Configuration requise"):
    st.markdown("""
    **Configuration de la clé API :**
    
    **Option 1 - Streamlit Cloud (Recommandé) :**
    1. Allez dans les paramètres de votre app sur Streamlit Cloud
    2. Section "Secrets"
    3. Ajoutez votre clé API :
    ```toml
    GOOGLE_GENAI_API_KEY = "votre_cle_api_ici"
    ```
    
    **Option 2 - Développement local :**
    - Créez un fichier `.env` avec :
    ```
    GOOGLE_GENAI_API_KEY=votre_cle_api_ici
    ```
    
    **Installation des dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
    """)

with st.expander("🔐 Configuration des secrets Streamlit Cloud"):
    st.markdown("""
    **Étapes pour configurer les secrets sur Streamlit Cloud :**
    
    1. **Accédez à votre app** sur [share.streamlit.io](https://share.streamlit.io)
    2. **Cliquez sur les 3 points** à droite de votre app
    3. **Sélectionnez "Settings"**
    4. **Allez dans l'onglet "Secrets"**
    5. **Ajoutez votre configuration** au format TOML :
    
    ```toml
    GOOGLE_GENAI_API_KEY = "AIza..."
    ```
    
    6. **Cliquez sur "Save"**
    7. **Votre app va redémarrer** automatiquement
    
    ⚠️ **Important :** Les secrets sont chiffrés et sécurisés sur Streamlit Cloud.
    """)

with st.expander("📄 Format de fichier supporté"):
    st.markdown("""
    **Format attendu :**
    - Fichiers PDF contenant des tableaux d'amortissement
    - Le tableau doit être clairement structuré avec les colonnes :
      - Date d'échéance
      - Amortissements
      - Intérêts
      - Assurances
      - Capital restant dû
    """)

with st.expander("🚀 Utilisation"):
    st.markdown("""
    **Étapes :**
    1. **Configurez votre clé API** :
       - Sur Streamlit Cloud : Utilisez les secrets (voir section dédiée)
       - En local : Créez un fichier `.env` avec votre clé API Google Gemini
    2. **Uploadez votre fichier PDF** contenant le tableau d'amortissement
    3. **Cliquez sur "Extraire le tableau d'amortissement"**
    4. **Consultez les résultats** et exportez en CSV ou Excel
    
    **Note :** L'application détecte automatiquement si vous utilisez Streamlit Cloud ou un environnement local.
    """)

# Footer
st.markdown("---")
st.markdown("*Développé avec Streamlit et l'API Google Gemini*")
