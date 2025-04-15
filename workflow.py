from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from AgentState import AgentState
from nodes import generator, get_weather, get_news, get_db
from edges import task_selector, check_routine

def run_workflow(input_query, llm, fall_alert = False, agent_components) -> str:
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
    workflow.add_node("await_voice_response", await_voice_response)
    workflow.add_node("send_emergency_report", send_emergency_report)
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
    workflow.add_conditional_edges(
        "check_routine",
        lambda x: x,
        {
            "call_db", "get_db",
            "reject", "generator"
        }
    )
    #  이후 분기: 낙상이면 → await_voice_response, 아니면 종료
    workflow.add_conditional_edges(
        "generator",
        lambda state: "voice_check" if state.fall_alert else "end",
        {
            "voice_check": "await_voice_response",
            "end": END
        }
    )

    # STT 결과 기반 분기
    workflow.add_conditional_edges(
        "await_voice_response",
        voice_response_condition,  # returns: "ok", "report", "no_response"
        {
            "ok": END,
            "report": "send_emergency_report",
            "no_response": "send_emergency_report"
        }
    )

    workflow.add_edge("send_emergency_report", END)
    
    # 워크플로우 컴파일
    app = workflow.compile()
    
    # 초기 상태 설정
    initial_state = AgentState(
        input_query=input_query,
        llm=llm,
        fall_alert=fall_alert,
        agent_componenets = agent_components
    )
    
    # 워크플로우 실행
    result = app.invoke(initial_state)
    
    return result.final_answer

