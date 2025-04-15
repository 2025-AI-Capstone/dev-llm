from AgentState import AgentState

def task_selector(state: AgentState) -> str:

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

def check_routine(state: AgentState) -> str:

    check_routine_chain = state.agent_components["check_routine_chain"]
    if not check_routine_chain:
        raise ValueError("agent_components not found in state")
    response = check_routine_chain.invoke({"user_input": state.input})
    state.check_routine = response.content
    return response.content

def await_voice_response(state: AgentState) -> str:
    """
    낙상 이후 사용자 음성 입력(STT 결과)을 분석하여 신고 여부 판단
    """
    fall_response = state.fall_response.strip()
    check_chain = state.agent_components["check_emergency_chain"]

    # 유효한 음성 입력이 없을 경우
    if not fall_response:
        state.voice_response = "no_response"
        return "no_response"

    # LLM을 통해 신고 여부 판단
    response = check_chain.invoke({"fall_response": fall_response}).content.strip().lower()

    if response in ["report", "ok", "no_response"]:
        state.voice_response = response
        return response
    else:
        # 예상치 못한 응답은 무시하고 no_response 처리
        state.voice_response = "no_response"
        return "no_response"
