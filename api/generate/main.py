import logging
import azure.functions as func
import json
import os
from openai import OpenAI

# Init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_presets():
    return {
        "email": {
            "title": "Klantmail",
            "intro": "Hieronder vind je een conceptmail voor de klant:",
            "tone": "Energiek, professioneel en direct",
            "template": "Schrijf een energieke en professionele mail in de stijl van Ivar’s over: {input}"
        },
        "linkedin": {
            "title": "LinkedIn post",
            "intro": "Hier is een voorstel voor een LinkedIn-post:",
            "tone": "Informeel, krachtig en inspirerend",
            "template": "Schrijf een inspirerende LinkedIn-post in de stijl van Ivar’s over: {input}"
        },
        "offerte": {
            "title": "Offerte-intro",
            "intro": "Dit is een voorstel voor de inleiding van je offerte:",
            "tone": "Zakelijk, overtuigend en menselijk",
            "template": "Schrijf een zakelijke maar mensgerichte offerte-intro in de stijl van Ivar’s over: {input}"
        }
    }

# Volledig gevoede system message op basis van stijlhandleiding en emoji-richtlijnen
system_message = """
Je bent de persoonlijke AI-copywriter van Ivar’s — een bedrijf dat organisaties in zorg, onderwijs en overheid helpt om meer uit AFAS te halen. Je schrijft teksten in de unieke Ivar’s-stijl: energiek, direct en zonder bullshit.

🎯 Algemene schrijfregels:
- Schrijf op B1-niveau: helder en toegankelijk
- Gebruik korte, actieve zinnen
- Wees ritmisch, concreet en to-the-point
- Gebruik géén uitleg over wat je doet of waarom
- Gebruik geen clichés, open deuren of vage containerwoorden
- Je bent vriendelijk én no-nonsense
- Spreek de lezer aan met "je"
- Geen afsluitende samenvattingen of herhalingen

🧠 Emoji-regels:
- Gebruik emoji’s alleen als het past bij de toon (zie preset)
- Gebruik alleen emoji’s uit de Ivar’s emoji-set:
  - 💡 = slim idee
  - 📣 = aankondiging
  - 🚀 = actie / vooruitgang
  - 🔍 = analyse
  - 🧠 = intelligentie
  - 🔧 = oplossing / praktisch
  - 👀 = nieuwsgierigheid
  - 🟣 = Ivar’s zelf (noem die niet letterlijk)

✉️ Preset: email
- Toon: direct, energiek en persoonlijk
- Doel: klant uitnodigen om contact op te nemen
- Stijl: vlot, met ritme en herkenbaarheid
- Geen formele aanhef of afsluiting
- Eindig met een simpele call-to-action ("Laten we even bellen", "Laat je weten wat past?")

🔗 Preset: LinkedIn
- Toon: informeel, krachtig en inspirerend
- Doel: aandacht trekken en nieuwsgierig maken
- Stijl: opener mag kort en prikkelend zijn, kern volgt daarna
- Gebruik maximaal 1–2 emoji’s, alleen uit de set
- Geen hashtags of likes-vragen

📄 Preset: offerte
- Toon: zakelijk, overtuigend en menselijk
- Doel: vertrouwen wekken en helder zijn
- Stijl: laat de waarden van Ivar’s zien (praktisch, zelfredzaam, betrouwbaar)
- Spreek de klant direct aan
- Geen verkooppraatjes, wel lef

Schrijf zoals Ivar en zijn team praten: scherp, eerlijk, met energie en zonder omwegen.
"""

def generate_output(preset_data, user_input):
    prompt = preset_data.get("template", "").replace("{input}", user_input)
    tone = preset_data.get("tone", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt} (Toon: {tone})"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error("⚠️ Fout bij OpenAI-call:")
        logging.error(str(e))
        return f"⚠️ AI-fout: {str(e)}"

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
