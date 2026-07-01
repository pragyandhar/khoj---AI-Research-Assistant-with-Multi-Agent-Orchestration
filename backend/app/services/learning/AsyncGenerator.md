### research_service.py
#### Question: What is AsyncGenerator[StreamEvents, None]?
Ye ek special type ka function hai jo:
- Ek saath answer nahi deta (jaise return karta hai).
- Time ke saath (thoda-thoda karke) multiple answers deta hai.
- Aur har answer dene ke beech mein intzaar (await) kar sakta hai (DB/API/LLM ka).

Syntax: async def + yield (andar await ho sakta hai).

#### Type Hints ka matlab [StreamEvents, None]
Pehla angle bracket (StreamEvent): Ye batata hai ki yeh generator bahar kya bhejega (yield karega). Matlab har baar ek StreamEvent object aayega (jaise {"status": "ROUTING"}).

Doosra angle bracket (None): Ye batata hai ki agar koi andar (.asend() se) kuch bhejta hai toh uska type kya hoga. Humare case mein koi andar kuch nahi bhej raha, isliye None hai. (Ignore karo, mostly None hi aata hai streaming APIs mein).

#### Question: Is project mein exactly kya ho raha hai? (Step-by-step flow)
Jab user query bhejta hai, toh backend yeh function call karta hai. Function turant return nahi karta, balki ek pipeline khol deta hai:
- Pehla Yield: "ROUTING" event bhejo (User ko frontend pe dikhega "Topic classify ho raha hai").
    - Yahan function rukta nahi, aage badhta hai.
- Await: Router Agent chal raha hai (2 second lage). Jab aayega, doosra Yield: "RESEARCHING" event bhejo.
- Await: Research Agent Tavily search kar raha (5 second). Teesra Yield: "SUMMARIZING" event bhejo.
- Await: Summary Agent report bana raha (10 second). Chautha Yield: Pura StructuredReport (JSON) bhejo.
- Function khatam (StopIteration).

#### Question: Bina iske kya hota? (Importance samjho)
Agar hum normal function (async def process() jo sirf return report karta) banate:
- User request aayi.
- Backend ne Router → Research → Summary sab kuch ek saath khatam kiya (17 second).
- 17 second tak HTTP connection open thi, lekin client ko kuch nahi bheja.
- Frontend par blank screen dikhti rahi.
- User bore hua, page refresh kiya (ya chhod diya). Production mein user drop-off.

Async Generator ke saath:
- 1 second pe "Topic mil gaya" dikha.
- 3 second pe "Internet search ho rahi" dikha.
- 10 second pe "Report ready" dikha.
- User engaged raha, pata bhi nahi chala ki 17 second lag rahe hain. Production mein user happy.