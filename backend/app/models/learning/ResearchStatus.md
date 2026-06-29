### In research.py
#### Question: What is Enum?
Enum ek pre-defined set of values hai. Iss class me aap koi fixed set of values define karte hai. In values ke alawa koi aur value assign nhi kar sakte unn variables ko

Technical Benefits
- Readability: It is better to use ResearchStatus.COMPLETED instead of writing "completed". Readability acchi hoti hai.

- Type Safety: Agar koi bhi function me ham function(status: ResearchStatus) define karte hai to sirf predicted values hi pass honge aur na ki koi random string jaise "complted" ya typos.


#### How does ```str``` help in JSON Serialization? 
Serialize karne ka matlab hai ki ek object ko aaise format me change karna taki ham usse store kar sakein ya uska transmission kar sakein.

Enum ek python object hota hai. JSON objects ko serialize nhi kar pata jab FastAPI ```json.dumps()``` function ko call karta hai JSON response return karne ke liye. 

Agar ham ```(str, Enum)``` pass karte hai PENDING, COMPLETED, ROUTING etc. string ki subclass ban jate hai, to FastAPI ```json.dumps()``` ko jab use karta hai to JSON ko pata hota hai ki abb yeh Enum koi object nhi hai but ek string hai. To ```json.dumps()``` usse JSON me daal sakta hai.

Python Example:
```
# Bina str (Sirf Enum)
class Status1(Enum):
    PENDING = "pending"
    
json.dumps(Status1.PENDING)  # ERROR: Object of type Status1 is not JSON serializable

# str ke saath
class Status2(str, Enum):
    PENDING = "pending"
    
json.dumps(Status2.PENDING)  # OUTPUT: "pending"  (sahi)
```