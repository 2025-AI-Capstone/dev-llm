from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from AgentState import AgentState
from nodes import agent, generator, db_save
from edges import which_retrieved, grade_documents, should_continue

class WorkflowState:
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

def task_selector(state: WorkflowState) -> str:
    """사용자 입력을 분석하여 적절한 작업을 선택"""
    # One word Please 조건 체크
    if len(state.input.split()) > 1:
        return "please_use_one_word"
    
    # 입력에 따른 작업 선택 로직
    # TODO: 실제 task 선택 로직 구현
    return "call_tool"

def call_tool(state: WorkflowState) -> Dict:
    """선택된 작업에 따라 적절한 도구 호출"""
    results = {}
    
    # Naver News API 호출
    try:
        # TODO: Naver News API 구현
        results['naver_news'] = []
    except Exception as e:
        results['naver_news_error'] = str(e)
    
    # Weather API 호출
    try:
        # TODO: Weather API 구현
        results['weather'] = {}
    except Exception as e:
        results['weather_error'] = str(e)
    
    # DB 조회
    try:
        # TODO: DB 조회 구현
        results['db'] = {}
    except Exception as e:
        results['db_error'] = str(e)
    
    state.api_results = results
    return state

def generator(state: WorkflowState) -> str:
    """수집된 정보를 바탕으로 답변 생성"""
    # Fall Alert가 있는 경우 우선 처리
    if state.fall_alert:
        # TODO: Fall Alert 처리 로직 구현
        pass
    
    # API 결과들을 종합하여 답변 생성
    # TODO: 실제 답변 생성 로직 구현
    state.final_answer = "Generated answer based on collected information"
    return state

def run_workflow(input_query: str, llm: Any, fall_alert: bool = False) -> str:
    """워크플로우 실행을 위한 메인 함수"""
    # StateGraph 초기화
    workflow = StateGraph(WorkflowState)
    
    # 노드 추가
    workflow.add_node("task_selector", task_selector)
    workflow.add_node("call_tool", call_tool)
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
    initial_state = WorkflowState(
        input_query=input_query,
        llm=llm,
        fall_alert=fall_alert
    )
    
    # 워크플로우 실행
    result = app.invoke(initial_state)
    
    return result.final_answer

def extract_final_response(result: WorkflowState) -> str:
    """최종 응답 추출"""
    return result.final_answer

