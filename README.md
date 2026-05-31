# Anki Korean Flashcard Generator

A local web application (Flask + HTML/JS/CSS) that automatically generates Anki flashcards for Korean vocabulary using the OpenAI API and AnkiConnect. The app fetches English translations, Korean definitions, exactly 5 conjugated example sentences (separated by '|'), grammatical notes, and Hanja.

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
4. For the custom card, please put this code in the back template:

*To edit the card code, please go to Tools > Manage Note Types > (you custom created card) > Cards, then you can edit the front and back template.*
```html
{{FrontSide}}

<hr id=answer>

{{Traduction}}

<div style='font-family: "Arial"; font-size: 20px;'>Definition: {{Definition_kr}}</div>

{{#Hanja}}
<div style='font-family: "Arial"; font-size: 20px;'>漢字: {{Hanja}}</div>
{{/Hanja}}

<div id="raw-examples" style="display: none;">{{example_korean}}</div>

<div style='font-family: "Arial"; font-size: 20px;'>
    Example: <span id="random-example"></span>
</div>

<div style='font-family: "Arial"; font-size: 20px;'>{{Image}}</div>

<div style='font-family: "Arial"; font-size: 20px;'>Notes: {{notes}}</div>

<script>
  (function() {
    var rawElement = document.getElementById("raw-examples");
    var rawText = rawElement.innerText || rawElement.textContent;
    
    var sentences = rawText.split("|").filter(function(s) { 
        return s.trim() !== ""; 
    });
    
    if (sentences.length > 0) {
      var randomIndex = Math.floor(Math.random() * sentences.length);
      document.getElementById("random-example").innerText = sentences[randomIndex].trim();
    } else {
      document.getElementById("random-example").innerText = "Aucun exemple disponible.";
    }
  })();
</script>
```

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
