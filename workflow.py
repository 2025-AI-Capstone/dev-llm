from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from AgentState import AgentState
from nodes import task_selector, generator, get_weather, get_news, get_db, call_alert
class AgentState:
    """워크플로우의 상태를 관리하는 클래스"""
    def __init__(self, 
                 input_query: str,
                 llm: Any,
                 fall_alert: bool = False):
        self.input = input_query
        self.llm = llm
        self.fall_alert = fall_alert
        self.task_result = None
        self.api_results = {}
        self.final_answer = ""


def run_workflow(input_query: str, llm: Any, fall_alert: bool = False) -> str:
    """워크플로우 실행을 위한 메인 함수"""
    # StateGraph 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("task_selector", task_selector)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("get_news", get_news)
    workflow.add_node("get_news", get_db)
    workflow.add_node("call_alert", call_alert)
    workflow.add_node("generator", generator)
    
    # 엣지 설정
    workflow.set_entry_point("task_selector")
    
    # Task Selector의 결과에 따른 조건부 엣지
    workflow.add_conditional_edges(
        "task_selector",
        lambda x: x,
        {
            "call_tool": "call_tool",
            "please_use_one_word": END
        }
    )
    
    # call_tool에서 generator로 연결
    workflow.add_edge("call_tool", "generator")
    
    # generator에서 종료
    workflow.add_edge("generator", END)
    
    # 워크플로우 컴파일
    app = workflow.compile()
    
    # 초기 상태 설정
    initial_state = AgentState(
        input_query=input_query,
        llm=llm,
        fall_alert=fall_alert
    )
    
    # 워크플로우 실행
    result = app.invoke(initial_state)
    
    return result.final_answer


