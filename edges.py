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