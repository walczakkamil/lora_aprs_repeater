import sqlite3, sys, json, base64, gzip

sys.stdout.reconfigure(encoding='utf-8')

def decode_data(data_str):
    if data_str.startswith('base64'):
        raw = base64.b64decode(data_str[6:])
        return gzip.decompress(raw).decode('utf-8')
    return data_str

conn = sqlite3.connect(r'c:\Users\walcz\PycharmProjects\lora_aprs_reapeter\PCB\repeater.eprj')
c = conn.cursor()

c.execute("SELECT title, dataStr FROM components WHERE title LIKE '%2.54-1*20%' OR title LIKE '%rfm96%'")
for title, dstr in c.fetchall():
    print('=== TITLE:', title)
    decoded = decode_data(dstr)
    lines = [l.strip() for l in decoded.split('\n') if l.strip()]
    for l in lines:
        try:
            arr = json.loads(l)
            if arr[0] in ['PIN', 'ATTR']:
                print(' ', arr[:6])
        except Exception as e:
            pass
