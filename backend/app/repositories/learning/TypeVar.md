### backend/app/repositories/base.py
#### What is TypeVar('T') and why is it used?
T = TypeVar("T")

Yeh ham ek generic type variable bana rhe hai. Iss project ke according ham isse ya to Session declare kar sakte hai ya to Report aur yeh phir uss particular declaration ke attributes ko hi allow karega use karne ke liye.

Ham isse code me as a SQLAlchemy Model use kar rhe hai. 

Production benefits of using this?
1) Compile-time Type Safety: IDE ko pata hai ki T exact kaunsa model hai. Agar aapne session_id ki jagah report_id likha toh VS Code red underline dikha dega deploy karne se pehle.
2) Zero-Code Duplication: CRUD operations (Create, Read, Update, Delete) sirf ek baar Base mein likho. Har naye table ke liye alag se get_by_id nahi likhna padta.
3) Refactoring Safety: Maan lo get_by_id ka return type badalna hai (e.g., T | None se T karna hai). Sirf BaseRepository mein ek jagah badlo. Saari 20 repositories automatically update ho jaati hain.

Advanced/In-depth topic:
Dhyan do: T = TypeVar("T") mein koi bound nahi diya. Matlab yeh kuch bhi ho sakta hai (string, int, Session, Report).

Lekin humne isko sirf SQLAlchemy models ke saath use karna hai. Isliye hum TypeVar("T", bound=Base) bhi kar sakte the (jahan Base hamara SQLAlchemy DeclarativeBase hai).
Lekin hamare code mein nahi kiya kyunki humne __init__(self, model: type[T]) likha hai. Agar koi galat type daalega (jaise int), toh type checker error dikhayega ki int ek valid SQLAlchemy model nahi hai.

Yeh Dependency Injection ke saath milkar aapki codebase ko itna robust bana deta hai ki 1 lakh lines of code mein bhi refactoring karne mein maza aata hai, darr nahi lagta!