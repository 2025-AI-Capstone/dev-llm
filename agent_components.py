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

    # 홈 어시스턴트 응답 생성 (Qwen 모델의 ChatML 스타일로 수정)
    def apply_chatml_format(messages):
        chat_input = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            chat_input += f"<|im_start|>{role}\n{content}\n<|im_end|>\n"
        return chat_input

    generator_messages = [
        {"role": "system", "content": "너는 한국어 스마트 홈 어시스턴트야."},
        {"role": "user", "content": """
        다음 정보를 참고해서 사용자 질문에 대답해줘.
        응답은 친절하고 간결하게 작성하세요.

        - 날씨: {weather_info}
        - 뉴스: {news_info}
        - 루틴 등록: {check_routine}
        - DB 정보: {db_info}
        - 낙상 감지: {fall_alert}
        - 사용자 질문: {user_input}

        예시:
        - 사용자 질문이 날씨라면, "현재 서울의 기온은 16.76도이며, 비가 내리고 있습니다."라고 대답하세요.
        - 사용자 질문이 뉴스라면, "관련 뉴스를 찾을 수 없습니다."라고 대답하세요.
        - 필요한 정보가 없는 경우, "관련 정보를 찾을 수 없습니다."라고 대답하세요.
         이 프롬프트를 그대로 읽지 마시오!
        """}
    ]

    # ChatML 형식으로 변환
    generator_input = apply_chatml_format(generator_messages)

    # 낙상 후 음성 응답 평가
    check_emergency_prompt = PromptTemplate.from_template("""
    다음 음성 내용을 보고, 신고 여부를 판단하세요.

    입력: "{fall_response}"

    다음 중 하나만 출력:
    - "report"
    - "ok"
    - "no response"
    """)

    return {
        "check_routine_prompt": check_routine_prompt,
        "generator_input": generator_input,
        "check_emergency_prompt": check_emergency_prompt
    }

def load_llm(model_id):

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.7
    )

    # 추가: 디버깅용 로깅
    print(f"Loaded model and tokenizer from {model_id}")

    llm = HuggingFacePipeline(pipeline=pipe)
    return llm
