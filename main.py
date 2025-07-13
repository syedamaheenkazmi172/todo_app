from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlalchemy
import databases

database_url="postgresql://postgres:forensics@localhost:5432/todo_db" 

#to setup connection
database=databases.Database(database_url) #connects to the database with database_url mentioned above
metadata=sqlalchemy.MetaData()#to store the tasks in the form of table in database where sqlalchemy translates the information into sql

tasks_table=sqlalchemy.Table(
    "tasks",
    metadata, 
    sqlalchemy.Column("id",sqlalchemy.Integer,primary_key=True),
    sqlalchemy.Column("title",sqlalchemy.String),
    sqlalchemy.Column("complete",sqlalchemy.Boolean,default=False),
)

#connecting it to postgresql
engine=sqlalchemy.create_engine(database_url)
metadata.create_all(engine)

app=FastAPI() #this way app inherits all parameters and functions of FastAPI

class TaskIn(BaseModel):
    title: str
    complete: bool = False
class Task(TaskIn):
    id: int

#connect to database on startup/shut down
@app.on_event("startup")
async def startup():
    await database.connect() #await fetches the data from the database

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

#routes

#@app.get("/",tags=["Welcome"])
#def welcome():
#    return {"message": "Welcome to To-Do App"}

@app.post("/tasks",response_model=Task)
async def create_tasks(task:TaskIn):
    query=tasks_table.insert().values(title=task.title,complete=task.complete)
    task_id=await database.execute(query) #creates an id automatically using sql
    return Task(id=task_id,**task.dict())

@app.get("/tasks",response_model=List[Task])
async def all_tasks():
    query = tasks_table.select().order_by(tasks_table.c.complete, tasks_table.c.id)
    return await database.fetch_all(query)

@app.get("/tasks/{task_id}",response_model=Task)
async def get_task(task_id:int):
    query = tasks_table.select().where(tasks_table.c.id == task_id)
    task=await database.fetch_one(query)
    if task is None:
        raise HTTPException(status_code=404,detail="Task not found")
    return task    

@app.put("/tasks/{task_id}",response_model=Task)
async def update_task(task_id:int,updated_task:TaskIn):
    query = tasks_table.update().where(tasks_table.c.id == task_id).values(**updated_task.dict())
    await database.execute(query)
    return Task(id=task_id, **updated_task.dict())

#to update the status to complete
@app.patch("/tasks/{task_id}/complete",response_model=Task)
async def mark_completed(task_id:int):
    task=await database.fetch_one(tasks_table.select().where(tasks_table.c.id==task_id))
    if not task:
        raise HTTPException(status_code=404,detail="Task not found")
    update=tasks_table.update().where(tasks_table.c.id==task_id).values(complete=True)
    await database.execute(update)
    return Task(id=task_id,title=task["title"],complete=True)

@app.delete("/tasks/{task_id}")
async def delete_task(task_id:int):
    query = tasks_table.delete().where(tasks_table.c.id == task_id)
    await database.execute(query)
    return {"message": "Task deleted"}