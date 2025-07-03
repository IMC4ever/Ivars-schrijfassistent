import logging
import azure.functions as func
import json
import os
from openai import OpenAI

# Init OpenAI client met nieuwe SDK v1
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎛️ Preset-configuratie: toon, instructie, structuur per type
def load_presets():
    return {
        "email": {
            "title": "Klantmail",
            "intro": "Hieronder vind je een conceptmail voor de klant:",
            "tone": "Energiek, professioneel en direct",
            "template": "Schrijf een energieke en professionele mail over: {input}",
            "extra_instructie": (
                "Zorg voor een ritmisch begin, heldere zinnen, en eindig met een duidelijke call-to-action. "
                "Gebruik geen jargon. Behandel de lezer als iemand die slim én druk is."
            )
        },
        "linkedin": {
            "title": "LinkedIn post",
            "intro": "Hier is een voorstel voor een LinkedIn-post:",
            "tone": "Informeel, krachtig en inspirerend",
            "template": "Schrijf een inspirerende LinkedIn-post over: {input}",
            "extra_instructie": (
                "Begin krachtig. Gebruik korte alinea’s. Voeg alleen emoji’s toe die zijn goedgekeurd binnen Ivar’s stijl: 💡 📊 🛠️ 🎯. "
                "Sluit af met een uitnodiging tot interactie of doorklik."
            )
        },
        "offerte": {
            "title": "Offerte-intro",
            "intro": "Dit is een voorstel voor de inleiding van je offerte:",
            "tone": "Zakelijk, overtuigend en menselijk",
            "template": "Schrijf een zakelijke maar menselijke offerte-intro over: {input}",
            "extra_instructie": (
                "Gebruik een zelfverzekerde toon, maar blijf menselijk. Verwijs naar resultaat, samenwerking en korte lijnen. "
                "Eén alinea is genoeg — geen inhoudsopgave of bullets."
            )
        }
    }

# 🧠 AI-aansturing op basis van preset + user input
def generate_output(preset_data, user_input):
    prompt = preset_data.get("template", "").replace("{input}", user_input)
    tone = preset_data.get("tone", "")
    extra = preset_data.get("extra_instructie", "")

    system_message = (
        "Je bent een professionele AI-copywriter die werkt namens Ivar’s. "
        "Je schrijft foutloos Nederlands op B1-niveau in een energieke, ritmische, duidelijke stijl. "
        "Je gebruikt korte actieve zinnen, vermijdt clichés, legt niets uit en levert alleen de eindtekst. "
        "Je houdt rekening met de tone-of-voice van Ivar’s zoals bekend uit eerdere opdrachten."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt}\n\n(Toon: {tone})\n{extra}"}
            ],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error("⚠️ Fout bij OpenAI-call:")
        logging.error(str(e))
        return f"⚠️ AI-fout: {str(e)}"

# 🔁 Azure Functions entrypoint
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ Ivar’s Assistent API aangeroepen")

    try:
        req_body = req.get_json()
        preset = req_body.get("preset", "").lower()
        user_input = req_body.get("input", "")

        logging.info(f"🎛️ Geselecteerde preset: {preset}")
        logging.info(f"✍️ Gebruikersinput: {user_input}")

        presets = load_presets()
        if preset not in presets:
            logging.warning(f"⚠️ Preset '{preset}' niet gevonden")
            return func.HttpResponse(
                json.dumps({"error": f"Preset '{preset}' niet gevonden."}),
                mimetype="application/json",
                status_code=400
            )

        output = generate_output(presets[preset], user_input)

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
