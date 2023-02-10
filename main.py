import uvicorn
from fastapi import FastAPI, Response
from starlette.responses import RedirectResponse

from config import HOST, PORT, DEBUG
from module.pools import FilePool, Factories

app = FastAPI()
factories = Factories()


@app.get('/')
async def get_root():
    return RedirectResponse('/targets')


@app.get('/targets')
async def get_factories(method: str = 'info'):
    match method:
        case 'info':
            return {key: item.info() for key, item in factories.items()}
        case 'reload':
            factories.reload_pools()
            return RedirectResponse('/targets')


@app.get('/targets/{pool}')
async def get_factory_pool(pool: str, method: str = 'info'):
    proxy_pool: FilePool = factories.get(pool)
    match method:
        case 'info':
            info = proxy_pool.info()
            return info
        case 'pool':
            pool = proxy_pool.get_pool()
            return Response(content='\n'.join(pool))
        case 'pop':
            value = proxy_pool.pop()
            return Response(content=value)
        case 'clear':
            proxy_pool.clear()
            return RedirectResponse(f'/targets/{pool}')
        case 'reload':
            proxy_pool.reload()
            return RedirectResponse(f'/targets/{pool}')


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=DEBUG)
