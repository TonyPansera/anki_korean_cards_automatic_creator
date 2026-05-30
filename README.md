# Anki Korean Flashcard Generator

A local web application (Flask + HTML/JS/CSS) that automatically generates Anki flashcards for Korean vocabulary using the OpenAI API and AnkiConnect. The app fetches English translations, Korean definitions, conjugated example sentences, grammatical notes, and Hanja.

## Requirements

- **Python 3.8+**
- **Anki** installed and running
- **AnkiConnect** (Anki add-on - Code: `2055492159`) installed and configured
- An **OpenAI API Key**

## Anki Configuration

1. Make sure the **AnkiConnect** add-on is installed and working in your Anki desktop app.
2. Note the exact name of the Deck you want to use (e.g., `korean_vocab`). You can enter this directly in the web UI.
3. Ensure you have a custom note type (e.g., `Vocab_new_cards`) containing exactly these fields:
   - `Hangeul`
   - `Traduction`
   - `Image`
   - `Definition_kr`
   - `example_korean`
   - `notes`
   - `Hanja`

## Installation

1. Clone or download this repository to your machine.
2. Open a terminal in the project folder:
   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment (Windows)
   .\venv\Scripts\activate
   # On Mac/Linux: source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
3. Create a `.env` file at the root of the project (you can copy `.env.example`) and insert your API key:
   ```env
   OPENAI_API_KEY=sk-YOUR_API_KEY_HERE
   ```

## Startup and Usage

1. Make sure Anki is open in the background.
2. Start the Flask application:
   ```bash
   python app.py
   ```
3. Open your browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000).
4. Verify or change the **Deck Name** and **Note Type (Model)** in the provided input fields to match your Anki setup.
5. Enter your Korean vocabulary words (one word per line) in the text area.
6. Click **Generate and send to Anki**.
7. The app will contact OpenAI to enrich your data, and then automatically send each card to Anki!
