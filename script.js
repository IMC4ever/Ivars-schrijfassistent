async function generate() {
  const preset = document.getElementById("preset").value;
  const userInput = document.getElementById("userInput").value;
  const outputDiv = document.getElementById("output");

  outputDiv.innerHTML = "⏳ Genereren...";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        preset: preset,
        input: userInput
      })
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    outputDiv.innerHTML = `<pre>${data.output || JSON.stringify(data)}</pre>`;
  } catch (err) {
    outputDiv.innerHTML = `❌ Fout: ${err.message}`;
  }
}
