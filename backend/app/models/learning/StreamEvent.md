### In research.py
#### Question 1: Event kya hota hai?
Event = System mein kisi kaam ke hone ki notification (signal).

Technical terms mein:
- Ek data structure (dictionary/object) hota hai.
- Usme yeh information hoti hai:
    - Kya hua? (event_type: e.g., "PROGRESS", "RESULT", "ERROR")
    - Kis data ke saath hua? (data: e.g., {"status": "researching", "percent": 40})
    - Kab hua? (timestamp)

Aapke code mein StreamEvent(BaseModel) ek event ka blueprint hai. Jab research ka koi stage complete ho, toh backend yeh object create karta hai aur frontend ko bhejta hai.

#### Question 2: Event Streaming kya hai?
Event Streaming = Ek HTTP connection ko khula (open) rakhna, aur usme time ke saath multiple events bhejte rehna.

Normal REST API (Bina streaming):
- Frontend request bhejta hai -> Backend 10 second ka kaam karta hai -> Phir ek baar mein poora result (JSON) bhejta hai.
- Problem: Frontend ko 10 second tak kuch nahi dikhta, bas loading spinner. User confuse ho jaata hai ki "app hang toh nahi ho gayi?"

Event Streaming (ke saath):
- Frontend request bhejta hai -> Backend connection band nahi karta.
- Backend kaam shuru karta hai:
    - 1 second baad: Event bhejta hai {"event": "ROUTING", "msg": "Route find kar raha hu"}
    - 3 second baad: Event bhejta hai {"event": "RESEARCHING", "msg": "Google search kar raha hu"}
    - 6 second baad: Event bhejta hai {"event": "SUMMARIZING", "msg": "Answer bana raha hu"}
    - 10 second baad: Event bhejta hai {"event": "DONE", "result": "..."} aur connection band karta hai.

Fayda: Frontend har event aate hi screen update kar sakta hai (jaise progress bar, ya live text generation).

