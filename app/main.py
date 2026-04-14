from fastapi import FastAPI
from app.database import Base, engine
from app.routes import user, ticket

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Ticket Management API Running"}

app.include_router(user.router)
app.include_router(ticket.router)