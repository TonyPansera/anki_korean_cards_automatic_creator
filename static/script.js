document.addEventListener("DOMContentLoaded", () => {
    const generateBtn = document.getElementById("generate-btn");
    const wordsInput = document.getElementById("words-input");
    const statusContainer = document.getElementById("status-container");
    const statusMessage = document.getElementById("status-message");

    const setStatus = (state, message) => {
        // Remove all state classes
        statusContainer.classList.remove("idle", "loading", "success", "error");
        
        // Add new state class
        statusContainer.classList.add(state);
        
        // Update text
        statusMessage.textContent = message;
    };

    generateBtn.addEventListener("click", async () => {
        const words = wordsInput.value.trim();
        const deckName = document.getElementById("deck-input").value.trim();
        const modelName = document.getElementById("model-input").value.trim();
        
        if (!words) {
            setStatus("error", "Error: Please enter at least one word.");
            return;
        }

        if (!deckName || !modelName) {
            setStatus("error", "Error: Deck Name and Note Type cannot be empty.");
            return;
        }

        // Disable UI
        generateBtn.disabled = true;
        wordsInput.disabled = true;
        document.getElementById("deck-input").disabled = true;
        document.getElementById("model-input").disabled = true;
        
        // Set loading state
        setStatus("loading", "⏳ Processing via AI and sending to Anki...");

        try {
            const response = await fetch("/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ 
                    words: words,
                    deck_name: deckName,
                    model_name: modelName
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                setStatus("error", `Error: ${data.error || "An unknown error occurred."}`);
            } else {
                let successMsg = `✅ Success! ${data.success_count} cards created successfully.`;
                if (data.errors && data.errors.length > 0) {
                    successMsg += `\nHowever, ${data.errors.length} error(s) occurred (see console).`;
                    console.error("Anki Errors:", data.errors);
                }
                setStatus("success", successMsg);
                wordsInput.value = ""; // Clear input on success
            }
        } catch (error) {
            console.error("Network Error:", error);
            setStatus("error", "Network Error: Could not connect to the server.");
        } finally {
            // Re-enable UI
            generateBtn.disabled = false;
            wordsInput.disabled = false;
            document.getElementById("deck-input").disabled = false;
            document.getElementById("model-input").disabled = false;
            wordsInput.focus();
        }
    });
});
