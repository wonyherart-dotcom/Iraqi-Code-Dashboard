import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
import google.generativeai as genai

# 환경변수 로드
NAVER_ID = os.environ.get("0Hna0veoqRLZ3xiu19lm")
NAVER_SECRET = os.environ.get("XHURNB2C9T")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# 1. 네이버 뉴스 검색 (이라크 건설, 안전 등)
query = urllib.parse.quote("이라크 건설 안전")
url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=3&sort=date"

req = urllib.request.Request(url)
req.add_header("0Hna0veoqRLZ3xiu19lm", NAVER_ID)
req.add_header("XHURNB2C9T", NAVER_SECRET)

response = urllib.request.urlopen(req)
news_items = json.loads(response.read().decode('utf-8')).get('items', [])

# 2. Gemini AI 요약 및 데이터 가공
processed_news = []
for item in news_items:
    clean_title = item['title'].replace('**', '').replace('**', '').replace('"', '"')
    clean_desc = item['description'].replace('**', '').replace('**', '').replace('"', '"')
    
    prompt = f"다음 뉴스 내용을 1~2문장의 전문적인 건설/안전 브리핑 문체로 요약해줘: {clean_desc}"
    try:
        summary = model.generate_content(prompt).text.strip()
    except Exception:
        summary = clean_desc

    processed_news.append({
        "title": clean_title,
        "date": datetime.now().strftime("%Y. %m. %d."),
        "summary": summary,
        "link": item['originallink'] or item['link']
    })

# 3. data/news.json 파일로 저장
os.makedirs("data", exist_ok=True)
output_data = {
    "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "articles": processed_news
}

with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print("뉴스 데이터 갱신 완료")
