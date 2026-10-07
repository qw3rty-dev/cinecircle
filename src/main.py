from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.admin.router import router as admin_router
from src.auth.router import router as auth_router
from src.feed.router import router as feed_router
from src.media.router import router as media_router
from src.reviews.router import router as reviews_router
from src.scheduler.scheduler import configure_scheduler, scheduler
from src.users.router import router as users_router
from src.watchlist.router import router as watchlist_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    configure_scheduler()
    scheduler.start()
    yield
    scheduler.shutdown()
    await app.state.http_client.aclose()


app = FastAPI(title="CineCircle API", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(media_router)
app.include_router(watchlist_router)
app.include_router(reviews_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(feed_router)
