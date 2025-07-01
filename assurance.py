# assurance.py

import requests
import re
import json
import base64

class LangfuseProcessor:
    """
    Une classe pour encapsuler la logique d'envoi de PDF à l'API Langfuse.
    """
    def __init__(self, auth_token: str, api_url: str, prompt_name: str, 
                 langfuse_public_key: str, prompt_version: str):
        """
        Initialise le processeur avec la configuration nécessaire.
        """
        if not all([auth_token, api_url, prompt_name, langfuse_public_key, prompt_version]):
            raise ValueError("Tous les paramètres de configuration doivent être fournis.")
            
        self.auth_token = auth_token
        self.api_url = api_url
        self.prompt_name = prompt_name
        self.langfuse_public_key = langfuse_public_key
        self.prompt_version = prompt_version

    def _process_langfuse_response(self, response: requests.Response):
        """
        Traite la réponse de l'API et extrait le contenu généré par le LLM.
        """
        try:
            # Vérifier le statut de la réponse
            response.raise_for_status()
            
            # Parser la réponse JSON complète
            response_data = response.json()
            
            # Extraire le contenu du LLM depuis le champ 'content'
            if 'content' in response_data:
                llm_output = response_data['content']
                print(f"Contenu trouvé, longueur: {len(llm_output)}")
                
                # Le contenu contient ```json\n[...]\n```
                # Extraire le JSON entre les balises markdown
                json_match = re.search(r'```json\n(.*?)\n```', llm_output, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    try:
                        json_content = json.loads(json_str)
                        print("✅ JSON extrait avec succès depuis les balises markdown")
                        return json_content
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Erreur de parsing JSON: {e}")
                        return {"raw_content": llm_output, "error": str(e)}
                else:
                    print("⚠️ Aucune balise JSON markdown trouvée, retour du contenu brut")
                    return {"raw_content": llm_output}
            else:
                print("❌ Pas de champ 'content' trouvé dans la réponse")
                available_fields = list(response_data.keys()) if isinstance(response_data, dict) else []
                return {"error": "Pas de contenu trouvé", "available_fields": available_fields}
                
        except requests.exceptions.HTTPError as e:
            print(f"❌ Erreur HTTP : {e}")
            return {"error": f"HTTP Error: {e}", "status_code": response.status_code}
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de décodage JSON : {e}")
            return {"error": f"JSON Decode Error: {e}", "raw_response": response.text}
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return {"error": f"Unexpected error: {e}"}
        

    def _send_pdf_direct(self, doc_data: bytes, pdf_path: str) -> dict or str:
        """
        Envoie le PDF directement à Langfuse (encodé en base64)
        
        Args:
            doc_data: Données binaires du PDF
            pdf_path: Chemin du fichier (pour le nom)
            
        Returns:
            Réponse de l'API Langfuse
        """
        # Encodage du PDF en base64
        pdf_base64 = base64.b64encode(doc_data).decode('utf-8')
        pdf_base64_uri = f"data:application/pdf;base64,{pdf_base64}"
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        # Payload avec fichier en base64
        payload = {
            "structured_output": False,
            "streaming": True,
            "prompt_name": self.prompt_name,
            "langfuse_public_key": self.langfuse_public_key,
            "prompt_version": self.prompt_version,
            "user_parameters": {},
            "attachments": [pdf_base64_uri],
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        return self._process_langfuse_response(response)

    def analyze_pdf(self, pdf_bytes: bytes, pdf_name: str):
        """
        Méthode publique pour lancer l'analyse d'un PDF.
        C'est cette méthode que l'interface Streamlit appellera.
        """
        print(f"Analyse du fichier '{pdf_name}'...")
        return self._send_pdf_direct(doc_data=pdf_bytes, pdf_path=pdf_name)