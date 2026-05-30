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
        
        if (!words) {
            setStatus("error", "Erreur : Veuillez entrer au moins un mot.");
            return;
        }

        // Disable UI
        generateBtn.disabled = true;
        wordsInput.disabled = true;
        
        // Set loading state
        setStatus("loading", "⏳ Traitement par l'IA et envoi à Anki en cours...");

        try {
            const response = await fetch("/api/generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ words: words })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                setStatus("error", `Erreur : ${data.error || "Une erreur inconnue s'est produite."}`);
            } else {
                let successMsg = `✅ Succès ! ${data.success_count} cartes créées avec succès.`;
                if (data.errors && data.errors.length > 0) {
                    successMsg += `\nCependant, ${data.errors.length} erreur(s) ont eu lieu (voir console).`;
                    console.error("Anki Errors:", data.errors);
                }
                setStatus("success", successMsg);
                wordsInput.value = ""; // Clear input on success
            }
        } catch (error) {
            console.error("Network Error:", error);
            setStatus("error", "Erreur réseau : Impossible de contacter le serveur.");
        } finally {
            // Re-enable UI
            generateBtn.disabled = false;
            wordsInput.disabled = false;
            wordsInput.focus();
        }
    });
});
