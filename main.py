from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import re
import json
app = FastAPI()
load_dotenv()

from enum import Enum
class PronounceRule(str, Enum):
    구개음화 = "구개음화"
    연음화 = "연음화"
    경음화 = "경음화"
    유음화 = "유음화"
    비음화 = "비음화"
    음운규칙_없음 = "음운규칙 없음"
    겹받침_쓰기 = "겹받침 쓰기"
    기식음화 = "기식음화"

class ClaudeRequest(BaseModel):
    age: int
    rule: PronounceRule
    count: int

@app.post("/claude")
async def generate_claude(request: ClaudeRequest):
    try:
        import anthropic
        from datetime import datetime

        client_claude = anthropic.Anthropic(
            api_key=os.getenv('CLAUDE_API_KEY'),  # 환경 변수를 설정했다면 생략 가능
        )
        message = client_claude.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            # 다양한 결과값을 얻기 위해 temperature 값 조절
            temperature=0.5,
            system="너는 음운 규칙별 받아쓰기 문제를 생성하는거야. 음운 규칙에는 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화가 있어.\n내가 'n살 난이도로 [m]유형으로 k문제 만들어줘' 라고 하면 맞춰서 받아쓰기 문제를 만들어줘.\nn: 8~13 (초등학교 1학년~6학년)\nm: 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화\nk: 1~15\n답변 형식:\n문제번호:문제 형태로 json형식으로 반환",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{request.age}살 난이도로 [{request.rule}] 유형으로 {request.count}문제 만들어줘. (seed: {datetime.now().isoformat()})"
                        }
                    ]
                }
            ]
        )
        generated_problem = message.content[0].text
        generated_problem = json.loads(generated_problem)
        return generated_problem
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    

# uvicorn main:app --reload
