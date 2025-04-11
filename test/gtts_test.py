from gtts import gTTS

text = '''
1. 라즈베리파이에서 쓰러짐 감지 -> 카메라로 감지 후, 감지된 정보(이미지 JPG compress) 서버로 전송

2. 서버에서 LLM 실행 -> 서버에서 LLM이 '비상연락망으로 연결할까요?"라는 질문 함

3. 결과를 핸드폰 or 데스크탑에 표시

방식 : **웹서버 + api방식** => 라즈베리파이가 감지한 정보를 api에 보내고, 결과를 표시 즉, 서버에서 LLm실행하고 결과를 API형태로 제공함
'''
tts = gTTS(text, lang="ko")
tts.save("hello_ko.mp3")