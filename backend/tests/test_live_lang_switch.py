import httpx
import re
import time

test_cases = [
    ('kn', 'Kannada', r'[\u0C80-\u0CFF]', 'ರೈತರಿಗೆ ಸಾಲ ಯೋಜನೆಗಳು'),
    ('bn', 'Bengali', r'[\u0980-\u09FF]', 'কৃষকদের জন্য ঋণ প্রকল্প'),
    ('mr', 'Marathi', r'[\u0900-\u097F]', 'शेतकऱ्यांसाठी कर्ज योजना'),
    ('ta', 'Tamil',   r'[\u0B80-\u0BFF]', 'விவசாயிகளுக்கான கடன் திட்டங்கள்'),
    ('te', 'Telugu',  r'[\u0C00-\u0C7F]', 'రైతులకు రుణ పథకాలు'),
    ('gu', 'Gujarati', r'[\u0A80-\u0AFF]', 'ખેડૂતો માટે લોન યોજનાઓ'),
    ('hi', 'Hindi',   r'[\u0900-\u097F]', 'किसानों के लिए ऋण योजनाएं'),
    ('en', 'English',  r'[A-Za-z]',        'Loan schemes for farmers')
]

print("=" * 80)
print("TESTING LIVE MULTI-LANGUAGE AGENT SWITCHING")
print("=" * 80)

for code, name, reg, query in test_cases:
    try:
        res = httpx.post('http://localhost:8000/api/agent/query', json={'query': query, 'language': code}, timeout=35.0)
        data = res.json()
        ans = data.get('answer', '')
        has_script = bool(re.search(reg, ans))
        status = '✅ PASS' if has_script and res.status_code == 200 else '❌ FAIL'
        preview = ans.replace('\n', ' ')[:60]
        print(f"[{code}] {name:10} | {status} | HTTP {res.status_code} | {preview}...")
    except Exception as e:
        print(f"[{code}] {name:10} | ❌ ERROR: {e}")
    time.sleep(2.0)
