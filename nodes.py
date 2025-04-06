from AgentState import AgentState

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

def get_weather(state: AgentState) -> str:
    return

def get_news(state: AgentState) -> str:
    return

def get_db(state: AgentState) -> bool:
    return

def check_routine(state: AgentState) -> bool:
    return

def generator(state: AgentState) -> str:
    """수집된 정보를 바탕으로 답변 생성"""
    # Fall Alert가 있는 경우 우선 처리
    if state.fall_alert:
        # TODO: Fall Alert 처리 로직 구현
        pass
    
    # API 결과들을 종합하여 답변 생성
    # TODO: 실제 답변 생성 로직 구현
    state.final_answer = "Generated answer based on collected information"
    return state