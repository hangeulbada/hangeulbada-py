from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

class PhonologicalRule(BaseModel):
    rule: str

@app.post("/gpt")
async def generate_dictation(rule: PhonologicalRule):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Write a haiku about recursion in programming."
                }
            ]
        )
        generated_problem = response.choices[0].message.strip()
        return {"problem": generated_problem}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# uvicorn main:app --reload