# Import
import re
import itertools

from .difficulty import decomposition


def levenshtein_distance(str1, str2):
    """ 레벤슈타인 거리 계산 """
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i-1] == str2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
    
    return dp[m][n]


def jamo_similarity(word1, word2):
    """ 한국어 자음 모음 유사도 계산 """
    # 자모 분리
    jamo1 = list(itertools.chain.from_iterable(decomposition(word1)))
    jamo2 = list(itertools.chain.from_iterable(decomposition(word2)))

    # print(jamo1)
    # print(jamo2)
    
    # 자모 유사도와 초성 유사도 계산
    jamo_similarity = 1 - (levenshtein_distance(jamo1, jamo2) / max(len(jamo1), len(jamo2)))
    
    return jamo_similarity