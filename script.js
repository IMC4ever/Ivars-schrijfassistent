async function generate() {
  const preset = document.getElementById("preset").value;
  const userInput = document.getElementById("userInput").value;
  const outputDiv = document.getElementById("output");

  outputDiv.innerHTML = "Even bezig met schrijven... ✍️";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ preset, user_input: userInput })
    });

    const data = await response.json();

    if (data.output) {
      outputDiv.innerHTML = `<p>${data.output}</p>`;
    } else {
      outputDiv.innerHTML = `<p style="color: red;">⚠️ Fout bij genereren: ${data.error || 'Onbekende fout'}</p>`;
    }
  } catch (error) {
    outputDiv.innerHTML = `<p style="color: red;">⚠️ Netwerkfout: ${error.message}</p>`;
  }
}
