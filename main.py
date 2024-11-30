from fastapi import FastAPI, HTTPException, Body, Query
from pydantic import BaseModel, Field
from typing import Dict
import os
from dotenv import load_dotenv
import json
from crud import difficulty, pronounce, score, ocr

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
    difficulty: int = Field(default=3, ge=1, le=5)
    rule: PronounceRule
    count: int = Field(default=5, ge=1, le=20)

@app.post("/phonological_rules", tags=['analysis'])
async def analysis_pronounce(text: Dict[int, str] = Body(
    example=
            {
                "1": "맏이가 동생을 돌보았다",
                "2": "굳이 그렇게까지 할 필요는 없어",
                "3": "해돋이를 보러 산에 올랐다",
                "4": "옷이 낡아서 새로 샀다",
                "5": "같이 영화 보러 갈래?"
            }

)):
    analysis = {}
    for n, t in text.items():
        if not t:
            raise HTTPException(status_code=400, detail="text에 빈 문자열이 포함되어 있습니다.")
        analysis[n]=pronounce.pronounce_crud(t)
    return analysis

@app.post("/claude", tags=['AI'])
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
            system="""너는 음운 규칙별 받아쓰기 문제를 생성하는거야. 
                    음운 규칙에는 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화가 있어.\n
                    내가 'n 난이도로 [m]유형으로 k문제 만들어줘' 라고 하면 맞춰서 받아쓰기 문제를 만들어줘.\n
                    n: 1~5 (초등학교 기준, 1: 단어, 2: 쉬운 단어가 있는 간단한 문장, 3: 쉬운 단어가 있는 짧은 문장, 4: 짧은 문장, 5: 문장)\n
                    m: 구개음화, 연음화, 경음화, 유음화, 비음화, 음운규칙 없음, 겹받침 쓰기, 기식음화\n
                    답변 형식: 문제번호:문제 형태로 json형식으로 반환""",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"{request.difficulty} 난이도로 [{request.rule}] 유형으로 {request.count}문제 만들어줘. (seed: {datetime.now().isoformat()})"
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
    
class DifficultyRequest(BaseModel):
    text: str = Field("맏이가 동생을 돌보았다")

@app.post('/difficulties', tags=['analysis'], summary='디버깅용')
async def difficulties_endpoint(texts: list[DifficultyRequest]):
    print(texts)
    return [await calc_difficulty(t) for t in texts]

@app.post("/difficulty", tags=['analysis'])
async def calc_difficulty(text: DifficultyRequest):
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

    # pronounce 추출해서 해당하는 부분만 스코어링
    s = text.text
    analysis = pronounce.pronounce_crud(s)

    ab_list, am_list = difficulty_dec(s)
    tsum = sum(b_grade.get(ab) for ab in ab_list) 
    tsum += sum(m_grade.get(am) for am in am_list)

    spro = ''

    for k, v in analysis.items():
        if not v: continue
        spro+=''.join(v)

    b_list, m_list = difficulty_dec(spro)
    if not len(spro): spro='0'

    # 정규화 필요
    b_grade_sum = sum(b_grade.get(b) for b in b_list)
    m_grade_sum = sum(m_grade.get(m) for m in m_list)
    total = (b_grade_sum+m_grade_sum)/((tsum)+len(s))

    difficulty_thresholds = [
        (1, 0.05),   # 20% 이하
        (2, 0.1),   # 40% 이하
        (3, 0.35),   # 60% 이하
        (4, 0.5),   # 80% 이하
        (5, 0.7)    # 100% 이하
    ]
    
    for difficulty, threshold in difficulty_thresholds:
        if total <= threshold:
            if len(s)<=3:
                difficulty-=3
            elif len(s)<=5:
                difficulty-=2
            elif len(s)<=7:
                difficulty-=1
            elif len(s)>=9:
                difficulty+=1
            elif len(s)>=13:
                difficulty+=2
            return max(1, min(5, difficulty))
    return max(1, min(5, difficulty))

class ScoreRequest(BaseModel):
    workbook: dict[int, str] = Field(description="문제집")
    answer: str = Field(description="답안 S3 주소")

@app.post("/score", tags=['analysis'])
async def score_endpoint(s: ScoreRequest = Body(
    example={
        "workbook": {
            "1": "시끌벅적한 소리가",
            "2": "힘차게 밟았다",
            "3": "아까부터 그랬단다"
        },
        "answer": "https://bada-static-bucket.s3.ap-northeast-2.amazonaws.com/117398116290476725816_66b9f0945dd57334d0755ca4.png"
        }
)):
    response = score.score_crud(s)
    
    # return {
    #     "1": 80,
    #     "2": 90,
    #     "3": 47
    # }

    return response


@app.get("/")
async def root():
    return {"message": "한글바다 AI 서버입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# uvicorn main:app --reload

def difficulty_dec(s: str):
    res = difficulty.decomposition(s)
    b_list = []
    m_list = []
    strip_list = [[col for col in row if col.strip()] for row in res]

    for i in strip_list:
        if len(i)==0: continue
        m_list.append(i[1])
        if len(i) == 3:
            b_list.append(i[2])
    return b_list, m_list

@app.get('/ocr', tags=['AI'], summary="디버깅용")
async def ocr_endpoint(filepath: str=Query(default="https://bada-static-bucket.s3.ap-northeast-2.amazonaws.com/117398116290476725816_66b9f0945dd57334d0755ca4.png",description="s3 파일 주소")):
    return ocr.infer_ocr(filepath)


class LevenRequest(BaseModel):
    workbook: dict[int, str] = Field(description="문제집")
    answer: dict[int, str] = Field(description="답안")


@app.post('/levenshtein', tags=['AI'], summary='디버깅용')
async def leven_endpoint(req: LevenRequest = Body(
    example={
        "workbook": {
            1: "시끌벅적한 소리가",
            2: "힘차게 밟았다",
            3: "아까부터 그랬단다"
        },
        "answer":{
            1: "시끌벅적한 소리가",
            2: "차게 밟았다.",
            3: "아까부터 그렀단다."
        }
    }
)):
    return score.simillarity(workbook=req.workbook, answer=req.answer)
