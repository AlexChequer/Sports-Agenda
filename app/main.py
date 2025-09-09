from fastapi import FastAPI
from app.api.routes import health, public, internal


app = FastAPI(title="Sports-Agenda")


app.include_router(health.router, tags=["health"])
app.include_router(public.router, tags=["public"])
app.include_router(internal.router, tags=["internal"])

