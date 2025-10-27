from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

if not api_key:
    raise RuntimeError("Nincs API kulcsod! Állítsd be az OPENAI_API_KEY környezeti változót vagy .env fájlt.")

client = OpenAI(api_key=api_key, base_url=base_url)

SYSTEM_PROMPT = (
    "Te egy nagyon okos asszisztens vagy, akinek ha beírok egy szöveget, "
    "átalakítja hivatalos Gmail formátumba a szöveget. "
    "Nem kell semmi plusz szöveg, csak az én beírt szövegemet alakítsd át a formátumba. "
    "Adj vissza KIZÁRÓLAG egy JSON-t ebben a formában: "
    '{ "subject": "Tárgy...", "body": "Törzs...", "signature": "Aláírás..." }'
)

@app.route("/")
def index():
    return render_template("index.html")  

@app.route("/emailFormat", methods=["POST"])
def email_format():
    data = request.get_json(silent=True) or {}
    nyers_szoveg = data.get("rawText", "").strip()

    if not nyers_szoveg:
        return jsonify({"error": "Nem adtál meg szöveget!"}), 400

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": nyers_szoveg}
    ]

    try:
        resp = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=messages,
            temperature=0.0,
            max_tokens=512
        )

        raw_text = resp.choices[0].message.content
        clean_text = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()

        try:
            email_json = json.loads(clean_text)
        except json.JSONDecodeError:
            return jsonify({
                "error": "A modell nem adott érvényes JSON-t.",
                "raw_output": clean_text
            }), 500

        return jsonify(email_json)

    except Exception as e:
        return jsonify({"error": "Model hívás sikertelen", "detail": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
