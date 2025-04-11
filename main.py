from fastapi import FastAPI, Request
from typing import Dict, Any
import os
import requests
from dotenv import load_dotenv

from langchain.chat_models import ChatOpenAI
from agent_components import initialize_agent_components
from workflow import run_workflow

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")

app = FastAPI()

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
agent_components = initialize_agent_components(llm)

@app.post("/routine/alarm")
async def trigger_routine_alarm(req: Request):
    alert_data: Dict[str, Any] = await req.json()
    print(f"루틴 알림 수신: {alert_data}")

    # LangGraph 실행
    final_answer = run_workflow(
        input_query="루틴 알림 요청입니다.",
        llm=llm,
        fall_alert=False,
        routine_alert_data=alert_data,
        agent_components=agent_components
    )

    return {
        "status": "success",
        "type": "routine_alert",
        "message": final_answer
    }



async def fall_detected():
    print("🚨 낙상 감지 알림 수신됨")

    final_answer = run_workflow(
        input_query="낙상이 감지되었습니다.",
        llm=llm,
        fall_alert=True,
        agent_components=agent_components
    )

    return {
        "status": "success",
        "type": "fall_alert",
        "message": final_answer
    }

@app.post("/user-request")
async def user_request(req: Request):
    data: Dict[str, Any] = await req.json()
    user_input = data.get("input", "")

    print(f"👤 유저 입력 수신: {user_input}")

    final_answer = run_workflow(
        input_query=user_input,
        llm=llm,
        fall_alert=False,
        agent_components=agent_components
    )

    return {
        "status": "success",
        "type": "user_request",
        "message": final_answer
    }
