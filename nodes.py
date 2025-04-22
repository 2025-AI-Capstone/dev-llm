from AgentState import AgentState
from utils.chatml_utils import apply_chatml_format
import os
import requests
import json
import urllib

# URL 및 프롬프트 상수
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?q=Seoul,KR&units=metric&appid="
NEWS_URL = "https://openapi.naver.com/v1/search/news?query="
GENERATOR_TEMPLATE = """
너는 한국어 스마트 홈 어시스턴트야.
다음 정보를 참고해서 사용자 질문에 대답해줘. 응답은 친절하고 간결하게 작성하세요.
- 날씨: {weather_info}
- 뉴스: {news_info}
- 루틴 등록: {check_routine}
- DB 정보: {db_info}
- 낙상 감지: {fall_alert}
- 사용자 질문: {user_input}
예시:
- 사용자 질문이 날씨라면, "현재 서울의 기온은 16.76도이며, 비가 내리고 있습니다."라고 대답하세요.
- 사용자 질문이 뉴스라면, "관련 뉴스를 찾을 수 없습니다."라고 대답하세요.
- 필요한 정보가 없는 경우, "관련 정보를 찾을 수 없습니다."라고 대답하세요.
이 프롬프트를 그대로 읽지 마시오!
"""


def get_weather(state: AgentState) -> AgentState:
    api_key = os.getenv("WEATHER_API_KEY", "")
    if not api_key:
        state["weather_info"] = ""
        return state
    try:
        response = requests.get(WEATHER_URL + api_key, timeout=5)
        response.raise_for_status()
        data = response.json()
        city = data.get("name", "")
        temp = data.get("main", {}).get("temp", "")
        weather = (data.get("weather") or [{}])[0].get("main", "")
        state["weather_info"] = str({"city": city, "temp": temp, "weather": weather})
    except requests.RequestException as e:
        state["weather_info"] = f"날씨 API 오류: {e}"
    return state


def get_news(state: AgentState) -> AgentState:
    client_id = os.getenv("CLIENT_ID", "")
    client_secret = os.getenv("CLIENT_SECRET", "")
    query = urllib.parse.quote(state.get("input", ""))
    try:
        req = urllib.request.Request(NEWS_URL + query)
        req.add_header("X-Naver-Client-Id", client_id)
        req.add_header("X-Naver-Client-Secret", client_secret)
        resp = urllib.request.urlopen(req, timeout=5)
        body = resp.read().decode("utf-8")
        state["news_info"] = body
    except Exception:
        state["news_info"] = ""
    return state


def get_db(state: AgentState) -> AgentState:
    payload = state.get("routine_data")
    backend = state["agent_components"].get("backend_url", "")
    if not payload:
        state["db_info"] = False
        return state
    try:
        resp = requests.post(f"{backend}/routines", json=payload, timeout=3)
        resp.raise_for_status()
        state["db_info"] = True
    except requests.RequestException:
        state["db_info"] = False
    return state


def generator(state: AgentState) -> AgentState:
    if state.get("fall_alert"):
        state["final_answer"] = "낙상이 감지되었습니다. 즉시 확인이 필요합니다. 괜찮으신가요?"
        return state
    llm = state["agent_components"]["llm"]
    prompt = GENERATOR_TEMPLATE.format(
        weather_info=state.get("weather_info", ""),
        news_info=state.get("news_info", ""),
        check_routine=str(state.get("check_routine", "")),
        db_info=str(state.get("db_info", False)),
        fall_alert=str(state.get("fall_alert", False)),
        user_input=state.get("input", "")
    )
    messages = [{"role": "user", "content": prompt}]
    chat_input = apply_chatml_format(messages)
    outputs = llm.pipeline(chat_input)
    state["final_answer"] = outputs[0].get("generated_text", "").strip()
    return state


def send_emergency_report(state: AgentState) -> AgentState:
    report = {
        "user_id": state["agent_components"].get("user_id", 1),
        "event": "fall_detected",
        "status": state.get("voice_response", ""),
        "timestamp": "",
        "details": "자동 신고"
    }
    backend = state["agent_components"].get("backend_url", "")
    try:
        requests.post(f"{backend}/emergency/report", json=report, timeout=3)
        state["final_answer"] = "응급 신고가 전송되었습니다."
    except Exception as e:
        state["final_answer"] = f"신고 오류: {e}"
    return state
