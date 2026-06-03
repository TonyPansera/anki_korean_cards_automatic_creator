import os
import json
import base64
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ANKI_URL = "http://localhost:8765"
DECK_NAME = "korean_vocab"

# Initialize OpenAI client with an explicit timeout to prevent infinite hangs
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    timeout=30.0
)

def invoke_anki(action, **params):
    """Helper to communicate with AnkiConnect."""
    payload = {"action": action, "version": 6, "params": params}
    response = requests.post(ANKI_URL, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if data.get("error"):
        raise Exception(data["error"])
    return data.get("result")

def main():
    if not client.api_key:
        print("Error: OPENAI_API_KEY is not set in the .env file.")
        return

    print(f"Fetching notes from deck: {DECK_NAME}...")
    
    # 1. Find all notes in the target deck
    note_ids = invoke_anki("findNotes", query=f'"deck:{DECK_NAME}"')
    if not note_ids:
        print(f"No notes found in deck '{DECK_NAME}' or Anki is not running.")
        return
    
    print(f"Found {len(note_ids)} notes. Fetching details...")

    # 2. Get note information
    notes_info = invoke_anki("notesInfo", notes=note_ids)
    if not notes_info:
        print("Failed to retrieve note details.")
        return

    updated_count = 0
    error_count = 0

    # 3. Iterate through notes
    for note in notes_info:
        note_id = note["noteId"]
        fields = note["fields"]
        
        example_korean = fields.get("example_korean", {}).get("value", "").strip()
        sound = fields.get("sound", {}).get("value", "").strip()
        hangeul = fields.get("Hangeul", {}).get("value", "").strip()
        
        # Skip if no example sentences
        if not example_korean:
            continue
            
        sentences = [s.strip() for s in example_korean.split("|") if s.strip()]
        
        # Repair previously generated audio to prevent duplicate TTS costs
        if sound and ";;" not in example_korean:
            sound_tags = [s.strip() for s in sound.split("|") if s.strip()]
            if len(sound_tags) == 5 and len(sentences) == 5:
                import re
                new_sentences = []
                for i in range(5):
                    match = re.search(r"\[sound:(.*?)\]", sound_tags[i])
                    if match:
                        new_sentences.append(f"{sentences[i]};;{match.group(1)}")
                
                if len(new_sentences) == 5:
                    try:
                        invoke_anki("updateNoteFields", note={
                            "id": note_id,
                            "fields": {
                                "example_korean": " | ".join(new_sentences)
                            }
                        })
                        print(f"Repaired Note ID {note_id} ('{hangeul}'): Linked existing audio.")
                        updated_count += 1
                    except Exception as e:
                        print(f"Error repairing Note ID {note_id}: {e}")
                        error_count += 1
                    continue

        if sound and ";;" in example_korean:
            print(f"Note ID {note_id} ('{hangeul}') already has audio. Skipping.")
            continue
            
        sentences = [s.strip() for s in example_korean.split("|") if s.strip()]
        
        if len(sentences) != 5:
            print(f"Note ID {note_id} ('{hangeul}') does not have exactly 5 sentences (Found {len(sentences)}). Skipping.")
            error_count += 1
            continue

        print(f"Processing Note ID {note_id} ('{hangeul}'): Generating audio 1-5...")
        
        audio_tags = []
        new_example_sentences = []
        success = True
        
        # 4. Generate TTS and Store in Anki
        for index, sentence in enumerate(sentences):
            # Remove any existing filename if somehow present
            clean_sentence = sentence.split(";;")[0].strip()
            filename = f"korean_audio_{note_id}_{index}.mp3"
            
            try:
                # Call OpenAI TTS
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=clean_sentence
                )
                
                # Convert the binary audio content to base64
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                
                # Store the media file in Anki directly
                stored_filename = invoke_anki("storeMediaFile", filename=filename, data=audio_base64)
                
                if stored_filename:
                    audio_tags.append(f"[sound:{stored_filename}]")
                    new_example_sentences.append(f"{clean_sentence};;{stored_filename}")
                else:
                    raise Exception(f"Failed to store '{filename}' in Anki.")
                    
            except Exception as e:
                print(f"  -> Error generating/storing audio for sentence {index + 1}: {e}")
                success = False
                break
                
        if not success or len(audio_tags) != 5:
            print(f"Failed to complete audio generation for Note ID {note_id}. Skipping update.")
            error_count += 1
            continue
            
        # 5. Update Note Database
        joined_sound_tags = " | ".join(audio_tags)
        joined_examples = " | ".join(new_example_sentences)
        
        try:
            invoke_anki("updateNoteFields", note={
                "id": note_id,
                "fields": {
                    "sound": joined_sound_tags,
                    "example_korean": joined_examples
                }
            })
            print(f"Successfully updated Note ID {note_id} with 5 audio files.")
            updated_count += 1
        except Exception as e:
            print(f"Error updating Note ID {note_id} fields: {e}")
            error_count += 1

    print("\n--- Summary ---")
    print(f"Total Notes Checked: {len(note_ids)}")
    print(f"Successfully Updated: {updated_count}")
    print(f"Errors/Skipped: {error_count}")

if __name__ == "__main__":
    main()
