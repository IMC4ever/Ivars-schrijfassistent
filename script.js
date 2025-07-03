async function generate() {
  const preset = document.getElementById("preset").value;
  const userInput = document.getElementById("userInput").value;
  const outputDiv = document.getElementById("output");

  // Statusmelding met HTML, mag iconen bevatten
  outputDiv.innerHTML = "Even bezig met schrijven... ✍️";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ preset, input: userInput })
    });

    const data = await response.json();
    console.log("🔍 Backend response:", data);

    if (response.ok && data.message) {
      // Output veilig als platte tekst met behoud van witregels
      outputDiv.textContent = data.message;
    } else {
      // Foutmelding als platte tekst tonen
      outputDiv.textContent = `⚠️ Fout bij genereren: ${data.error || 'Onbekende fout'}`;
    }
  } catch (error) {
    console.error("❌ Netwerkfout:", error);
    outputDiv.textContent = `⚠️ Netwerkfout: ${error.message}`;
  }
}
