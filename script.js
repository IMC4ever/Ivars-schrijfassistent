
async function generate() {
  const input = document.getElementById("userInput").value;
  const preset = document.getElementById("preset").value;
  const output = document.getElementById("output");

  output.innerHTML = "⏳ Genereren...";

  const response = await fetch("https://api.ivars.ai/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ preset, input })
  });

  const data = await response.json();
  output.innerHTML = "<strong>Resultaat:</strong><br>" + data.output;
}
