# run.py
from graph import graph

result = graph.invoke({
    "message": "i want to know the laundry system",
    "history": []
})

print(result)
