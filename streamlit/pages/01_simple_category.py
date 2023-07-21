import streamlit as st
from streamlit_tags import st_tags
from streamlit_space import space
from PIL import Image
import requests


# custom
from attribute import get_simple_category
from utils import (
    add_logo,
    delete_another_session_state,
    make_category_request_json,
    make_audio_data
)
from streamlit_space import space
from constraints import PATH, TAG, SECRET


# 카테고리 선택 방식 Page
COLS = 4
PAGE_TITLE = 'Simple Category / 간단 카테고리 선택'

button_num = 0
st.set_page_config(
    page_title=INFO.PROJECT_NAME,
    page_icon=PATH.ICON_PATH,
    layout="wide"
)

# 결과 페이지에 사용되는 클래스 -> 캡션, 음악파일, 다운로드버튼으로 구성됌
class CategorysimpleContent():
    def __init__(self, caption, file):
        self.caption = caption
        self.music_file = file

    def set_content(self):
        global button_num

        st.markdown("""
        <style>
        .big-font {
            font-size:20px !important; text-align: center;
        }
        button {
            height: auto;
            padding-top: 14px !important;
            padding-bottom: 14px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # 첫번째 라인
        col_0, col_1, col_2 = st.columns([2, 13, 3])
        with col_0:     # 아이콘 부분
            icon = Image.open(PATH.IMAGE_ICON_PATH).resize((60, 60))
            st.image(icon)
        with col_1:     # 음악 재생 부분
            st.audio(self.music_file, format='audio/ogg')
        with col_2:
            music_caption = '_'.join(self.caption)
            st.download_button(
                label=":blue[DOWNLOAD]",    # 버튼 라벨 텍스트
                key=f"button{str(button_num)}",
                data=self.music_file,
                file_name=f"{music_caption}_music.wav"
            )
            button_num += 1     # 버튼은 key값을 지정해야 하기때문에 임의로 Key를 지정
        space(lines=1)      # 컨텐츠 구분을 짓기 위한 개행 처리


# 카테고리 선택 페이지
def simple_category(title, category):
    # default 설정 -> 카테고리의 디폴트값 설정
    if "simple_inputs" not in st.session_state:
        default = {
            TAG.GENRES: [],
            TAG.INSTRUMENTS: [],
            TAG.MOODS: [],
            TAG.ETC: [],
            TAG.DURATION: 1,  # index이므로
            TAG.TEMPO: 1,  # index이므로
        }
    else:
        # 결과페이지에서 돌아온 경우, default값은 선택한 카테고리를 보존
        # duration이 int로 돌아오기 때문에 inb -> index로 변환하는 작업
        duration = st.session_state['simple_inputs'][TAG.DURATION]
        hour, minute = duration//60, duration % 60
        duration = f"{hour}:{minute}"

        for i, s in enumerate(category[TAG.DURATION]):
            if s == duration:
                duration = i
                break

        for i, s in enumerate(category[TAG.TEMPO]):
            if s == st.session_state['simple_inputs'][TAG.TEMPO]:
                tempo = i
                break

        default = {
            TAG.GENRES: st.session_state['simple_inputs'][TAG.GENRES],
            TAG.INSTRUMENTS: st.session_state['simple_inputs'][TAG.INSTRUMENTS],
            TAG.MOODS: st.session_state['simple_inputs'][TAG.MOODS],
            TAG.ETC: st.session_state['simple_inputs'][TAG.ETC],
            TAG.DURATION: duration,  # index이므로
            TAG.TEMPO: tempo,  # index이므로
        }

    st.title(title)
    st.write("---")

    with st.expander("사용법 가이드"):
        st.markdown("""
            ### 😊 "Simple Category"는 간단하게 원하는 정보를 선택하여 배경 음악을 생성하는 방식입니다.
            1. 원하는 `장르`와 `악기`, `분위기`를 선택해 주세요. 여러 개를 선택하셔도 됩니다!!  
            2. 카테고리 외에 추가하고 싶은 키워드가 있다면 `기타(ETC)`에 추가해 주세요  
            3. 마지막으로, 음악의 `재생시간`과 `속도`를 선택하고 Submit 버튼을 눌러주세요!!  

            💢 주의 ) 초기화 버튼을 누르면 선택한 모든 카테고리가 사라집니다!!  
            """)

    # 장르
    st.subheader('🎼 장르 (Genre)')
    cols_list = st.columns([1]*COLS)
    for i, genre in enumerate(category[TAG.GENRES]):
        cols_list[i % COLS].checkbox(
            genre, key=genre+st.session_state['key_num'])
    space(lines=1)

    # 악기
    st.subheader('🥁 악기 (Musical Instruments)')
    cols_list = st.columns([1]*COLS)
    for i, instrument in enumerate(category[TAG.INSTRUMENTS]):
        cols_list[i % COLS].checkbox(
            instrument, key=instrument+st.session_state['key_num'])
    space(lines=1)

    # 분위기
    st.subheader('📣 분위기 (Mood)')
    cols_list = st.columns([1]*COLS)
    for i, mood in enumerate(category[TAG.MOODS]):
        cols_list[i % COLS].checkbox(
            mood, key=mood+st.session_state['key_num'])
    space(lines=1)

    # 사용자 keywords 생성
    etc = st_tags(
        label='### ⚙ 기타 (ETC)',
        text='생성할 음악의 추가정보를 입력해 주세요',
        suggestions=category[TAG.ETC],
        value=default[TAG.ETC],
        key="etc"+st.session_state['key_num'])
    space(lines=1)

    col_1, col_2 = st.columns([1, 1], gap="large")

    col_1.subheader('⌛ 길이(Duration)')
    duration = col_1.selectbox(
        label='생성할 음악의 길이를 선택해 주세요',
        options=category[TAG.DURATION],
        index=default[TAG.DURATION],
        key="duration"+st.session_state['key_num'])

    col_2.subheader('🏇 속도 (Tempo)')
    tempo = col_2.radio(
        label='생성할 음악의 빠르기를 선택해 주세요',
        options=category[TAG.TEMPO],
        index=default[TAG.TEMPO],
        key="tempo"+st.session_state['key_num'])

    button_cols_1, button_cols_2 = st.columns([14, 2])
    if button_cols_1.button('초기화'):  # 결과페이지에서 Return을 누르고 돌아오면 작동하지만, 첫화면에서는 작동 안됨
        if "simple_inputs" in st.session_state:
            del st.session_state['simple_inputs']

        # key값 변경
        if st.session_state['key_num'] == TAG.ONE:
            st.session_state['key_num'] = TAG.TWO
        else:
            st.session_state['key_num'] = TAG.ONE

        st.experimental_rerun()

    if button_cols_2.button("Submit"):  # 제출버튼
        # API로 전송하기 위해 input생성
        inputs = make_simple_request_json(category, st.session_state)

        # 선택한 카테고리를 세션으로 저장해둠 -> 다시 Return으로 돌아갈 경우 default로 사용
        st.session_state['simple_inputs'] = inputs

        # TO DO : 리스트를 모델 서버로 전달 -> 다시 생성된 음악 파일 받고 올림
        st.session_state['simple_state'] = 'submit'
        st.experimental_rerun()


# 제출페이지 누르면 실행 -> disabled=True, button 삭제, post요청 보내고 spinner가 돌아감
def submit_simple_category(title, category):

    # default 설정 -> 카테고리의 디폴트값 설정
    if "simple_inputs" not in st.session_state:
        default = {
            TAG.GENRES: [],
            TAG.INSTRUMENTS: [],
            TAG.MOODS: [],
            TAG.ETC: [],
            TAG.DURATION: 1,  # index이므로
            TAG.TEMPO: 1,  # index이므로
        }
    else:
        # 결과페이지에서 돌아온 경우, default값은 선택한 카테고리를 보존
        # duration이 int로 돌아오기 때문에 inb -> index로 변환하는 작업
        duration = st.session_state['simple_inputs'][TAG.DURATION]
        minute, second = duration//60, duration % 60

        duration = f"{minute}:{second}"
        for i, s in enumerate(category[TAG.DURATION]):
            if s == duration:
                duration = i
                break

        for i, s in enumerate(category[TAG.TEMPO]):
            if s == st.session_state['simple_inputs'][TAG.TEMPO]:
                tempo = i
                break

        default = {
            TAG.GENRES: st.session_state['simple_inputs']['genres'],
            TAG.INSTRUMENTS: st.session_state['simple_inputs']['instruments'],
            TAG.MOODS: st.session_state['simple_inputs']['moods'],
            TAG.ETC: st.session_state['simple_inputs']['etc'],
            TAG.DURATION: duration,  # index이므로
            TAG.TEMPO: tempo,  # index이므로
        }

    st.title(title)
    st.write("---")

    with st.expander("사용법 가이드"):
        st.markdown("""
                    1. `장르`와 `악기`, `분위기`를 선택해 주세요. 여러 개를 선택하셔도 선택하지 않으셔도 됩니다!!  
                    2. 카테고리 외에 추가하고 싶은 키워드가 있다면 `기타(ETC)`에 추가해 주세요  
                    3. 마지막으로, 음악의 `재생시간`과 `속도`를 선택하고 Submit 버튼을 눌러주세요!!  

                    💢 주의 ) 초기화 버튼을 누르면 선택한 모든 카테고리가 사라집니다!!  
                    """)

    # multiselect
    st.subheader('🎼 장르 (Genre)')
    cols_list = st.columns([1]*COLS)
    for i, genre in enumerate(category[TAG.GENRES]):
        cols_list[i % COLS].checkbox(
            genre, disabled=True)
    space(lines=1)

    # 악기
    st.subheader('🥁 악기 (Musical Instruments)')
    cols_list = st.columns([1]*COLS)
    for i, instrument in enumerate(category[TAG.INSTRUMENTS]):
        cols_list[i % COLS].checkbox(
            instrument, disabled=True)
    space(lines=1)

    # 분위기
    st.subheader('📣 분위기 (Mood)')
    cols_list = st.columns([1]*COLS)
    for i, mood in enumerate(category[TAG.MOODS]):
        cols_list[i % COLS].checkbox(
            mood, disabled=True)
    space(lines=1)

    # 사용자 keywords 생성
    st.subheader('⚙ 기타 (ETC)')
    etc = st.multiselect(
        label='생성할 음악의 추가정보를 입력해 주세요',
        options=default[TAG.ETC],
        default=default[TAG.ETC],
        disabled=True)
    space(lines=1)

    col_1, col_2 = st.columns([1, 1], gap="large")

    col_1.subheader('⌛ 길이(Duration)')
    duration = col_1.selectbox(
        label='생성할 음악의 길이를 선택해 주세요',
        options=category[TAG.DURATION],
        index=default[TAG.DURATION],
        disabled=True)

    col_2.subheader('🏇 속도 (Tempo)')
    tempo = col_2.radio(
        label='생성할 음악의 빠르기를 선택해 주세요',
        options=category[TAG.TEMPO],
        index=default[TAG.TEMPO],
        disabled=True)

    with st.spinner('음악을 생성중입니다...'):
        my_json = st.session_state['simple_inputs']
        res = requests.post(SECRET.MUSICGEN_CATEGORY_URL, json=my_json)
        print(">>", PAGE_TITLE, res)      # log로 요청이 제대로 왔는지 확인

        audio_files, caption = make_audio_data(res)
        st.session_state['audiofile'] = {
            'audios': audio_files, 'captions': caption}

    st.session_state['res'] = res
    st.session_state['simple_state'] = 'result'
    st.experimental_rerun()


# 결과 페이지
def result_simple_category(title, inputs):
    caption = [cpt for cpt in inputs['captions']
               [0].split(', ') if cpt]  # 캡션의 정보를 받음
    st.title(title)
    st.divider()

    st.write("### 📃 \t캡션 정보 (Caption)")
    captions = st.multiselect(
        label='',
        options=caption,
        default=caption,
        disabled=True
    )
    space(lines=3)

    # 음악, 다운로드 버튼 생성
    music_contents = [CategorysimpleContent(
        caption, w) for w in inputs['audios']]
    for content in music_contents:
        content.set_content()

    _, button_cols = st.columns([14, 2])

    # 카테고리 선택화면으로 돌아가기
    if button_cols.button("Return"):
        # TO DO : 리스트를 모델 서버로 전달 -> 다시 생성된 음악 파일 받고 올림
        st.session_state['simple_state'] = 'execute'
        st.experimental_rerun()


# main


if __name__ == "__main__":

    # 임시 options
    category = get_simple_category()

    audio_file = open(PATH.TEST_MUSIC_PATH, 'rb').read()

    # state가 없으면 생성
    if 'simple_state' not in st.session_state:
        st.session_state['simple_state'] = 'execute'

    # key값을 변경 -> 값의 초기화하고 새로고침을 만들기 위해 key값을 다르게 설정
    if 'key_num' not in st.session_state:
        st.session_state['key_num'] = TAG.ONE

    # 다른 state 제거
    delete_another_session_state('simple_state')

    # logo설정
    add_logo(PATH.SIDEBAR_IMAGE_PATH, height=250)

    # state가 execute인 경우, 카테고리 선택페이지를 출력
    if st.session_state['simple_state'] == 'execute':
        simple_category(title=PAGE_TITLE, category=category)

    elif st.session_state['simple_state'] == 'submit':
        submit_simple_category(title=PAGE_TITLE, category=category)

    # state가 result인 경우 결과화면을 출력
    else:
        result_simple_category('🎧 Music Generate Result',
                               st.session_state['audiofile'])
