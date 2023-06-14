import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app import cache, donors, links, referrals, stats, targets, texts
from app.config import HOST, PORT, DEBUG

if DEBUG:
    title = f'Email automation api DEBUG'
else:
    title = f'Email automation api'

app = FastAPI(title=title)

app.include_router(donors.router)
app.include_router(links.router)
app.include_router(referrals.router)
app.include_router(stats.router)
app.include_router(targets.router)
app.include_router(texts.router)


@app.on_event('startup')
def startup():
    if not DEBUG:
        cache.create_cache()
        stats.update_stats()


@app.on_event('shutdown')
def startup():
    if not DEBUG:
        cache.kill_cache()
    else:
        pass


@app.get('/', tags=['root'])
async def get_root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    uvicorn.run('app.main:app', host=HOST, port=int(PORT), reload=DEBUG)
