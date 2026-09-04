from fastapi import FastAPI,Request,HTTPException,status,Depends
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from schemas import PostCreate,PostResponse 
from datetime import datetime
from typing import Annotated


templates = Jinja2Templates(directory ="templates")
posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "Getting Started with FastAPI",
        "content": "FastAPI makes it easy to build fast and modern APIs with Python.",
        "date_posted": "2026-08-15",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Understanding Python Type Hints",
        "content": "Type hints make Python code easier to read, maintain, and validate.",
        "date_posted": "2026-08-16",
    },
    {
        "id": 3,
        "author": "John Smith",
        "title": "Building Your First API Endpoint",
        "content": "A simple GET endpoint is a great way to learn the basics of FastAPI.",
        "date_posted": "2026-08-17",
    },
]
app = FastAPI()

@app.get("/", include_in_schema=False)
@app.get("/post",include_in_schema=False)
def home(request:Request):
    return templates.TemplateResponse(request,"home.html",{"post":posts,"title":"Homepage"})

@app.get("/api/post",response_model=list[PostResponse])
def get_post():
    return posts

@app.get("/api/post/{post_id}", response_model=PostResponse)
def get_post_by_id(post_id: int):
    post = next((p for p in posts if p["id"] == post_id),None)
    print(post)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found!")
    return post

@app.post("/api/post",response_model=PostCreate,status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts)+ 1 if posts else 1
    new_post = {
        "id":new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    posts.append(new_post)
    return new_post


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request:Request,exception:RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()
        })