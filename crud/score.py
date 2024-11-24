from crud import pronounce
from pydantic import BaseModel
from typing import List
class ScoreAnalysis(BaseModel):
    question: str
    answer: str
    pronounce: List[str]

class ScoreResponse(BaseModel):
    score: int
    ocr_answer: str
    analysis: List[ScoreAnalysis]# from pydantic import List

def score_crud(score):
    workbook = score.workbook
    answer = score.answer

    """
    ocr request
    답안이 저장된 s3 주소 (string)
    ocr response
    {문제 번호(int): 답안(string), ..., 문제 번호: 답안}
    """
    atext = ocr(answer)

    """
    simillarity request
    workbook
    {문제 번호(int): 문제(string), ..., 문제 번호: 문제}
    answer
    {문제 번호(int): 문제(string), ..., 문제 번호: 문제}
    
    simillarity response
    {문제 번호(int): 점수(int), ..., 문제 번호(int): 점수(int)}

    """
    ascore = simillarity(workbook, answer)

    # {1: [('맏이가', '마지가')], 2: [('굳이', '구지'), ('그렇게까지', '그러케까 지')], 4: [('새로', '세로')]}
    wrong_list = extract_wa(workbook, atext)
    wk = list(workbook)

    response = {}

    for i in range(wk[0], wk[-1]+1):
        sa=[]
        if i not in wrong_list:
            print("!!!!!!", ascore[i], atext[i])
            sr = ScoreResponse(score=ascore[i], ocr_answer=atext[i], analysis=[])
            response[i] = sr
            continue

        for w in wrong_list[i]:
            print(w)
            q = w[0]
            a = w[1]
            saq = q
            saa = a
            sap = analysis_wrong(q, a)

            sa.append(ScoreAnalysis(question=saq, answer=saa, pronounce=sap))
            print(sa)

        sr = ScoreResponse(score=ascore[i], ocr_answer=atext[i], analysis=sa)
        # print(sr)

        response[i] = sr
    
    return response

    """
        1:{
            "score": 70
            "analysis": [
                {
                    "question": "맏이가",
                    "answer": "마지가",
                    "pronounce": ["구개음화", "연음화"]
                },
                {
                    "question": "맏이가",
                    "answer": "마지가",
                    "pronounce": ["구개음화", "연음화"]
                }
            ]
        }
        2:{
            "score": 80
            "analysis": [
                {
                    "question": "맏이가",
                    "answer": "마지가",
                    "pronounce": ["구개음화", "연음화"]
                },
                {
                    "question": "맏이가",
                    "answer": "마지가",
                    "pronounce": ["구개음화", "연음화"]
                }
            ]
        },
        3: {"score": 100, "analysis": []}
    """

def ocr(a):
    return{
        1: "마지가 동생을 돌보았다",
        2: "구지 그러케까지 할 필요는 없어",
        3: "해돋이를 보러 산에 올랐다",
        4: "옷이 낡아서 세로 샀다",
        5: "같이 영화 보러 갈래?",
        6: "밥머고 영화 볼 싸람?"
    }

def simillarity(workbook, a):
    return {1: 90, 2:80, 3:100, 4:80, 5:100, 6:20}
    
def extract_wa(workbook, atext):
    wrong = {}
    wk = list(workbook)
    for i in range(wk[0], wk[-1]+1):
        if i not in atext.keys(): continue
        wlist = workbook[i].split()
        alist = atext[i].split()
        
        for j in range(max(len(wlist), len(alist))):
            if wlist[j]!=alist[j]:
                if i not in wrong: wrong[i]=[]
                wrong[i].append((wlist[j], alist[j]))
    return wrong

def analysis_wrong(q, a):
    analysis = pronounce.pronounce_crud(q)
    plist = []
    for a in analysis:
        if not len(analysis[a]): continue
        plist.append(a)

    if not len(plist): return ['음운규칙 없음']
    return plist

