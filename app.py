import os
import json
import requests
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Constants
ANKI_URL = "http://localhost:8765"
DECK_NAME = "Coréen::Vocabulaire"
MODEL_NAME = "Coréen - Parfait"

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a strict data parsing backend for a Korean-French dictionary app. Analyze the input list of Korean words. For each word, generate its French translation, a short Korean definition, a polite informal example sentence in Korean, helpful grammatical/nuance notes in French, and Hanja if applicable. If a word has multiple meanings, duplicate the entry for each meaning. Return exclusively a JSON object with a single root key 'cards' containing an array of objects matching the specified schema fields. Do not include markdown wrappers or extra text."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"success": False, "error": "Invalid request. Missing 'words'."}), 400
    
    words_input = data["words"]
    # Filter empty lines
    words_list = [w.strip() for w in words_input.split("\n") if w.strip()]
    
    if not words_list:
        return jsonify({"success": False, "error": "The word list is empty."}), 400

    if not client.api_key:
         return jsonify({"success": False, "error": "OpenAI API key is missing. Please set it in your .env file."}), 500

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o", # Using gpt-4o as default for structured output, could be gpt-3.5-turbo if needed
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Words to process:\n" + "\n".join(words_list)}
            ],
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        cards_data = json.loads(content)
        cards = cards_data.get("cards", [])

    except Exception as e:
        return jsonify({"success": False, "error": f"LLM API Error: {str(e)}"}), 500
    
    # Process cards and send to Anki
    success_count = 0
    errors = []
    
    for card in cards:
        # Ensure all required fields exist
        fields = {
            "Hangeul": card.get("Hangeul", ""),
            "Traduction": card.get("Traduction", ""),
            "Image": "", # Forced to empty string as per requirements
            "Definition_kr": card.get("Definition_kr", ""),
            "example_korean": card.get("example_korean", ""),
            "notes": card.get("notes", ""),
            "Hanja": card.get("Hanja", "")
        }
        
        anki_payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": DECK_NAME,
                    "modelName": MODEL_NAME,
                    "fields": fields,
                    "options": {
                        "allowDuplicate": False
                    }
                }
            }
        }
        
        try:
            anki_response = requests.post(ANKI_URL, json=anki_payload, timeout=5)
            anki_result = anki_response.json()
            
            if anki_result.get("error"):
                errors.append(f"Anki Error for '{fields['Hangeul']}': {anki_result['error']}")
            else:
                success_count += 1
        except requests.exceptions.RequestException as e:
            # If AnkiConnect is not running
            return jsonify({
                "success": False,
                "error": "Could not connect to AnkiConnect. Is Anki running with AnkiConnect installed?"
            }), 500

    return jsonify({
        "success": True, 
        "message": f"Succès ! {success_count} cartes créées avec succès.",
        "success_count": success_count,
        "errors": errors,
        "total_attempted": len(cards)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
