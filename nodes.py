from AgentState import AgentState
from dotenv import load_dotenv
import requests
import json
import os

def task_selector(state: AgentState) -> str:
    """
    사용자 입력을 분석하여 어떤 작업을 수행할지(날씨 API, 뉴스 API, DB 작업 등) 결정하는 함수.
    필요에 따라 분기를 늘려갈 수 있다.
    """
    user_input = state.input.strip().lower()
    
    # (특정 키워드(날씨, 뉴스, DB 등)를 기준으로 라우팅
    #  실제로는 여기에 NLP 파싱, 정규식, 의도 분류 모델 등을 적용 가능
    if user_input in ["weather", "날씨", "기상", "온도", "기온", "예보"]:
        return "call_weather"
    elif user_input in ["news", "뉴스", "기사", "소식", "정보"]:
        return "call_news"
    elif user_input in ['저장', "기억해", "일정 추가", "알람 설정", "알림 설정", "알림", "일정", "기억"]:
        return "call_db"
    
    return "normal"

def get_weather(api_key: str) -> str:
    
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key :
        return json.dumps({"error": "OPENWEATHER_API_KEY가 설정되지 않았습니다."}, ensure_ascii=False)
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        "?q=Seoul,KR"
        f"&appid={api_key}"
        "&units=metric"  # 섭씨 온도를 위해 units=metric 사용
    )
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # 필요한 정보만 추출
        city = data.get("name", "Unknown")
        main_data = data.get("main", {})
        weather_arr = data.get("weather", [])
        
        # (weather 배열의 0번째에 대한 예외 처리)
        if weather_arr:
            weather_main = weather_arr[0].get("main", "")
        else:
            weather_main = ""

        temp = main_data.get("temp", "N/A")

        # 간단 정보만 담아서 JSON 문자열로
        minimal_info = {
            "city": city,
            "temp": temp,
            "weather": weather_main
        }
        return json.dumps(minimal_info, ensure_ascii=False)

    except requests.RequestException as e:
        return json.dumps({"error": f"날씨 API 요청 중 오류 발생: {e}"}, ensure_ascii=False)
    except KeyError as e:
        return json.dumps({"error": f"응답 데이터 파싱 오류: {e}"}, ensure_ascii=False)

def get_news(state: AgentState) -> str:
    return

def get_db(state: AgentState) -> bool:
    return

def check_routine(state: AgentState) -> bool:
    return

def generator(state: AgentState) -> str:
    # Fall Alert가 있는 경우 우선 처리
    if state.fall_alert:
        # TODO: Fall Alert 처리 로직 구현
        pass
    
    # API 결과들을 종합하여 답변 생성
    # TODO: 실제 답변 생성 로직 구현
    state.final_answer = "Generated answer based on collected information"
    return state