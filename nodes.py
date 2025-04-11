from AgentState import AgentState
from dotenv import load_dotenv
import requests
import json
import os
import urllib

def get_weather(state:AgentState) -> AgentState:
    
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
        weather_info = {
            "city": city,
            "temp": temp,
            "weather": weather_main
        }
        state.weather_info = str(weather_info)
        return weather_info

    except requests.RequestException as e:
        return json.dumps({"error": f"날씨 API 요청 중 오류 발생: {e}"}, ensure_ascii=False)
    except KeyError as e:
        return json.dumps({"error": f"응답 데이터 파싱 오류: {e}"}, ensure_ascii=False)
    

def get_news(state: AgentState) -> AgentState:
    load_dotenv()
    # API 키 가져오기
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    print("enter the naver engine")

    agent_response = state.get('agent_response', '')

    encText = urllib.parse.quote(agent_response)

    url = 'https://openapi.naver.com/v1/search/news?query='+ encText
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-id",client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        search_response = response_body.decode('utf-8')
        state.news_info = search_response
        return search_response



def get_db(state: AgentState) -> bool:
    """
    check_routine에서 전달한 루틴 정보를 받아 백엔드에 POST 요청을 보낸다.
    성공 시 True, 실패 시 False 반환
    """
    backend_url = "http://localhost:8080/routines"
    
    # check_routine에서 전달한 루틴 정보 가져오기
    routine_payload = getattr(state, "routine_data", None)
    
    if not routine_payload:
        print("No routine data found in state.")
        state.db_info = False
        return False

    try:
        response = requests.post(backend_url, json=routine_payload, timeout=3)
        response.raise_for_status()
        print(f"Routine 등록 성공: {response.status_code}")
        state.db_info = True
        return True
    except requests.exceptions.RequestException as e:
        print(f"Routine 등록 실패: {e}")
        state.db_info = False
        return False


def generator(state: AgentState) -> str:
    # Fall Alert가 있는 경우 우선 처리
    if state.fall_alert:
        # TODO: Fall Alert 처리 로직 구현
        pass
    
    # API 결과들을 종합하여 답변 생성
    # TODO: 실제 답변 생성 로직 구현
    state.final_answer = "Generated answer based on collected information"
    return state