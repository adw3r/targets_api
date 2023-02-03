import uvicorn
from fastapi import FastAPI, Response
from starlette.responses import RedirectResponse

from config import HOST, PORT
from pools import FilePool, Factories

app = FastAPI()
factories = Factories()


@app.get('/')
async def get_root():
    return RedirectResponse('/docs')


@app.get('/targets')
async def get_factories():
    factory_instance = factories.get('targets')
    if factory_instance:
        return {key: item.info() for key, item in factory_instance.items()}


@app.get('/targets/{pool}')
async def get_factory_pools(pool: str):
    factory_instance = factories.get('targets')
    if factory_instance:
        target_pool: FilePool = factory_instance[pool]
        info = target_pool.info()
        return info


@app.get('/targets/{pool}/pool')
async def get_pool_list(pool: str):
    factory_instance = factories.get('targets')
    if factory_instance:
        proxy_pool: FilePool = factory_instance[pool]
        return Response(content='\n'.join(proxy_pool.get_pool()))


@app.get('/targets/{pool}/pop')
async def pop_from_pool(pool: str):
    factory_instance = factories.get('targets')
    if factory_instance:
        target_pool: FilePool = factory_instance[pool]
        value = target_pool.pop()
        return Response(content=value)


@app.get('/targets/{pool}/clear')
async def clear_pool(pool: str):
    factory_instance = factories.get('targets')
    if factory_instance:
        target_pool: FilePool = factory_instance[pool]
        target_pool.clear()
        return target_pool.info()


@app.get('/targets/{pool}/reload')
async def reload_pool(pool: str):
    factory_instance = factories.get('targets')
    if factory_instance:
        target_pool: FilePool = factory_instance[pool]
        target_pool.reload()
        return target_pool.info()


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT))
