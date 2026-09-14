from fastapi import FastAPI
from src.auth.router import router as auth_router
from src.media.router import router as media_router
from src.watchlist.router import router as watchlist_router
from src.reviews.router import router as reviews_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(media_router)
app.include_router(watchlist_router)
app.include_router(reviews_router)