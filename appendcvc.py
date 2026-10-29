import numpy as np
from scipy.io import wavfile
from VowelSynthesizer import gen_vowel

path = "AppendCV/assets-c/"
filename = {
    'ㅅ': "s.wav",
    'ㅆ': "ss.wav",
    'ㅎ': "h_sound.wav"
}

#각 자음별 (초성일때) 자음->모음 전환되면서 겹치는 시간(초)
overlapsec = {
    'ㅅ': 0.015,
    'ㅆ': 0.015,
    'ㅎ': 0.015
}

def wav2strnp(c): #c는 문자임
    sample_rate, output = wavfile.read(path + filename[c])
    output = np.column_stack((output, output)).flatten().astype(np.int16)
    return output


def crossfade(au1, au2, transSec, sample_rate = 44100): #au1랑 au2는 모두 스테레오 넘파이 배열, transSec은 전환시간(초)
    n_au1 = int(len(au1) / 2)
    n_au2 = int(len(au2) / 2)
    #데시벨 그래프는 일단 모노로 그려서 칼럼으로 필거임.. 그래서 일단 저 위의 n들은 모노일때 기준으로, 그러니까 반 나눠서 샘플 수를 계산했음.

    n_trans = int(sample_rate * transSec) #겹칠 부분 만큼의 샘플 수 정의
    n_whole = n_au1 + n_au2 - n_trans #전체 이어붙인 그 오디오의 샘플 수 정의

    #데시벨 그래프 생성
    fadeout = np.append(np.ones(n_au1 - n_trans), np.linspace(1, 0, n_trans))
    fadein = np.append(np.linspace(0, 1, n_trans), np.ones(n_au2 - n_trans))

    #데시벨 그래프 스테레오화
    fadeout = np.column_stack((fadeout, fadeout)).flatten()
    fadein = np.column_stack((fadein, fadein)).flatten()

    out1 = fadeout * au1
    out1 = out1.astype(np.int16)
    out2 = fadein * au2
    out2 = out2.astype(np.int16)

    #출력물 담을 그릇 만들기
    output = np.zeros(n_whole)
    output = np.column_stack((output, output)).flatten()

    R = np.zeros(len(output) - len(out1), dtype=output.dtype)
    output = output + np.append(out1, R)

    L = np.zeros(len(output) - len(out2), dtype=output.dtype)
    output = output + np.append(L, out2)

    return output.astype(np.int16)




# 그전에!!! append에서 받는 duration은 모음 기준임!!!
def append(c1, v, c2, pitch, duration): #c1과 c2는 문자, v는 오디오 넘파이, pitch는 튜플, duration은 실수
    #종성 붙일까 말까는 일단 나중가서 정해도 될듯...

    C = wav2strnp(c1)
    V = gen_vowel.make_sound(v, pitch, duration)

    output = crossfade(C, V, overlapsec[c1])

    return output






