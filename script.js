// HTML escapen
function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Vervang **bold** door <strong>
function replaceBold(text) {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

async function generate() {
  const preset = document.getElementById("preset").value;
  const userInput = document.getElementById("userInput").value;
  const outputDiv = document.getElementById("output");
  const copyBtn = document.getElementById("copyBtn");

  copyBtn.style.display = "none"; // knop verbergen tot output

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
      const safeText = escapeHtml(data.message);
      const formattedText = replaceBold(safeText).replace(/\n/g, "<br>");
      outputDiv.innerHTML = formattedText;

      // Kopieerknop tonen
      copyBtn.style.display = "inline-block";
    } else {
      outputDiv.textContent = `⚠️ Fout bij genereren: ${data.error || 'Onbekende fout'}`;
    }
  } catch (error) {
    console.error("❌ Netwerkfout:", error);
    outputDiv.textContent = `⚠️ Netwerkfout: ${error.message}`;
  }
}

// Kopieer functionaliteit
document.getElementById("copyBtn").addEventListener("click", () => {
  const outputDiv = document.getElementById("output");
  
  // Kopieer de *platte tekst* (zonder HTML tags)
  const textToCopy = outputDiv.textContent;

  navigator.clipboard.writeText(textToCopy).then(() => {
    alert("Tekst gekopieerd naar klembord!");
  }).catch(err => {
    alert("Kopiëren mislukt: " + err);
  });
});
