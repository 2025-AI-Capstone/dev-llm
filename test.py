from workflow import run_workflow
from agent_components import initialize_agent_components
from dotenv import load_dotenv
import os
from langchain.chat_models import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
agent_components = initialize_agent_components(llm)

result = run_workflow(
    input="매일 오후 2시에 운동하는 일정 추가해줘",
    llm=llm,
    fall_alert=False,
    agent_components= agent_components
)

print("테스트 결과:", result)
