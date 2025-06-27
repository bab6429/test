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

# Vérification du fichier .env
env_file_exists = os.path.exists('.env')
if env_file_exists:
    st.sidebar.success("✅ Fichier .env détecté")
else:
    st.sidebar.error("❌ Fichier .env non trouvé")
    st.sidebar.markdown("Créez un fichier `.env` avec votre clé API Google Gemini")

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
            if not env_file_exists:
                st.error("❌ Impossible de continuer sans le fichier .env")
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
    **Fichiers nécessaires :**
    - `.env` : Contient votre clé API Google Gemini
    - `requirements.txt` : Liste des dépendances Python
    
    **Contenu du fichier .env :**
    ```
    GOOGLE_GENAI_API_KEY=votre_cle_api_ici
    ```
    
    **Installation des dépendances :**
    ```bash
    pip install -r requirements.txt
    ```
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
    1. Configurez votre fichier `.env` avec la clé API Google Gemini
    2. Uploadez votre fichier PDF contenant le tableau d'amortissement
    3. Cliquez sur "Extraire le tableau d'amortissement"
    4. Consultez les résultats et exportez en CSV ou Excel
    """)

# Footer
st.markdown("---")
st.markdown("*Développé avec Streamlit et l'API Google Gemini*")
