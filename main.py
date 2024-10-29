from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
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
    age: int = Field(default=11)
    rule: PronounceRule
    count: int = Field(default=5)

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

@app.post("/difficulty")
async def calc_difficulty(s: str):
    b_grade={
        'ㄱ':2, 'ㄴ':2, 'ㄹ':2, 'ㅁ':2, 'ㅇ':2,
        'ㄷ':3, 'ㅂ':3, 'ㅅ':3, 'ㅈ':3,  'ㅎ':3, 'ㅆ':3,
        'ㅊ':4, 'ㅋ':4, 'ㅌ':4, 'ㅍ':4, 'ㄲ':4,
        'ㄵ':5, 'ㄶ':5, 
        'ㄺ':6, 'ㄻ':6, 'ㄼ':6, 'ㅀ':6, 'ㅄ':6,
        'ㄳ':7, 'ㄽ':7, 'ㄾ':7, 'ㄿ':7, 
    }
    m_grade={
        'ㅏ':1,  'ㅓ':1, 'ㅗ':1, 'ㅜ':1, 'ㅡ':1, 'ㅣ':1,
        'ㅐ':2, 'ㅔ':2,
        'ㅑ':3, 'ㅕ':3, 'ㅛ':3, 
        'ㅚ':4, 'ㅟ':4,
        'ㅘ':5, 'ㅝ':5, 'ㅢ':5,
        'ㅖ':6, 'ㅙ':6, 'ㅞ':6,
        'ㅒ':7, 'ㅠ':7,
    }

    b_list, m_list = decomposition(s)
    print(b_list, m_list)
    b_grade_sum = sum(b_grade.get(b) for b in b_list)
    m_grade_sum = sum(m_grade.get(m) for m in m_list)
    return b_grade_sum + m_grade_sum


@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# uvicorn main:app --reload

def decomposition(korean_word: str):
    # 초성 리스트. 00 ~ 18
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    # 중성 리스트. 00 ~ 20
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    # 종성 리스트. 00 ~ 27 + 1(1개 없음)
    JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    r_lst = []
    for w in list(korean_word.strip()):
        ## 영어인 경우 구분해서 작성함. 
        if '가'<=w<='힣':
            ## 588개 마다 초성이 바뀜. 
            ch1 = (ord(w) - ord('가'))//588
            ## 중성은 총 28가지 종류
            ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
            r_lst.append([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
        else:
            r_lst.append([w])
    print (r_lst)
    b_list = []
    m_list = []
    strip_list = [[col for col in row if col.strip()] for row in r_lst]

    for i in strip_list:
        m_list.append(i[1])
        if len(i) == 3:
            b_list.append(i[2])
    
    return b_list, m_list