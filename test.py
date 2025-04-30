from workflow import run_workflow
from agent_components import initialize_agent_components, load_llm
from dotenv import load_dotenv

load_dotenv()

model_id = "Qwen/Qwen2.5-3B-Instruct"
llm = load_llm(model_id)
agent_components = initialize_agent_components(llm)

result = run_workflow(
    input="날씨",
    llm=llm,
    fall_alert=False,
    agent_components= agent_components
)

print("테스트 결과:", result)
