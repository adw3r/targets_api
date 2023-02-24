import fastapi
import uvicorn
from fastapi import FastAPI, Response
from starlette.responses import RedirectResponse

import module.services as _services
from config import HOST, PORT, DEBUG
from module.database import _orm
from module.pools import Factories
from module.services import create_database

app = FastAPI()
factories = Factories()
create_database()


@app.get('/targets')
async def get_factories(method: str = 'info', db: _orm.Session = fastapi.Depends(_services.get_db)):
    match method:
        case 'info':
            info = await _services.get_all_sources_info(db)
            return info
        # case 'reload':
        #     await factories.reload_pools()
        #     return RedirectResponse('/targets')


@app.get('/targets/{pool}')
async def test(pool: str, method: str = 'info', db: _orm.Session = fastapi.Depends(_services.get_db)):
    match method:
        case 'info':
            info = await _services.info(db, pool)
            return info
        case 'pool':
            pool = await _services.get_pool(db, pool)
            return Response(content='\n'.join(pool))
        case 'pop':
            email = await _services.get_email_from_pool(db, pool)
            return Response(content=email.email)


@app.get('/')
async def get_root():
    return RedirectResponse('/targets')


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=DEBUG)
