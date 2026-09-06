import models
from typing import Annotated
from datetime import datetime
from sqlalchemy import select,Text
from sqlalchemy.orm import Session
from database import Base, engine,get_db
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI,Request,HTTPException,status,Depends
from schemas import PostCreate,PostResponse,UserResponse, UserCreate
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()
templates = Jinja2Templates(directory ="templates")
Base.metadata.create_all(bind=engine)

@app.get("/", include_in_schema=False)
@app.get("/post",include_in_schema=False)
def home(request:Request):
    return templates.TemplateResponse(request,"home.html",{"post":posts,"title":"Homepage"})

# ================ APIs ================

# Posts
# GET POST
@app.get("/api/post",response_model=list[PostResponse])
def get_post(db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    if posts:
        return posts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")

#  GET POST BY ID
@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post_by_id(post_id: int,db: Annotated[Session,Depends(get_db)]):
    result = db.execute(
        select(models.Post).where(models.Post.id==post_id)
    )
    posts = result.scalars().first()
    if posts:
        return posts
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post not found")
    

# CREATE POST 
@app.post("/api/post",response_model=PostCreate,status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate,db:Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.id== post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request:Request,exception:RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()
        })
        
@app.post("/api/users",response_model=UserResponse,status_code=status.HTTP_201_CREATED,)
def create_user(user: UserCreate, db: Annotated[Session,Depends(get_db)]):
    result = db.execute(select(models.User).where(models.User.username==user.username))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist" 
        )
    result = db.execute(select(models.User).where(models.User.email==user.email))
    existing_email = result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exist"
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
        
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
        
@app.get("/api/users/{user_id}",response_model=UserResponse)
def get_user(user_id:int,db: Annotated[Session,Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id==user_id)
    )
    user = result.scalars().first()
    if user: return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found")

@app.get("/api/users/{user_id}/posts",response_model=list[PostResponse])
def get_user_posts(user_id:int,db: Annotated[Session,Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.id==user_id)
    )
    user = result.scalars().first()
    print(user)
    if user: 
        return user.post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not Found")

