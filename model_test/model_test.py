import torch
import time
from transformers import AutoTokenizer, AutoModelForCausalLM
import matplotlib.pyplot as plt

models = {
    "KoGPT2 (skt)": "skt/kogpt2-base-v2",
    "KcGPT2 (beomi)": "beomi/KcGPT-2-sentiment-kor",
    "KoreanLM 1.3B": "quantumaikr/koreanlm-1.3b",
    "KoAlpaca-Polyglot 3.6B": "beomi/KoAlpaca-Polyglot-3.6B",        # 알파카 기반 소형 모델
    "KoAlpaca-Polyglot 5.8B": "beomi/KoAlpaca-Polyglot-5.8B",        # GPU 필요
    "KULLM 3B (polyglot)": "nlpai-lab/kullm-polyglot-3b-v2",         # 경량 버전
    "KULLM 5.8B (polyglot)": "nlpai-lab/kullm-polyglot-5.8b-v2",     # 중간급
    "LLaMA 3 Ko 8B (Upstage)": "upstage/llama-3-8b-instruct-ko",    # GPU 강력 추천
    "Snubi/KR-GPT2-Base": "snubi/KR-GPT2-Base",                      # GPT2 기반 한국어 모델
    "KoGPT-Base-Final": "taeminlee/kogpt-base-final"                # GPT2 구조 기반 최종 학습
}


inference_times = {}
prompt = "오늘 하루 어땠어?"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def measure_inference_time(model_name: str, prompt: str, max_new_tokens: int = 30):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    model.eval()

    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    start = time.time()
    with torch.no_grad():
        _ = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.9
        )
    end = time.time()

    del model
    torch.cuda.empty_cache()
    return end - start

for label, model_id in models.items():
    try:
        print(f"Measuring {label}...")
        t = measure_inference_time(model_id, prompt)
        inference_times[label] = t
    except Exception as e:
        inference_times[label] = None
        print(f"Failed to measure {label}: {e}")



labels = list(inference_times.keys())
values = [inference_times[k] if inference_times[k] is not None else 0 for k in labels]

plt.figure(figsize=(10, 5))
plt.barh(labels, values, color='skyblue')
plt.xlabel("Inference Time (seconds)")
plt.title("Inference Time Comparison (Small Korean LLMs)")
plt.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.gca().invert_yaxis()
plt.show()
