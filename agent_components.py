from langchain.prompts import PromptTemplate, ChatPromptTemplate
import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline
def initialize_agent_components(llm):


    check_routine_prompt = PromptTemplate.from_template("""
    사용자의 입력이 루틴 등록 요청인지 확인하고, 요청이라면 다음 정보를 JSON 형식으로 추출하세요.

    요구 형식:
    {{
    "title": 루틴 제목 (예: "약먹을시간"),
    "alarm_time": 알람 시간 (HH:MM:SS, 24시간 형식),
    "repeat_type": 반복 유형 ("daily", "once", "weekly"),
    "user_id": 1
    }}

    요청이 루틴 등록이 아니라면 "reject"만 출력하세요.

    사용자 입력:
    {user_input}
    """)


    generator_prompt = ChatPromptTemplate.from_messages([
        ("system", "당신은 스마트 홈 어시스턴트입니다. 모든 답변은 한국어로 작성하세요."),
        ("human", """
    다음 정보를 참고하여 사용자에게 적절한 응답을 생성하세요.

    - 날씨 정보: {weather_info}
    - 뉴스 정보: {news_info}
    - 루틴 여부: {check_routine}
    - DB 정보 여부: {db_info}
    - 낙상 감지 여부: {fall_alert}
    - 사용자 질문 : {user_input}

    상황에 맞는 자연스러운 응답을 간결하게 출력하세요. 
    낙상 감지가 True일 경우, 가장 먼저 경고 메시지를 포함하세요.
    """)
    ])
    check_emergency_prompt = PromptTemplate.from_template("""
        당신은 긴급 상황에서 사용자의 요청을 판단하는 AI입니다.

        다음 음성 입력 내용을 보고, 신고가 필요한 상황인지 판단하세요.
        입력이 잡음 또는 비어있어도 신고 상황으로 판단합니다.

        음성 입력:
        "{fall_response}"

        다음 중 하나로만 답하세요:
        - "report": 신고 요청으로 해석됨
        - "ok": 괜찮다는 의사 표시로 해석됨
        - "no response": 입력이 없거나 노이즈만 있을 때
        """)
    check_routine_chain = check_routine_prompt | llm.bind(temperature=0.4)
    generator_chain = generator_prompt | llm.bind(temperature=0.3)
    check_emergency_chain = check_emergency_prompt | llm.bind(temperature=0.2)
    
    return {
        "check_routine_chain":check_routine_chain,
        "generator_chain":generator_chain,
        "check_emergency_chain":check_emergency_chain
    }



def load_llm(model_id):

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=60,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )

    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

