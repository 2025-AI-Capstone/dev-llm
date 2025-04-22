from AgentState import AgentState
from utils.chatml_utils import apply_chatml_format
import json

# ChatML prompt 템플릿 (수정 금지)
CHECK_ROUTINE_PROMPT = """
입력이 루틴 등록 요청이면 아래 형식의 JSON으로 추출하고,
그 외에는 "reject"만 출력하세요.

예시 형식:
{{
"title": "약먹을시간",
"alarm_time": "09:00:00",
"repeat_type": "daily",
"user_id": 1
}}

입력: {user_input}
"""

CHECK_EMERGENCY_PROMPT = """
다음 음성 내용을 보고, 신고 여부를 판단하세요.

입력: "{fall_response}"

다음 중 하나만 출력:
- "report"
- "ok"
- "no response"
"""

def task_selector(state: AgentState) -> AgentState:
    user_input = state['input'].strip().lower()
    if user_input in ["weather", "날씨", "기상", "온도", "기온", "예보"]:
        state['task_type'] = 'call_weather'
    elif user_input in ["news", "뉴스", "기사", "소식", "정보"]:
        state['task_type'] = 'call_news'
    elif user_input in ['저장', "기억해", "일정 추가", "알람 설정", "알람", "일정", "기억"]:
        state['task_type'] = 'call_db'
    else:
        state['task_type'] = 'normal'
    return state


def check_routine_edge(state: AgentState) -> AgentState:
    llm = state['agent_components']['llm']
    user_input = state['input']
    prompt = CHECK_ROUTINE_PROMPT.format(user_input=user_input)
    messages = [{'role': 'user', 'content': prompt}]
    chat_input = apply_chatml_format(messages)
    outputs = llm.pipeline(chat_input)
    raw = outputs[0].get('generated_text', '').strip()
    state['check_routine'] = raw
    try:
        state['routine_data'] = json.loads(raw)
    except json.JSONDecodeError:
        state['routine_data'] = None
    return state


def await_voice_response(state: AgentState) -> AgentState:
    llm = state['agent_components']['llm']
    fall_response = state.get('fall_response', '')
    if not fall_response:
        state['voice_response'] = 'no_response'
        return state
    prompt = CHECK_EMERGENCY_PROMPT.format(fall_response=fall_response)
    messages = [{'role': 'user', 'content': prompt}]
    chat_input = apply_chatml_format(messages)
    outputs = llm.pipeline(chat_input)
    response = outputs[0].get('generated_text', '').strip().lower()
    state['voice_response'] = response if response in ['report', 'ok', 'no response'] else 'no_response'
    return state
