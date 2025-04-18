from langchain_core.language_models.fake import FakeListLLM
from workflow import run_workflow
from agent_components import initialize_agent_components

# 테스트용 Mock LLM (항상 동일한 응답 반환)
mock_llm = FakeListLLM(responses=[
    "voice_check",  # generator → await_voice_response
    "report",       # await_voice_response → send_emergency_report
    "응급 신고가 전송되었습니다."  # final response
])

agent_components = initialize_agent_components(mock_llm)

result = run_workflow(
    input="낙상이 감지되었습니다.",
    llm=mock_llm,
    fall_alert=False,
    agent_components= agent_components
)

print("🧪 테스트 결과:", result)
