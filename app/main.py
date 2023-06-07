import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app import cache, routers
from app.config import HOST, PORT, DEBUG

app = FastAPI(
    title='Email automation api'
)

app.include_router(routers.links.router)
app.include_router(routers.projects.router)
app.include_router(routers.referrals.router)
app.include_router(routers.stats.router)
app.include_router(routers.targets.router)
app.include_router(routers.texts.router)


@app.on_event('startup')
def startup():
    cache.create_cache()


@app.on_event('shutdown')
def startup():
    cache.kill_cache()


@app.get('/', tags=['root'])
async def get_root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=DEBUG)
