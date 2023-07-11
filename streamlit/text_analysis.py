import json
import requests
import streamlit as st
from streamlit_tags import st_tags


# 문서 분석 방식


def text_analysis(title):

    st.title(title)
    st.write("---")

    with st.expander("# Custom"):

        # multiselect
        st.write('### 장르 (Genre)')
        options_0 = st.multiselect(
            label='🎼 배경음악의 장르를 정해주세요.',
            options=['Green', 'Yellow', 'Red', 'Blue'],
            default=[])

        st.write('### 악기 (Musical Instruments)')
        options_1 = st.multiselect(
            label='🥁 배경음악의 악기를 정해주세요.',
            options=['Green', 'Yellow', 'Red', 'Blue'],
            default=[])

        st.write('### 분위기 (Mood)')
        options_2 = st.multiselect(
            label='📣 배경음악의 분위기를 정해주세요.',
            options=['Green', 'Yellow', 'Red', 'Blue'],
            default=[])

        # 사용자 keywords 생성
        options_3 = st_tags(
            label='### 그 외 (ETC)',
            text='그 외에 추가하고 싶은 곡 정보를 입력해주세요.',
            value=['Blue'],
            suggestions=['Green', 'Yellow', 'Red', 'Blue'],
            key="etc_choice")
    
    # text area
    text = st.text_area('분석을 진행하고 싶은 텍스트를 입력하세요 👉')
    
    if st.button("SUBMIT"):
        # TO DO : 리스트를 모델 서버로 전달 -> 다시 생성된 음악 파일 받고 올림
        inputs = {
            "genre": options_0,
            "instrument": options_1,
            "mood": options_2,
            "etc": options_3,
            "text": text
        }
        st.write(inputs)
        requests.post(url = "http://127.0.0.1:8000/text_analysis", data = json.dumps(inputs))
