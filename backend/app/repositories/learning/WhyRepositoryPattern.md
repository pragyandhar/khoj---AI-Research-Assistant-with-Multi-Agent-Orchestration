### Questions
#### Why repository pattern is used in my project?
Me dependency inversion principle ko follow kr rha hoon. 

High-level modules (Service/Business Logic) must not be dependent on the Low-level modules (DB) because this may lead to tight coupling of modules. And if we have to switch our DB in the future, we have to rewrite everything. 

Repository ek abstraction layer ki tarah kaam kar rha hai. Is project me Langgraph ke checkpoints bahut sensitive hai. While fetching data for them, ek galat SQL query might corrupt the entire graph state. 

Repository ka use karke ham yeh ensure kar rhe hai ki DB operations safe, testable and centralized ho taki agar kabhi production ke time pr agar hame kabhi bhi AWS pr ya Redis pr backup karna ho to ham sirf iss repository me change kareinge aur na ki pure project ke every relevant file me.