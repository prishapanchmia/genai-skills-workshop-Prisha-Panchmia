import sys
import os
import datetime
import pandas as pd
import vertexai
from vertexai.preview.evaluation import EvalTask

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import ads_chatbot

# Initialize Vertex AI experiment
vertexai.init(
    project="qwiklabs-gcp-02-5d502ebd5e20",
    location="us-central1",
    experiment="ads-evaluation"
)

questions = [
    "What services does the Alaska Department of Snow provide?",
    "What happens during heavy snowstorms?"
]

# Generate system responses
predictions = [ads_chatbot(q) for q in questions]

# ✅ Include 'prompt' column (REQUIRED for groundedness)
data = pd.DataFrame({
    "prompt": questions,
    "instruction": questions,
    "response": predictions
})

task = EvalTask(
    dataset=data,
    metrics=["groundedness"]
)

run_name = f"ads-eval-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

result = task.evaluate(
    experiment_run_name=run_name
)

print("✅ Evaluation complete")
print(result.summary_metrics)