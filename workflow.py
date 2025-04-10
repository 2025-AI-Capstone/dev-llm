from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from AgentState import AgentState
from nodes import task_selector, generator, get_weather, get_news, get_db, check_routine

def run_workflow(input_query: str, llm: Any, fall_alert: bool = False) -> str:
    """워크플로우 실행을 위한 메인 함수"""
    # StateGraph 초기화
    workflow = StateGraph(AgentState)
    
    # 노드 추가
    workflow.add_node("task_selector", task_selector)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("get_news", get_news)
    workflow.add_node("get_db", get_db)
    workflow.add_node("check_routine", check_routine)
    workflow.add_node("generator", generator)
    
    # 엣지 설정
    workflow.set_entry_point("task_selector")
    
    # Task Selector의 결과에 따른 조건부 엣지
    workflow.add_conditional_edges(
        "task_selector",
        lambda x: x,
        {
            "call_weather": "get_weather",
            "call_news": "get_weather",
            "call_db": "check_routine",
            "normal": "generator"
        }
    )
    
    workflow.add_edge("get_weather", "generator")
    workflow.add_edge("get_news", "generator")
    workflow.add_edge("check_routine", "generator")
    workflow.add_edge("get_db", "generator")

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

