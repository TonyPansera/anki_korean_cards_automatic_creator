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
- **Anki Deck Target**: `Coréen::Vocabulaire`
- **Anki Note Type Target**: `Coréen - Parfait`
- Duplicate checking is enabled (no duplicates allowed).
- The `Image` field is strictly passed as empty.

## Future Enhancements
- (Empty for now - add ideas here)
