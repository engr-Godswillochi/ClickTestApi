from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import string
import random

app = FastAPI()

# In-memory store
link_store = {}

# Pydantic model for input
class LinkCreate(BaseModel):
    target_url: str

# Utility to generate random slug
def generate_slug(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten")
def create_short_link(link: LinkCreate):
    slug = generate_slug()
    while slug in link_store:
        slug = generate_slug()  # avoid collision

    link_store[slug] = {
        "target_url": link.target_url,
        "click_count": 0,
    }

    return {
        "slug": slug,
        "short_url": f"http://localhost:8000/{slug}",
        "target_url": link.target_url
    }

@app.get("/{slug}")
def redirect(slug: str, request: Request):
    link_data = link_store.get(slug)
    if not link_data:
        raise HTTPException(status_code=404, detail="Link not found")

    link_data["click_count"] += 1
    return RedirectResponse(url=link_data["target_url"])

@app.get("/stats/{slug}")
def get_stats(slug: str):
    link_data = link_store.get(slug)
    if not link_data:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return {
        "slug": slug,
        "target_url": link_data["target_url"],
        "click_count": link_data["click_count"]
    }
