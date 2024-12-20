from crud import pronounce
from crud import ocr, levenshtein
from pydantic import BaseModel
from typing import List
class ScoreAnalysis(BaseModel):
    question: str
    answer: str
    pronounce: List[str]

class ScoreMeta(BaseModel):
    num: int
    simillarity: int
    ocr_answer: str
    analysis: List[ScoreAnalysis]# from pydantic import List

class ScoreResponse(BaseModel):
    answers: List[ScoreMeta]

def score_crud(score):
    workbook = score.workbook
    answer_url = score.answer
    answers = []

    """
    ocr request
    답안이 저장된 s3 주소 (string)
    ocr response
    {문제 번호(int): 답안(string), ..., 문제 번호: 답안}
    """
    atext = ocr.infer_ocr(filepath=answer_url)
    atext = atext['results']

    """
    simillarity request
    workbook
    {문제 번호(int): 문제(string), ..., 문제 번호: 문제}
    answer
    {문제 번호(int): 문제(string), ..., 문제 번호: 문제}
    
    simillarity response
    {문제 번호(int): 점수(int), ..., 문제 번호(int): 점수(int)}

    """
    ascore = simillarity(workbook, atext)

    # {1: [('맏이가', '마지가')], 2: [('굳이', '구지'), ('그렇게까지', '그러케까 지')], 4: [('새로', '세로')]}
    wrong_list = extract_wa(workbook, atext)

    # 틀린게 없는 경우
    if not len(wrong_list): 
        for i in atext.keys():
            sr = ScoreMeta(num=i, simillarity=ascore[i], ocr_answer=atext[i], analysis=[])
        answers.append(sr)

    # 혼합된 경우 완전탐색
    for i in range(list(atext.keys())[0], list(atext.keys())[-1]+1):
        sa=[]
        if i not in wrong_list.keys() and i<=len(ascore) and i<=len(atext):
            sr = ScoreMeta(num=i, simillarity=ascore[i], ocr_answer=atext[i], analysis=[])
            answers.append(sr)
            continue
        # print("www", i, wrong_list[i])
        for w in wrong_list[i]:
            # print(w)
            q = w[0]
            a = w[1]
            saq = q
            saa = a
            sap = analysis_wrong(q, a)

            sa.append(ScoreAnalysis(question=saq, answer=saa, pronounce=sap))
            print(sa)

        sr = ScoreMeta(num=i, simillarity=ascore[i], ocr_answer=atext[i], analysis=sa)
        answers.append(sr)
        
    
    return ScoreResponse(answers=answers)

def simillarity(workbook, answer):
    res = {}
    for i in range(list(workbook.keys())[0],list(workbook.keys())[-1]+1):
        sim = levenshtein.jamo_similarity(workbook[i], answer[i])
        res[i] = int(sim*100)
    return res

# 틀린 부분 찾기
def extract_wa(workbook, atext):
    wrong = {}
    for i in range(list(workbook.keys())[0],list(workbook.keys())[-1]+1):
        wlist = workbook[i].split()
        alist = atext[i].split()
        for j in range(min(len(wlist), len(alist))):
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