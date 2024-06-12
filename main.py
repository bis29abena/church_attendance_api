from fastapi import FastAPI
from sqlmodel import SQLModel
from dotenv import load_dotenv
import uvicorn
from db import engine
from contextlib import asynccontextmanager
from routers.tittle_route import TitleRouter
from routers.user_route import UserRouter
from routers.attendancetype_route import AttendancetypeRouter
from routers.servicetype_route import ServiceTypeRouter
from routers.service_route import ServiceRoute
from routers.auth_route import AuthRouter
from routers.members_route import MembersRoute


# load environment variables
load_dotenv(".env")

# create a lifespan which will be called before the apps run and it will
# be used throughout the application cycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

title_router = TitleRouter()
user_router = UserRouter()
attendancetype_router = AttendancetypeRouter()
servicetype_router = ServiceTypeRouter()
service_router = ServiceRoute()
auth_route = AuthRouter()
member_route = MembersRoute()

# instantiate the fast api
app = FastAPI(lifespan=lifespan)

app.include_router(title_router)
app.include_router(user_router)
app.include_router(attendancetype_router)
app.include_router(servicetype_router)
app.include_router(service_router)
app.include_router(auth_route)
app.include_router(member_route)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
