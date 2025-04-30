from langchain.prompts import PromptTemplate, ChatPromptTemplate
import datetime
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline

def initialize_agent_components(llm):

    # 루틴 등록 여부 확인
    check_routine_prompt = PromptTemplate.from_template("""
    입력이 루틴 등록 요청이면 아래 형식의 JSON으로 추출하고,
    그 외에는 "reject"만 출력하세요.

    예시 형식:
    {{
    "title": "약먹을시간",
    "alarm_time": "09:00:00",
    "repeat_type": "daily",
    "user_id": 1
    }}

    입력: {user_input}
    """)

    # 홈 어시스턴트 응답 생성
    generator_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    당신은 한국어 스마트 홈 어시스턴트입니다. 다음 규칙을 엄격히 따르세요:
    1. 제공된 정보 중 값이 있는 항목만 언급하세요
    2. 값이 비어있거나 없는 항목은 절대 언급하지 마세요
    3. 응답은 정보 전달에만 집중하고 불필요한 설명이나 추가 문구를 포함하지 마세요
    4. 정보를 사실적으로만 전달하고 추가적인 제안이나 질문을 하지 마세요
    """),
    ("human", "{user_input}"),
    ("system", """
    현재 정보:
    날씨: {weather_info}
    뉴스: {news_info}
    루틴: {check_routine}
    DB: {db_info}
    낙상알림: {fall_alert}
    
    위 정보 중 값이 있는 항목만 사용해 응답하세요. 
    정보를 있는 그대로만 전달하고, 추가 질문이나 제안, 인사말, 마무리 문구를 붙이지 마세요.
    응답은 필요한 정보만 포함하고 다른 내용은 제외하세요.
    """)
])

    # 낙상 후 음성 응답 평가
    check_emergency_prompt = PromptTemplate.from_template("""
    다음 음성 내용을 보고, 신고 여부를 판단하세요.

    입력: "{fall_response}"

    다음 중 하나만 출력:
    - "report"
    - "ok"
    - "no response"
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
        temperature=0.7,
        return_full_text=False
    )

    llm = HuggingFacePipeline(pipeline=pipe)
    return llm

