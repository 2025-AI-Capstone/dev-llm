import os
import requests
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# .env에서 API 키 불러오기
api_key = os.getenv("OPENWEATHER_API_KEY")

if not api_key:
    print("❌ OPENWEATHER_API_KEY가 .env에 설정되어 있지 않습니다.")
    exit()

# 서울 날씨 조회 URL 구성
url = (
    "https://api.openweathermap.org/data/2.5/weather"
    "?q=Seoul,KR"
    f"&appid={api_key}"
    "&units=metric"  # 섭씨 온도
)

print("🔍 서울 날씨 정보를 불러오는 중...\n")

try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    data = response.json()

    # 최소 정보만 추출
    city = data.get("name", "Unknown")
    temp = data.get("main", {}).get("temp", "N/A")
    weather = data.get("weather", [{}])[0].get("main", "")

    result = {
        "city": city,
        "temp": temp,
        "weather": weather
    }

    print("✅ 결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

except requests.RequestException as e:
    print(f"❌ 날씨 API 요청 중 오류 발생: {e}")
except KeyError as e:
    print(f"❌ 응답 파싱 오류: {e}")
