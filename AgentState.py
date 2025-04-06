class AgentState:
    """워크플로우의 상태를 관리하는 클래스"""
    def __init__(self, 
                 input_query: str,
                 llm: Any,
                 fall_alert: bool = False):
        self.input = input_query
        self.llm = llm
        self.weather_info = ""
        self.news_info = ""
        self.db_info = bool
        self.fall_alert = fall_alert
        self.check_routine = bool

        self.final_answer = ""