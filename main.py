from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app=FastAPI() #this way app inherits all parameters and functions of FastAPI

class Task(BaseModel):
    id:int
    title:str
    complete:bool =False

tasks:List[Task]=[]#this creates a list of several tasks

@app.get("/") #this gets nothing
def read():
    return {"message": "Welcome to To-Do App"}

@app.get("/tasks")
def all_tasks():
    return sorted(tasks, key=lambda x: x.id)

@app.get("/tasks/{task_id}",response_model=Task)
def get_task(task_id:int):
    for task in tasks:
        if task.id==task_id:
            return task
    raise HTTPException(status_code=404,detail="Task not found")

@app.post("/tasks")
def create_tasks(task:Task):
    for t in tasks:
        if t.id==task.id:
            raise HTTPException(status_code=400,detail="Task ID already exists")
    tasks.append(task)
    return task

@app.put("/tasks/{task_id}",response_model=Task)
def update_task(task_id:int,updated_task:Task):
    for i,t in enumerate(tasks):
        if t.id==task_id:
            tasks[i]=updated_task
            return updated_task
    raise HTTPException(status_code=404,detail="Task not found")

#to update the status to complete
@app.patch("/tasks/{task_id}/complete",response_model=Task)
def mark_completed(task_id:int):
    for task in tasks:
        if task_id==task.id:
            task.complete=True
            return task
    raise HTTPException(status_code=404,detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id:int):
    for i,t in enumerate(tasks):
        if t.id==task_id:
            tasks.pop(i)
            return {"message":"task deleted"}
    raise HTTPException(status_code=404,detail="Task not found")
