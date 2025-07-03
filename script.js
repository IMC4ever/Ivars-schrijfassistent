// HTML-tekens escapen (tegen XSS)
function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Vervang **bold** door <strong>bold</strong>
function replaceBold(text) {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

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
      // Veilig HTML escapen, bold vervangen en witregels behouden met <br>
      const safeText = escapeHtml(data.message);
      const formattedText = replaceBold(safeText).replace(/\n/g, "<br>");
      outputDiv.innerHTML = formattedText;
    } else {
      outputDiv.textContent = `⚠️ Fout bij genereren: ${data.error || 'Onbekende fout'}`;
    }
  } catch (error) {
    console.error("❌ Netwerkfout:", error);
    outputDiv.textContent = `⚠️ Netwerkfout: ${error.message}`;
  }
}
