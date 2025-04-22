from typing import Dict, Any
from langgraph.graph import StateGraph, END
from AgentState import AgentState
from nodes import (
    generator, get_weather, get_news, get_db,
    send_emergency_report
)
from edges import await_voice_response, task_selector, check_routine_edge


def run_workflow(input: str, llm: Any, fall_alert: bool = False, agent_components: Dict[str, Any] = None) -> str:
    """
    LangGraph 기반 워크플로우 실행 함수
    """
    # 그래프 초기화
    workflow = StateGraph(AgentState)

    # 노드 추가
    workflow.add_node("task_selector", task_selector)
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("get_news", get_news)
    workflow.add_node("get_db", get_db)
    workflow.add_node("check_routine_edge", check_routine_edge)
    workflow.add_node("generator", generator)
    workflow.add_node("await_voice_response", await_voice_response)
    workflow.add_node("send_emergency_report", send_emergency_report)

    # 시작 지점 설정
    workflow.set_entry_point("task_selector")

    # task_selector 분기
    workflow.add_conditional_edges(
        "task_selector",
        lambda state: state["task_type"],
        {
            "call_weather": "get_weather",
            "call_news": "get_news",
            "call_db": "check_routine_edge",
            "normal": "generator"
        }
    )

    # 각 노드 연결
    workflow.add_edge("get_weather", "generator")
    workflow.add_edge("get_news", "generator")
    workflow.add_edge("get_db", "generator")

    # check_routine_edge 분기 수정
    workflow.add_conditional_edges(
        "check_routine_edge",
        lambda state: "reject" if state.get("check_routine") == "reject" else "call_db",
        {
            "call_db": "get_db",
            "reject": "generator"
        }
    )

    # generator -> 낙상 여부에 따른 분기
    workflow.add_conditional_edges(
        "generator",
        lambda state: "voice_check" if state.get("fall_alert") else "end",
        {
            "voice_check": "await_voice_response",
            "end": END
        }
    )

    # await_voice_response 분기
    workflow.add_conditional_edges(
        "await_voice_response",
        lambda state: state.get("voice_response"),
        {
            "ok": END,
            "report": "send_emergency_report",
            "no_response": "send_emergency_report"
        }
    )

    # 응급신고 노드 연결
    workflow.add_edge("send_emergency_report", END)

    # 앱 컴파일 및 상태 초기화
    app = workflow.compile()
    initial_state: AgentState = {
        "input": input,
        "llm": llm,
        "fall_alert": fall_alert,
        "agent_components": agent_components or {},
        "weather_info": "",
        "news_info": "",
        "db_info": False,
        "check_routine": "",
        "routine_data": None,
        "final_answer": "",
        "routine_alarm": {},
        "voice_input": "",
        "voice_response": ""
    }

    # 워크플로우 실행 및 결과 반환
    result = app.invoke(initial_state)
    return result.get("final_answer", "")
