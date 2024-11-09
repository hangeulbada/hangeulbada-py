from pecab import PeCab
import crud
pecab = PeCab()

def analysis_pronounce_crud(text):
    dec = crud.difficulty.decomposition(text)
    return {
        "구개음화": analysis_gugaeumhwa(text, dec),
        "비음화": analysis_beumhwa(text, dec),
        "유음화": analysis_yueumhwa(text, dec)
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

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if r[2]=='ㄹ' and dec[i+1][0]=='ㄹ':
            yeoneumhwa.append(text[i:i+2])

    return yeoneumhwa