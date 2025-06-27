# -*- coding: utf-8 -*-
"""
Module d'extraction et traitement de tableaux d'amortissement à partir de fichiers PDF
Utilise l'API Google Gemini pour extraire les données et les convertir en DataFrame
"""

import os
import json
import pandas as pd
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import Optional

# Charger les variables d'environnement
load_dotenv()


class AmortizationExtractor:
    """Classe pour extraire et traiter les tableaux d'amortissement depuis des fichiers PDF"""
    
    def __init__(self):
        """Initialise le client Gemini avec la clé API depuis le fichier .env"""
        api_key = os.getenv('GOOGLE_GENAI_API_KEY')
        if not api_key:
            raise ValueError("La clé API GOOGLE_GENAI_API_KEY n'est pas définie dans le fichier .env")
        
        self.client = genai.Client(api_key=api_key)
        self.prompt = '''Peux tu m extraires de ce fichier le tableau d amortissement et générer un le résultat sous la forme d un json comme ceci :
[
    {
        "Date d'écheance" : "JJ/MM/AAAA",
        "amortissements" : "xx",
        "Interet" : "xx",
        "Assurances" : "xx",
        "capital restant du" : "xx",
    }
]

Tu dois générer le contenu sous la forme d'un json et uniquement un json. Ton json doit etre complet et tu ne dois oublier aucune ligne de ce tableau d'amortissement. Ton output devra etre une base pour que je puisse ensuite créer un csv à partir de ce json donc il faut qu'il soit complet
'''

    def extract_from_pdf(self, pdf_path: str) -> str:
        """
        Extrait le tableau d'amortissement d'un fichier PDF
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Réponse brute de l'API Gemini
            
        Raises:
            FileNotFoundError: Si le fichier PDF n'existe pas
            Exception: Pour les autres erreurs d'extraction
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier '{pdf_path}' n'a pas été trouvé.")
        
        try:
            # Lecture du fichier PDF
            with open(pdf_path, 'rb') as f:
                doc_data = f.read()

            # Appel à l'API Gemini
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=doc_data,
                        mime_type='application/pdf',
                    ),
                    self.prompt
                ])
            
            return response.text
            
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")

    def convertir_llm_output_en_dataframe(self, llm_output: str) -> Optional[pd.DataFrame]:
        """
        Nettoie la sortie brute d'un LLM pour en extraire un JSON et le convertit en DataFrame Pandas.

        Cette fonction est conçue pour être robuste face à du texte ou des balises
        markdown (comme ```json) qui peuvent entourer le contenu JSON réel.

        Args:
            llm_output: La chaîne de caractères complète retournée par le LLM.

        Returns:
            Un DataFrame Pandas si la conversion réussit, sinon None.
        """
        print("--- Tentative de nettoyage et d'extraction du JSON ---")

        try:
            # 1. Isoler le JSON : trouver le premier '[' et le dernier ']'
            # C'est une méthode simple et efficace pour ignorer le texte environnant.
            debut_json = llm_output.find('[')
            fin_json = llm_output.rfind(']') + 1

            # Vérification si les délimiteurs JSON ont été trouvés
            if debut_json == -1 or fin_json == 0:
                print("ERREUR : Impossible de trouver le début ou la fin du JSON (caractères '[' et ']').")
                return None

            # Extraire la chaîne de caractères contenant uniquement le JSON
            json_isole = llm_output[debut_json:fin_json]
            print("JSON isolé avec succès.")

            # 2. Charger le JSON en objet Python
            # json.loads() transforme la chaîne de caractères en une liste de dictionnaires
            donnees_python = json.loads(json_isole)

            # 3. Créer le DataFrame avec Pandas
            df = pd.DataFrame(donnees_python)

            # 4. (Optionnel mais recommandé) Convertir les colonnes aux bons types
            # S'assure que la colonne de date est bien un objet date et non du texte
            if "Date d'echeance" in df.columns:
                df["Date d'echeance"] = pd.to_datetime(df["Date d'echeance"], format='%d/%m/%Y')

            print("Conversion en DataFrame Pandas réussie.")
            return df

        except json.JSONDecodeError:
            print(f"ERREUR : La chaîne extraite n'est pas un JSON valide.\nContenu extrait : {json_isole}")
            return None
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")
            return None

    def process_pdf_to_dataframe(self, pdf_path: str) -> Optional[pd.DataFrame]:
        """
        Traite un fichier PDF complet : extraction + conversion en DataFrame
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            DataFrame contenant le tableau d'amortissement ou None en cas d'erreur
        """
        try:
            # Extraction du contenu
            llm_output = self.extract_from_pdf(pdf_path)
            
            # Conversion en DataFrame
            df = self.convertir_llm_output_en_dataframe(llm_output)
            
            return df
            
        except Exception as e:
            print(f"Erreur lors du traitement complet : {str(e)}")
            return None

    def calculer_statistiques(self, df: pd.DataFrame) -> dict:
        """
        Calcule les statistiques du tableau d'amortissement
        
        Args:
            df: DataFrame contenant le tableau d'amortissement
            
        Returns:
            Dictionnaire avec les statistiques calculées
        """
        stats = {}
        
        try:
            # Total des assurances
            if 'Assurances' in df.columns:
                assurances_values = df['Assurances'].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('€', '')
                assurances_numeric = pd.to_numeric(assurances_values, errors='coerce').fillna(0)
                stats['total_assurances'] = assurances_numeric.sum()
            else:
                stats['total_assurances'] = 0
            
            # Total des intérêts
            if 'Interet' in df.columns:
                interet_values = df['Interet'].astype(str).str.replace(',', '.').str.replace(' ', '').str.replace('€', '')
                interet_numeric = pd.to_numeric(interet_values, errors='coerce').fillna(0)
                stats['total_interets'] = interet_numeric.sum()
            else:
                stats['total_interets'] = 0
            
            # Première date d'échéance
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'echeance' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                try:
                    # Essayer de convertir en date
                    dates = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
                    if not dates.isna().all():
                        stats['premiere_echeance'] = dates.min().strftime('%d/%m/%Y')
                    else:
                        # Si la conversion échoue, prendre la première valeur
                        stats['premiere_echeance'] = str(df[date_col].iloc[0])
                except:
                    stats['premiere_echeance'] = str(df[date_col].iloc[0])
            else:
                stats['premiere_echeance'] = "Non trouvé"
            
            # Nombre d'échéances
            stats['nombre_echeances'] = len(df)
            
            return stats
            
        except Exception as e:
            print(f"Erreur lors du calcul des statistiques : {str(e)}")
            return {
                'total_assurances': 0,
                'total_interets': 0,
                'premiere_echeance': "Erreur",
                'nombre_echeances': 0
            }


def main():
    """Fonction principale pour tester le module"""
    # Exemple d'utilisation
    extractor = AmortizationExtractor()
    
    # Chemin vers votre fichier PDF (à adapter selon votre environnement)
    pdf_path = "/content/2025 07_tableau-amortissement_Modulation 24 M (1).pdf"
    
    # Si vous êtes sur Windows, utilisez un chemin comme :
    # pdf_path = r"C:\Users\votre_nom\Documents\votre_fichier.pdf"
    
    # Traitement du PDF
    df = extractor.process_pdf_to_dataframe(pdf_path)
    
    if df is not None:
        print("DataFrame créé avec succès :")
        print(df.head())
        
        # Calcul des statistiques
        stats = extractor.calculer_statistiques(df)
        print("\nStatistiques :")
        print(f"Total assurances : {stats['total_assurances']:.2f} €")
        print(f"Total intérêts : {stats['total_interets']:.2f} €")
        print(f"Première échéance : {stats['premiere_echeance']}")
        print(f"Nombre d'échéances : {stats['nombre_echeances']}")
        
        # Optionnel : sauvegarde en CSV
        df.to_csv("tableau_amortissement.csv", index=False)
        print("Fichier CSV sauvegardé : tableau_amortissement.csv")
    else:
        print("Échec du traitement du PDF")


if __name__ == "__main__":
    main()