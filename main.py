from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory ="templates")
post: list[dict] = [
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
    return templates.TemplateResponse(request,"home.html",{"post":post,"title":"Homepage"})

@app.get("/api/post")
def get_post():
    return post

@app.get(f"/api/post/{post_id}")
def get_post(post_id):
    for p