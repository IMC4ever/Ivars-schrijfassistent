async function generate() {
  const input = document.getElementById("userInput").value;
  const preset = document.getElementById("preset").value;
  const outputDiv = document.getElementById("output");

  outputDiv.innerHTML = "<p><em>Even wachten... jouw Ivar’s stijl wordt gegenereerd.</em></p>";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ input, preset })
    });

    if (!response.ok) {
      throw new Error("Er ging iets mis bij het ophalen van een antwoord.");
    }

    const data = await response.json();
    outputDiv.innerHTML = `<p>${data.result}</p>`;
  } catch (error) {
    console.error("Fout:", error);
    outputDiv.innerHTML = "<p style='color: red;'>Er ging iets mis. Probeer het later opnieuw.</p>";
  }
}
