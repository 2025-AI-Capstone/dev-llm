from transformers import AutoTokenizer, TextGeneration
import torch, time

model_name = "beomi/KR-ELECTRA-Small-KoBool"  # 추정 대체 가능한 variant
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = TextGeneration.from_pretrained(model_name)

text = "기분이 좋은 하루였어."
inputs = tokenizer(text, return_tensors="pt")

start = time.time()
with torch.no_grad():
    outputs = model(**inputs)
end = time.time()

print("logits:", outputs.logits)
print("추론 시간:", end - start, "초")
