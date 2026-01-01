import os
import io
import base64
from PIL import Image
from flask import Flask, request, render_template
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"


def image_to_base64(image):
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    return base64.b64encode(img_bytes.getvalue()).decode()


def generate_description(prompt, image):
    img_b64 = image_to_base64(image)

    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [img_b64],
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]


def validate_output(text):
    payload = {
        "model": "llava",
        "prompt": f"Is this medically relevant? Answer Yes or No only:\n{text}",
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"].strip()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["file"]

        if uploaded_file.filename == "":
            return render_template("index.html", response_text="Please upload an image.")

        image = Image.open(uploaded_file)

        prompt = """
        Describe this medical image in detail.
        Identify problems, abnormalities, symptoms, conditions.
        Do not guess.
        """

        description = generate_description(prompt, image)
        valid = validate_output(description)

        if valid.lower() == "yes":
            return render_template("index.html", response_text=description)
        else:
            return render_template("index.html",
                                   response_text="❌ This does not seem like a medical image!")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
