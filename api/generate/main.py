import logging
import azure.functions as func
import json
import os
from openai import OpenAI

# OpenAI client initialiseren met API key uit omgeving
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Bestandslocaties
BASE_DIR = os.path.dirname(__file__)
STYLEBRAIN_PATH = os.path.join(BASE_DIR, "style", "stylebrain.json")
STYLE_DIR = os.path.join(BASE_DIR, "style")

# Algemene stijlregels laden
def load_stylebrain():
    with open(STYLEBRAIN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Stijlbestand per preset laden
def load_preset_style(style_filename):
    path = os.path.join(STYLE_DIR, style_filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Combineren van alle stijlregels in één system prompt
def build_system_message(general, specific):
    message = (
        f"Je bent een professionele AI-copywriter die schrijft namens Ivar’s.\n"
        f"Gebruik altijd deze schrijfstijl:\n"
        f"- Toon: {general['tone_of_voice']}\n"
        f"- Niveau: {general['schrijfstijl']['niveau']}\n"
        f"- Zinnen: {general['schrijfstijl']['zinnen']}\n"
        f"- Vorm: {general['schrijfstijl']['vorm']}\n"
        f"- Humor: {general['schrijfstijl']['humor']}\n"
        f"- Vermijd: {', '.join(general['verboden'])}\n"
        f"- Emoji-regels: {general['emoji']['regels']}\n"
        f"- Toegestane emoji’s: {json.dumps(general['emoji']['voorbeelden'])}\n\n"
        f"Preset-instructies:\n"
        f"- Doel: {specific.get('doel', '')}\n"
    )

    # Structuur (indien aanwezig)
    if 'structure' in specific:
        structuur = specific['structure']
        if isinstance(structuur, list):
            if all(isinstance(b, dict) and 'blok' in b and 'beschrijving' in b for b in structuur):
                structuur_beschrijving = "\n".join(
                    [f"  • {blok['blok']}: {blok['beschrijving']}" for blok in structuur]
                )
                message += f"- Structuur per blok:\n{structuur_beschrijving}\n"
            elif all(isinstance(b, str) for b in structuur):
                structuur_beschrijving = ", ".join(structuur)
                message += f"- Structuur: {structuur_beschrijving}\n"

    # Toon
    if 'tone' in specific:
        message += f"- Toon: {specific['tone']}\n"

    # Voorbeeldoutput
    if example_output := specific.get("example_output"):
        message += f"- Voorbeeldoutput:\n"
        for blok, inhoud in example_output.items():
            message += f"  • {blok}: {inhoud}\n"

    # Stijlvoorbeeld (indien aanwezig)
    if voorbeeld := specific.get("stijlvoorbeeld"):
        message += f"- Stijlvoorbeeld: {voorbeeld}\n"

    return message

# Output genereren
def generate_output(system_msg, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error("⚠️ Fout bij OpenAI-call:")
        logging.error(str(e))
        return f"⚠️ AI-fout: {str(e)}"

# Azure Functions endpoint
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ Ivar’s Assistent API aangeroepen")

    try:
        req_body = req.get_json()
        preset_key = req_body.get("preset", "").lower()
        user_input = req_body.get("input", "").strip()

        if not preset_key or not user_input:
            return func.HttpResponse(
                json.dumps({"error": "Preset of input ontbreekt."}),
                mimetype="application/json",
                status_code=400
            )

        stylebrain = load_stylebrain()
        general_style = stylebrain.get("algemeen", {})
        preset_meta = stylebrain.get("presets", {}).get(preset_key)

        if not preset_meta:
            return func.HttpResponse(
                json.dumps({"error": f"Preset '{preset_key}' niet gevonden in stylebrain."}),
                mimetype="application/json",
                status_code=400
            )

        # Laad het juiste stylebestand
        stylefile = preset_meta.get("stylefile")
        if not stylefile:
            return func.HttpResponse(
                json.dumps({"error": f"Stylefile niet gespecificeerd voor preset '{preset_key}'."}),
                mimetype="application/json",
                status_code=500
            )

        preset_style = load_preset_style(stylefile)
        system_message = build_system_message(general_style, preset_style)

        # Prompt opbouwen
        if "template" in preset_style:
            prompt = preset_style["template"].replace("{input}", user_input)
        else:
            prompt = f"Schrijf in Ivar’s-stijl een {preset_key}-tekst over: {user_input}"

        output = generate_output(system_message, prompt)

        return func.HttpResponse(
            json.dumps({"message": output}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error("💥 Fout in backend:")
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": f"Serverfout: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )
