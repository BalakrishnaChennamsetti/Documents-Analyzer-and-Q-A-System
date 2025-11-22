# backend/web_search.py
import os
import requests

SERPER_KEY = os.environ.get("SERPER_API_KEY")

def web_search(query: str, num: int = 5):
    if not SERPER_KEY:
        return {"error": "SERPER_API_KEY not configured"}
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json()
            out = []
            for item in data.get("organic", []):
                title = item.get("title")
                snippet = item.get("snippet")
                link = item.get("link")
                out.append({"title": title, "snippet": snippet, "link": link})
            return out
        else:
            return {"error": f"serper_error_{r.status_code}", "text": r.text}
    except Exception as e:
        return {"error": "exception", "message": str(e)}
