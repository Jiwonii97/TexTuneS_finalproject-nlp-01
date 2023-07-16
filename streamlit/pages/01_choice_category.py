import os
import numpy as np
import streamlit as st
from streamlit_tags import st_tags
from streamlit_space import space
from PIL import Image


# custom
from utils import add_logo, delete_another_session_state, get_music_category
from streamlit_space import space
from constraints import PATH, TAG

# 카테고리 선택 방식 Page
button_num = 0

# 결과 페이지에 사용되는 클래스 -> 캡션, 음악파일, 다운로드버튼으로 구성됌


class CategoryChoiceContent():
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


def choice_category(title, categoty):

    # default 설정 -> 카테고리의 디폴트값 설정
    if "choice_inputs" not in st.session_state:
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
        duration = st.session_state['choice_inputs']['duration']
        duration = str(int(duration/60))+':'+str(duration % 60)
        if len(duration) == 3:
            duration += '0'  # 3:0 인경우가 있음
        for i, s in enumerate(categoty['duration']):
            if s == duration:
                duration = i
                break

        for i, s in enumerate(categoty['tempo']):
            if s == st.session_state['choice_inputs']['tempo']:
                tempo = i
                break

        default = {
            "genre": st.session_state['choice_inputs']['genre'],
            "instruments": st.session_state['choice_inputs']['instruments'],
            "mood": st.session_state['choice_inputs']['mood'],
            "etc": st.session_state['choice_inputs']['etc'],
            "duration": duration,  # index이므로
            "tempo": tempo,  # index이므로
        }

    st.title(title)
    st.write("---")

    with st.expander("사용법 가이드"):
        st.write("1. 장르와 악기, 분위기를 선택해 주세요. 여러개를 선택하셔도, 선택하지 않으셔도 됩니다!!")
        st.write("2. 카테고리 외에 추가하고 싶은 키워드가 있다면 '기타(ETC)'에 추가해 주세요")
        st.write("3. 마지막으로, 음악의 재생시간과 속도를 선택하고 Submit 버튼을 눌러주세요!!")
        space(lines=1)
        st.write("※ 주의 ) 초기화 버튼을 누르면 선택한 모든 카테고리가 사라집니다")

    # multiselect
    st.subheader('🎼 장르 (Genre)')
    genre = st.multiselect(
        label='생성할 음악의 장르를 선택해 주세요.',
        options=categoty[TAG.GENRES],
        default=default[TAG.GENRES])
    space(lines=1)

    st.subheader('🥁 악기 (Musical Instruments)')
    instruments = st.multiselect(
        label='생성할 음악의 악기를 선택해 주세요.',
        options=categoty[TAG.INSTRUMENTS],
        default=default[TAG.INSTRUMENTS])
    space(lines=1)

    st.subheader('📣 분위기 (Mood)')
    mood = st.multiselect(
        label='생성할 음악의 분위기를 선택해 주세요.',
        options=categoty[TAG.MOODS],
        default=default[TAG.MOODS])
    space(lines=1)

    # 사용자 keywords 생성
    etc = st_tags(
        label='### ⚙ 기타 (ETC)',
        text='생성할 음악의 추가정보를 입력해 주세요',
        suggestions=categoty[TAG.ETC],
        value=default[TAG.ETC])
    space(lines=1)

    col_1, col_2 = st.columns([1, 1], gap="large")

    col_1.subheader('⌛ 길이(Duration)')
    duration = col_1.selectbox(
        label='생성할 음악의 길이를 선택해 주세요',
        options=categoty[TAG.DURATION],
        index=default[TAG.DURATION])

    col_2.subheader('🏇 속도 (Tempo)')
    tempo = col_2.radio(
        label='생성할 음악의 빠르기를 선택해 주세요',
        options=categoty[TAG.TEMPO],
        index=default[TAG.TEMPO])

    button_cols_1, button_cols_2 = st.columns([14, 2])
    if button_cols_1.button('초기화'):  # 결과페이지에서 Return을 누르고 돌아오면 작동하지만, 첫화면에서는 작동 안됨
        if "choice_inputs" in st.session_state:
            del st.session_state['choice_inputs']
        st.experimental_rerun()

    if button_cols_2.button("Submit"):  # 제출버튼

        # duration 파싱 -> str to int로 바꿔서 API서버로 전송
        min, sec = map(int, duration.split(':'))
        duration = min*60 + sec

        # API로 전송하기 위해 input생성
        inputs = {
            "genre": genre,
            "instruments": instruments,
            "mood": mood,
            "etc": etc,
            "duration": duration,
            "tempo": tempo,
        }

        # 선택한 카테고리를 세션으로 저장해둠 -> 다시 Return으로 돌아갈 경우 default로 사용
        st.session_state['choice_inputs'] = inputs

        # TO DO : 리스트를 모델 서버로 전달 -> 다시 생성된 음악 파일 받고 올림
        # res = requests.post(url = "http://127.0.0.1:8000/choice_category", data = json.dumps(inputs))

        # session_state 변경 -> result 페이지로 이동
        st.session_state['choice_state'] = 'result'
        st.experimental_rerun()


# 임시 examp생성
def create_exam_audio():
    sample_rate = 44100  # 44100 samples per second
    seconds = 2  # Note duration of 2 seconds

    frequency_la = 440  # Our played note will be 440 Hz

    # Generate array with seconds*sample_rate steps, ranging between 0 and seconds
    t = np.linspace(0, seconds, seconds * sample_rate, False)

    # Generate a 440 Hz sine wave
    note_la = np.sin(frequency_la * t * 2 * np.pi)
    return note_la


# 임시 examp 생성
def create_exam_binary():
    binary_contents = b'example content'
    return binary_contents


# 결과 페이지
def result_choice_category(title, inputs):
    caption = inputs['captions']  # 캡션의 정보를 받음
    st.title(title)
    st.write("---")

    st.write("### 📃 \t캡션 정보 (Caption)")
    captions = st.multiselect(
        label='',
        options=inputs['captions'],
        default=inputs['captions'],
        disabled=True
    )
    space(lines=3)

    # 음악, 다운로드 버튼 생성
    music_contents = [CategoryChoiceContent(caption, w) for w in inputs['wav']]
    for content in music_contents:
        content.set_content()

    _, button_cols = st.columns([14, 2])

    # 카테고리 선택화면으로 돌아가기
    if button_cols.button("Return"):
        # TO DO : 리스트를 모델 서버로 전달 -> 다시 생성된 음악 파일 받고 올림
        st.session_state['choice_state'] = 'execute'
        st.experimental_rerun()


# main


if __name__ == "__main__":

    # 임시 options
    categoty = get_music_category()

    audio_file = open(PATH.TEST_MUSIC_PATH, 'rb').read()

    # state가 없으면 생성
    if 'choice_state' not in st.session_state:
        st.session_state['choice_state'] = 'execute'

    # 다른 state 제거
    delete_another_session_state('choice_state')

    # logo설정
    add_logo(PATH.SIDEBAR_IMAGE_PATH, height=250)

    # state가 execute인 경우, 카테고리 선택페이지를 출력
    if st.session_state['choice_state'] == 'execute':
        choice_category(title='카테고리 선택', options=categoty)

    # state가 result인 경우 결과화면을 출력
    else:
        # 임시 input 생성
        inputs = {
            'captions': PATH.TEST_CAPTION,
            'wav': [audio_file, audio_file, audio_file, audio_file]
        }

        result_choice_category('🎧 Music Generate Result', inputs)
