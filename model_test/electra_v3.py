from transformers import AutoTokenizer, TextGeneration
import torch, time

model_name = "monologg/koelectra-small-v3-discriminator"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = TextGeneration.from_pretrained(model_name)

text = "오늘 날씨 어때?"
inputs = tokenizer(text, return_tensors="pt")

start = time.time()
with torch.no_grad():
    outputs = model(**inputs)
end = time.time()

print("🔹 logits:", outputs.logits)
print("⏱️ 추론 시간:", end - start, "초")
