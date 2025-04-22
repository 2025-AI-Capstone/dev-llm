from workflow import run_workflow
from agent_components import initialize_agent_components
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 모델 ID 지정
model_id = "Qwen/Qwen2.5-3B-Instruct"

# 에이전트 컴포넌트 초기화 (LLM 및 백엔드 URL 설정 포함)
agent_components = initialize_agent_components(model_id)
llm = agent_components["llm"]

# 워크플로우 실행 테스트
result = run_workflow(
    input="날씨",
    llm=llm,
    fall_alert=False,
    agent_components=agent_components
)

print("테스트 결과:", result)
