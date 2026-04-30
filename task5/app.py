from flask import Flask, request, jsonify

# Vertex AI (Gemini)
import vertexai
from vertexai.preview.generative_models import GenerativeModel

# RAG + tools
from rag.retriever import retrieve_context
from tools.weather_api import get_weather, CITY_COORDS

# Guardrails
from guardrails.prompt_filter import is_prompt_allowed
from guardrails.response_validator import is_response_safe

# Logging
from app_logging.logger import logger


# ------------------------------------------------------------------------------
# Vertex AI Initialization
# ------------------------------------------------------------------------------
vertexai.init(
    project="qwiklabs-gcp-02-5d502ebd5e20",
    location="us-central1",
)

model = GenerativeModel(
    "gemini-2.5-flash",
    system_instruction="""
You are the Alaska Department of Snow (ADS) virtual assistant.

Rules:
- Answer ONLY using the provided context or verified API data
- Do NOT hallucinate or invent information
- Be factual, concise, and helpful
- If information is unavailable, say so clearly
"""
)


# ------------------------------------------------------------------------------
# Core Chatbot Logic
# ------------------------------------------------------------------------------
def ads_chatbot(user_prompt: str) -> str:
    logger.info(f"User prompt: {user_prompt}")

    if not is_prompt_allowed(user_prompt):
        return "Your request cannot be processed due to policy restrictions."

    context = retrieve_context(user_prompt)

    # -------------------------------
    # Weather tool trigger (improved)
    # -------------------------------
    weather_trigger_words = ["weather", "forecast", "temperature", "snow", "storm"]
    weather_used = False

    if any(w in user_prompt.lower() for w in weather_trigger_words):
        for city in CITY_COORDS:
            if city in user_prompt.lower():
                context += f"\n\nWeather Information:\n{get_weather(city)}"
                weather_used = True

    # Graceful fallback if weather asked but no city specified
    if "weather" in user_prompt.lower() and not weather_used:
        return (
            "I can provide current weather information for Anchorage, "
            "Fairbanks, or Juneau. Please specify one of these locations."
        )

    response = model.generate_content(
        f"""
Context:
{context}

User Question:
{user_prompt}
"""
    ).text.strip()

    if not is_response_safe(response):
        return (
            "I’m unable to provide a response to that request, "
            "but I can help with questions about Alaska snow services or weather."
        )

    logger.info(f"Model response: {response}")
    return response


# ------------------------------------------------------------------------------
# Flask App
# ------------------------------------------------------------------------------
app = Flask(__name__)


# ------------------------------------------------------------------------------
# Frontend: Simple Browser Chat UI
# ------------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Alaska Department of Snow Chatbot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 30px; }
        #chat-box {
            border: 1px solid #ccc;
            padding: 10px;
            height: 420px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .user { font-weight: bold; margin-top: 10px; }
        .bot { color: #0033cc; margin-bottom: 10px; }
        input { width: 75%; padding: 8px; }
        button { padding: 8px 14px; }
    </style>
</head>
<body>

<h2>❄️ Alaska Department of Snow Chatbot</h2>
<p>Ask questions about snow services, operations, or Alaska weather.</p>

<div id="chat-box"></div>

<input type="text" id="prompt" placeholder="Type your question…" />
<button onclick="sendMessage()">Send</button>

<script>
function sendMessage() {
    const input = document.getElementById("prompt");
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += "<div class='user'>You:</div><div>" + message + "</div>";
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: message })
    })
    .then(res => res.json())
    .then(data => {
        chatBox.innerHTML += "<div class='bot'>ADS:</div><div>" + data.response + "</div>";
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

document.getElementById("prompt").addEventListener("keydown", function(e) {
    if (e.key === "Enter") sendMessage();
});
</script>

</body>
</html>
"""


# ------------------------------------------------------------------------------
# Backend Chat API
# ------------------------------------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True)
    if not payload or "prompt" not in payload:
        return jsonify({"error": "Missing prompt"}), 400

    response = ads_chatbot(payload["prompt"])
    return jsonify({"response": response})


# ------------------------------------------------------------------------------
# Run Locally
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)