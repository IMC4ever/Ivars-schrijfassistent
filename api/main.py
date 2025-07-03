import logging
import azure.functions as func
import json
import os

def load_presets():
    path = os.path.join(os.path.dirname(__file__), 'presets.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output(preset_data, user_input):
    template = preset_data.get("template", "Schrijf iets over: {input}")
    tone = preset_data.get("tone", "")
    intro = preset_data.get("intro", "")

    # Als de template een {input} verwacht maar er is geen input meegegeven
    if "{input}" in template and not user_input.strip():
        return "⚠️ Deze preset vereist aanvullende input."

    # Alleen vervangen als de placeholder voorkomt
    if "{input}" in template:
        generated = template.replace("{input}", user_input.strip())
    else:
        generated = template

    return f"{intro}\n\n{generated}\n\n(Toon: {tone})"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ Ivar’s Assistent API aangeroepen")

    try:
        # ✅ Stap 1: Request body uitlezen
        req_body = req.get_json()
        logging.info("📥 Request body ontvangen:")
        logging.info(json.dumps(req_body, indent=2))

        # ✅ Stap 2: preset en input ophalen
        preset = req_body.get("preset", "").lower()
        user_input = req_body.get("input", "")

        logging.info(f"🎛️ Geselecteerde preset: {preset}")
        logging.info(f"✍️ Gebruikersinput: {user_input}")

        # ✅ Stap 3: Presets laden
        presets = load_presets()
        logging.info(f"📁 Beschikbare presets: {list(presets.keys())}")

        if preset not in presets:
            logging.warning(f"⚠️ Preset '{preset}' niet gevonden in presets.json")
            return func.HttpResponse(
                json.dumps({"error": f"Preset '{preset}' niet gevonden."}),
                mimetype="application/json",
                status_code=400
            )

        # ✅ Stap 4: Output genereren
        logging.info("🧩 Gekozen presetconfig:")
        logging.info(json.dumps(presets[preset], indent=2))

        response = generate_output(presets[preset], user_input)

        logging.info("✅ Output succesvol gegenereerd")
        return func.HttpResponse(
            json.dumps({"message": response}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error("💥 Fout in backend:")
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": f"Serverfout: {str(e)}"}),  # <-- toont exacte foutmelding in frontend
            mimetype="application/json",
            status_code=500
        )
        
