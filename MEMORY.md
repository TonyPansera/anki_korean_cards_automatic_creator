# Memory & Context

## System Architecture
- **Backend**: Python (Flask). Serves the frontend and handles API requests.
- **Frontend**: HTML5, CSS3, Vanilla JS. Single Page Application (SPA).
- **LLM Integration**: OpenAI API (using `gpt-4o`). The prompt forces JSON output (`response_format={"type": "json_object"}`).
- **Anki Integration**: Uses AnkiConnect (`http://localhost:8765`).

## Key Project Files
- `app.py`: Flask server, handles the `/api/generate` route.
- `requirements.txt`: Python dependencies.
- `templates/index.html`: The HTML layout.
- `static/style.css`: Dark mode modern styling.
- `static/script.js`: Client-side fetch logic.

## Design Notes
- **Anki Deck Target**: Dynamically input from UI (defaults to `korean_vocab`)
- **Anki Note Type Target**: Dynamically input from UI (defaults to `Vocab_new_cards`)
- Duplicate checking is enabled (no duplicates allowed).
- The `Image` field is strictly passed as empty.
- The `example_korean` field stores exactly 5 example sentences joined by the `|` character. To support JS-based audio playback without triggering Anki's global autoplay, each sentence also has its associated audio filename appended via a `;;` separator (e.g., `Sentence;;filename.mp3 | Sentence2;;filename2.mp3`).
- **Audio/TTS Integration**: A `sound` field has been added. The backend generates 5 TTS MP3 files (using OpenAI's `alloy` voice) for the 5 example sentences, stores them in Anki via `storeMediaFile`, and joins the `[sound:...]` tags with `|` in the `sound` field (which is kept hidden to prevent autoplay, but required so Anki doesn't delete the media files). A standalone script `update_audio.py` is available to retroactively add audio to older cards, and includes logic to safely skip or repair cards without double-charging the API.
- **OpenAI Timeout**: The OpenAI client is configured with a strict 30-second timeout to prevent the script from freezing due to network issues or API rate-limiting.

## Future Enhancements
- (Empty for now - add ideas here)
