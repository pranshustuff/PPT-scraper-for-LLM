from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
import json
import requests
import os

app = FastAPI(title="PPT Summarizer + LLaMA 3.1 QA API")

HF_API_KEY = os.getenv("HF_API_KEY")
LLAMA_MODEL = "meta-llama/Llama-3-1-GPT-Instruct" 

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

class SummarizerRequest(BaseModel):
    question: str

@app.post("/ask-lecture")
async def ask_lecture(
    json_file: UploadFile = File(...),
    prompt_file: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Receives a JSON of PPT summaries, a prompt.txt, and a question.
    Returns LLaMA 3.1 answer.
    """
    summaries = await json_file.read()
    ppt_data = json.loads(summaries)
  
    combined_summary = ""
    for chunk in ppt_data:
        combined_summary += chunk.get("summary", "") + "\n"
      
    prompt_text = "You are an AI Study Guide. Use the following lecture summaries to teach me about the subject and generate a quiz with 20 questions : [Insert summaries here]"

    input_text = prompt_text.replace("[Insert summaries here]", combined_summary)
    input_text += f"\n\nQuestion: {question}"
  
    payload = {
        "inputs": input_text,
        "parameters": {"max_new_tokens": 300, "temperature": 0.3}
    }
    response = requests.post(
        f"https://api-inference.huggingface.co/models/{LLAMA_MODEL}",
        headers=HEADERS,
        json=payload
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    answer = result[0]["generated_text"] if isinstance(result, list) else result

    return {"answer": answer}
