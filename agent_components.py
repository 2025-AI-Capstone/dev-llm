from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from utils.chatml_utils import apply_chatml_format


def initialize_agent_components(model_id: str, backend_url: str = "http://localhost:8080"):
    """
    LLMPipeline과 필요한 설정만 반환합니다.
    - apply_chatml_format 방식을 유지합니다.

    Args:
        model_id: HuggingFace 모델 식별자
        backend_url: 백엔드 알람/리포트 엔드포인트 기본 URL

    Returns:
        Dict[str, Any]:
            {
                "llm": HuggingFacePipeline,
                "backend_url": str
            }
    """
    # 모델 로드
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
    llm = HuggingFacePipeline(pipeline=pipe)

    # 환경변수는 최상단에서 load_dotenv()로 로드했다고 가정
    return {
        "llm": llm,
        "backend_url": backend_url
    }