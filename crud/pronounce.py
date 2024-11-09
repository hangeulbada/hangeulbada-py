from pecab import PeCab
import crud
import crud.difficulty
pecab = PeCab()

def analysis_pronounce_crud(text):
    dec = crud.difficulty.decomposition(text)
    return {
        "구개음화": analysis_gugaeumhwa(text, dec),
        "비음화": analysis_beumhwa(text, dec),
        "유음화": analysis_yueumhwa(text, dec),
        "연음화": analysis_yeoneumhwa(text, dec)
    }

def analysis_gugaeumhwa(text, dec):

    gugaeumhwa=[]

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if not (r[2]=='ㄷ' or r[2]=='ㅌ'): continue
        print(r)
        if (text[i+1]=='이' or text[i+1]=='히'):
            gugaeumhwa.append(text[i:i+2])

    return gugaeumhwa

def analysis_beumhwa(text, dec):
    beumhwa=[]
    payeoleum = ['ㅂ','ㄷ','ㄱ']
    beeum = ['ㄴ','ㅁ']
    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if  r[2] in payeoleum and dec[i+1][0] in beeum:
            beumhwa.append(text[i:i+2])

    return beumhwa

def analysis_yueumhwa(text, dec):
    yueumhwa=[]

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if r[2]=='ㄹ' and dec[i+1][0]=='ㄴ':
            yueumhwa.append(text[i:i+2])
        elif r[2]=='ㄴ' and dec[i+1][0]=='ㄹ':
            yueumhwa.append(text[i:i+2])

    return yueumhwa

def analysis_yeoneumhwa(text, dec):
    yeoneumhwa=[]
    pos = pecab.pos(text)

    # 모음(ㅇ)으로 시작되는 조사, 어미, 접미사인 경우 연음화
    josa = ['JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC', 'EP', 'EF', 'EC', 'ETN', 'ETM', 'XSN','XSV','XSA']
    for i, (word, tag) in enumerate(pos):
        wdec = crud.difficulty.decomposition(word)
        if wdec[-1][0] != 'ㅇ': continue
        if tag not in josa: continue
        forward = pos[i-1][0]
        fdec = crud.difficulty.decomposition(forward)
        fdec = [col for col in fdec[-1] if col.strip()]
        if len(fdec)!=3: continue
        yeoneumhwa.append(forward+word)
    # 받침 뒤에 ㅏ, ㅓ, ㅗ, ㅜ, ㅟ로 시작하는 실질 형태소가 오는 경우

    return yeoneumhwa