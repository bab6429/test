# streamlit_app.py

import streamlit as st
from assurance import LangfuseProcessor # Importe la classe du fichier assurance.py

st.set_page_config(page_title="Analyseur de PDF", layout="centered")

st.title("📄 Analyseur de documents PDF avec Langfuse")

# --- Configuration et initialisation ---
# Utilisation de st.secrets pour une gestion sécurisée des clés
try:
    processor = LangfuseProcessor(
        auth_token=st.secrets["langfuse"]["auth_token"],
        api_url=st.secrets["langfuse"]["api_url"],
        prompt_name=st.secrets["langfuse"]["prompt_name"],
        langfuse_public_key=st.secrets["langfuse"]["langfuse_public_key"],
        prompt_version=st.secrets["langfuse"]["prompt_version"]
    )
except (KeyError, FileNotFoundError):
    st.error("⚠️ La configuration de l'API Langfuse est manquante.")
    st.info("Veuillez créer un fichier .streamlit/secrets.toml avec vos identifiants.")
    st.code("""
# .streamlit/secrets.toml
[langfuse]
auth_token = "VOTRE_TOKEN_ICI"
api_url = "URL_DE_VOTRE_API_ICI"
prompt_name = "NOM_DU_PROMPT"
langfuse_public_key = "VOTRE_CLE_PUBLIQUE_LANGFUSE"
prompt_version = "VERSION_DU_PROMPT"
    """)
    st.stop()


# --- Interface d'upload ---
uploaded_file = st.file_uploader(
    "Chargez votre fichier PDF ici pour l'analyser.",
    type="pdf"
)

if uploaded_file is not None:
    st.success(f"Fichier **{uploaded_file.name}** prêt à être analysé.")
    
    # Bouton pour lancer l'analyse
    if st.button("Lancer l'analyse ✨"):
        # Lire les données binaires du fichier uploadé
        pdf_bytes = uploaded_file.getvalue()
        
        # Afficher un spinner pendant le traitement
        with st.spinner("Analyse en cours... Merci de patienter."):
            try:
                # Appeler la méthode d'analyse de notre classe
                result = processor.analyze_pdf(
                    pdf_bytes=pdf_bytes, 
                    pdf_name=uploaded_file.name
                )
                
                st.success("Analyse terminée avec succès !")
                st.subheader("Résultat de l'analyse :")
                st.json(result) # Afficher le JSON de réponse de manière formatée
                
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'analyse :")
                st.exception(e)