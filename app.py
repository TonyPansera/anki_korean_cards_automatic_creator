import os
import json
import base64
import uuid
import requests
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Constants
ANKI_URL = "http://localhost:8765"
DECK_NAME = "korean_vocab" # Modifié pour correspondre à votre base
MODEL_NAME = "Vocab_new_cards" # Modifié pour correspondre à votre base

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """You are a strict data parsing backend for a Korean-English dictionary app. Analyze the input list of Korean words. For each word, generate its English translation, a short Korean definition, exactly 5 polite informal example sentences in Korean, helpful grammatical/nuance notes in Korean, and Hanja if applicable. If a word has multiple meanings, duplicate the entry for each meaning.

CRITICAL: Return exclusively a JSON object with a single root key 'cards' containing an array of objects. Each object MUST strictly use these exact field names:
- "Hangeul": The exact word in Korean characters.
- "Traduction": The primary meaning translated clearly into English.
- "Image": Leave this as an empty string ("").
- "Definition_kr": A simple, natural monolingual definition written ENTIRELY in Korean (no French/English).
- "example_korean": A single string containing EXACTLY 5 natural example sentences using the word, separated by the '|' character (e.g., "Sentence 1.|Sentence 2.|..."). Each sentence must be strictly conjugated in the polite informal style (해요체), written ENTIRELY in Korean.
- "notes": Contextual, high-value notes written in Korean.
- "Hanja": Traditional Chinese characters if applicable, otherwise an empty string ("").

Do not include markdown wrappers or extra text."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data or "words" not in data:
        return jsonify({"success": False, "error": "Invalid request. Missing 'words'."}), 400
    
    words_input = data["words"]
    deck_name = data.get("deck_name", DECK_NAME)
    model_name = data.get("model_name", MODEL_NAME)

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
        print("--- OPENAI API RESPONSE ---")
        print(content)
        print("---------------------------")
        cards_data = json.loads(content)
        cards = cards_data.get("cards", [])

    except Exception as e:
        return jsonify({"success": False, "error": f"LLM API Error: {str(e)}"}), 500
    
    # Process cards and send to Anki
    success_count = 0
    errors = []
    
    for card in cards:
        hangeul = card.get("Hangeul", "")
        example_korean = card.get("example_korean", "")
        
        # --- TTS AUDIO GENERATION ---
        audio_tags = []
        new_example_sentences = []
        sentences = [s.strip() for s in example_korean.split("|") if s.strip()]
        
        if len(sentences) == 5:
            note_id_temp = str(uuid.uuid4())[:8] # short unique identifier for media files
            for idx, sentence in enumerate(sentences):
                filename = f"korean_audio_{note_id_temp}_{idx}.mp3"
                try:
                    # Call OpenAI TTS
                    tts_response = client.audio.speech.create(
                        model="tts-1",
                        voice="alloy",
                        input=sentence
                    )
                    audio_base64 = base64.b64encode(tts_response.content).decode('utf-8')
                    
                    # Store media file in Anki
                    store_payload = {
                        "action": "storeMediaFile",
                        "version": 6,
                        "params": {
                            "filename": filename,
                            "data": audio_base64
                        }
                    }
                    store_res = requests.post(ANKI_URL, json=store_payload, timeout=30).json()
                    
                    if store_res.get("error"):
                        errors.append(f"Media Error for '{hangeul}' ({idx+1}/5): {store_res['error']}")
                    else:
                        stored_filename = store_res.get('result', filename)
                        audio_tags.append(f"[sound:{stored_filename}]")
                        new_example_sentences.append(f"{sentence};;{stored_filename}")
                except Exception as e:
                    errors.append(f"TTS Error for '{hangeul}' ({idx+1}/5): {str(e)}")
        else:
            errors.append(f"Warning: '{hangeul}' generated {len(sentences)} sentences instead of 5. Audio skipped.")

        joined_sound_tags = " | ".join(audio_tags) if len(audio_tags) == 5 else ""
        joined_examples = " | ".join(new_example_sentences) if len(new_example_sentences) == 5 else example_korean

        # Ensure all required fields exist
        fields = {
            "Hangeul": hangeul,
            "Traduction": card.get("Traduction", ""),
            "Image": "", # Forced to empty string as per requirements
            "Definition_kr": card.get("Definition_kr", ""),
            "example_korean": joined_examples,
            "notes": card.get("notes", ""),
            "Hanja": card.get("Hanja", ""),
            "sound": joined_sound_tags
        }
        
        anki_payload = {
            "action": "addNote",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deck_name,
                    "modelName": model_name,
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

    if success_count == 0 and errors:
        return jsonify({
            "success": False,
            "error": f"Anki refused the addition. First error: {errors[0]}",
            "errors": errors
        }), 400

    return jsonify({
        "success": True, 
        "message": f"Success! {success_count} cards created successfully.",
        "success_count": success_count,
        "errors": errors,
        "total_attempted": len(cards)
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
