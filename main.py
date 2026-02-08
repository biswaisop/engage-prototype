# run.py
from graph import graph
message = input("Enter your message: ")
result = graph.invoke({
    "message": message,
    "history": []
})

print(result)
