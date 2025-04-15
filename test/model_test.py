import torch
import time
import gc
from transformers import AutoTokenizer, AutoModelForCausalLM
import matplotlib.pyplot as plt

models = {
    "KoGPT2 (skt)": "skt/kogpt2-base-v2",
    "KULLM 3B (polyglot)": "nlpai-lab/kullm-polyglot-3b-v2",
    "KULLM 5.8B (polyglot)": "nlpai-lab/kullm-polyglot-5.8b-v2",
    "LLaMA 3 Ko 8B (Upstage)": "upstage/llama-3-8b-instruct-ko",
    "Snubi/KR-GPT2-Base": "snubi/KR-GPT2-Base",
    "KoGPT-Base-Final": "taeminlee/kogpt-base-final"
}

# CUDA 사용 여부 확인
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"현재 사용 중인 GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU 개수: {torch.cuda.device_count()}")
    print(f"초기 GPU 메모리 사용량: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
    print(f"초기 GPU 메모리 캐시: {torch.cuda.memory_reserved(0) / 1024**2:.2f} MB")
else:
    print("CUDA를 사용할 수 없습니다. CPU를 사용합니다.")

inference_times = {}
prompt = "오늘 하루 어땠어?"

def measure_inference_time(model_name: str, prompt: str, max_new_tokens: int = 30):
    print(f"\n테스트 시작: {model_name}")
    
    # 테스트 전 메모리 상태 확인
    if torch.cuda.is_available():
        print(f"테스트 전 GPU 메모리: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        model.eval()

        # 모델 로딩 후 메모리 상태
        if torch.cuda.is_available():
            print(f"모델 로딩 후 GPU 메모리: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")

        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.9
            )
        end = time.time()
        
        # 생성된 텍스트 출력 (디버깅 목적)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"생성된 텍스트: {generated_text}")
        
        inference_time = end - start
        print(f"추론 시간: {inference_time:.4f}초")
        
        # 메모리 정리
        del model
        del tokenizer
        del inputs
        del outputs
        gc.collect()
        torch.cuda.empty_cache()
        
        # 메모리 정리 후 상태 확인
        if torch.cuda.is_available():
            print(f"메모리 정리 후 GPU 메모리: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        
        return inference_time
    
    except Exception as e:
        print(f"오류 발생: {e}")
        # 오류 발생 시에도 메모리 정리
        gc.collect()
        torch.cuda.empty_cache()
        if torch.cuda.is_available():
            print(f"오류 후 메모리 정리 완료: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        return None

# 모델 하나씩 순차적으로 테스트
for label, model_id in models.items():
    print(f"\n===== {label} 테스트 중... =====")
    inference_time = measure_inference_time(model_id, prompt)
    inference_times[label] = inference_time
    print(f"===== {label} 테스트 완료 =====")
    
    # 각 모델 테스트 사이에 추가 정리 및 잠시 대기
    gc.collect()
    torch.cuda.empty_cache()
    time.sleep(2)  # 2초 대기로 시스템 안정화

# 결과 시각화
successful_models = {k: v for k, v in inference_times.items() if v is not None}
labels = list(successful_models.keys())
values = list(successful_models.values())

if labels:
    plt.figure(figsize=(12, 6))
    bars = plt.barh(labels, values, color='skyblue')
    plt.xlabel("추론 시간 (초)")
    plt.title("한국어 LLM 추론 시간 비교")
    plt.grid(True, axis='x', linestyle='--', alpha=0.6)
    
    # 막대 위에 시간 표시
    for bar, value in zip(bars, values):
        plt.text(value + 0.1, bar.get_y() + bar.get_height()/2, f'{value:.2f}s', 
                 va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.gca().invert_yaxis()
    plt.show()
    
    # 결과 요약 출력
    print("\n===== 추론 시간 결과 요약 =====")
    for label, time_value in sorted(successful_models.items(), key=lambda x: x[1]):
        print(f"{label}: {time_value:.4f}초")
else:
    print("성공적으로 테스트된 모델이 없습니다.")