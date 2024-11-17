from pecab import PeCab
import crud
import crud.difficulty
pecab = PeCab()

# 음절의 끝소리 규칙

def pronounce_crud(text):
    dec = crud.difficulty.decomposition(text)
    return {
        "구개음화": analysis_gugaeumhwa(text, dec),
        "비음화": analysis_beumhwa(text, dec),
        "유음화": analysis_yueumhwa(text, dec),
        "연음화": analysis_yeoneumhwa(text, dec),
        "경음화": anaylsis_gyeonumhwa(text, dec),
        "겹받침 쓰기": doubleb_analysis(text, dec),
        "거센소리": geosensori_analysis(text, dec)
    }

def analysis_gugaeumhwa(text, dec):

    gugaeumhwa=[]

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue
        if not (r[2]=='ㄷ' or r[2]=='ㅌ'): continue
        if (text[i+1]=='이' or text[i+1]=='히'):
            gugaeumhwa.append(text[i:i+2])

    return gugaeumhwa

def analysis_beumhwa(text, dec):
    beumhwa=[]
    payeoleum = ['ㅂ','ㄷ','ㄱ', 'ㅍ','ㄼ','ㅄ','ㅅ','ㅆ','ㅈ','ㅊ','ㅎ','ㄲ','ㅋ','ㄺ']
    payeoleum = ['ㅂ','ㄷ','ㄱ', 'ㅍ','ㄼ','ㅄ','ㅅ','ㅆ','ㅈ','ㅊ','ㅎ','ㄲ','ㅋ','ㄺ']
    beeum = ['ㄴ','ㅁ']
    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue

        if  r[2] in payeoleum and dec[i+1][0] in beeum:
            beumhwa.append(text[i:i+2])

    return beumhwa

def analysis_yueumhwa(text, dec):
    yueumhwa=[]

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue

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
        if fdec[2]=='ㅇ': continue
        yeoneumhwa.append(forward[-1]+word[0])
    # 받침 뒤에 ㅏ, ㅓ, ㅗ, ㅜ, ㅟ로 시작하는 실질 형태소가 오는 경우

    return yeoneumhwa

def anaylsis_gyeonumhwa(text, dec):
    gyeongumhwa = []
    pos = pecab.pos(text)

    # 받침 뒤
    b1list = ['ㄱ','ㄷ','ㅂ', 'ㄲ','ㅋ','ㄳ','ㄺ','ㅅ','ㅆ','ㅈ','ㅊ','ㅌ','ㅍ','ㄼ','ㄿ','ㅄ']
    b2list = ['ㄼ', 'ㄾ']
    
    n1list = ['ㄱ','ㄷ','ㅂ','ㅅ','ㅈ']
    n2list = ['ㄱ','ㄷ','ㅅ','ㅈ']
    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue

        # 받침 ㄱ,ㄷ,ㅂ 뒤 ㄱㄷㅂㅅㅈ
        if r[2] in b1list and dec[i+1][0] in n1list:
            gyeongumhwa.append(text[i:i+2])
        # 어간 받침 ㄼ, ㄾ  뒤 ㄱ, ㄷ, ㅅ, ㅈ
        if r[2] in b2list and dec[i+1][0] in n2list:
            gyeongumhwa.append(text[i:i+2])

    # 용언의 어간 받침 ㄴ, ㅁ 뒤 ㄱ, ㄷ, ㅅ, ㅈ
    # VV(동사)[2]
    for i, (word, tag) in enumerate(pos):
        if tag == 'VV':
            wdec = crud.difficulty.decomposition(word)
            if wdec[-1][2] not in ['ㄴ','ㅁ']: continue
            sdec = crud.difficulty.decomposition(pos[i+1][0])
            if sdec[-1][0] not in n2list: continue
            gyeongumhwa.append(word+pos[i+1][0])
    

    # 관형사형 어미 -(으)ㄹ 뒤 ㄱ, ㄷ, ㅂ, ㅅ, ㅈ
    # ETM
    for i, (word, tag) in enumerate(pos):
        if 'ETM' in tag:
            wdec = crud.difficulty.decomposition(word)
            if wdec[-1][0]!='ㅇ' or wdec[-1][2] != 'ㄹ': continue
            sdec = crud.difficulty.decomposition(pos[i+1][0])

            if sdec[0][0] not in n1list: continue
            gyeongumhwa.append(word+pos[i+1][0])

    # 한자어 ㄹ 받침 뒤 ㄷ, ㅅ, ㅈ
    return gyeongumhwa

def doubleb_analysis(text, dec):
    # 겹받침

    doubleb = []
    doubleblist = ['ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ']
    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue

        # 받침 ㄱ,ㄷ,ㅂ 뒤 ㄱㄷㅂㅅㅈ
        if r[2] in doubleblist:
            doubleb.append(text[i])

    return doubleb

def geosensori_analysis(text, dec):
    geosensori=[]
    geosensorilist = ['ㅎ','ㄶ','ㅀ']
    trigger = ['ㄱ', 'ㄷ', 'ㅂ', 'ㅈ', 'ㄵ', 'ㄺ', 'ㄼ']

    for i, r in enumerate(dec):
        r = [col for col in r if col.strip()]
        if len(r)!=3: continue
        if i+1>=len(dec): continue

        # 받침 ㄱ,ㄷ,ㅂ 뒤 ㄱㄷㅂㅅㅈ
        if r[2] in geosensorilist and dec[i+1][0] in trigger:
            geosensori.append(text[i:i+2])
        if r[2] in trigger and dec[i+1][0] in geosensorilist:
            geosensori.append(text[i:i+2])

    return geosensori