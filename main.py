import fastapi
import uvicorn
from fastapi import FastAPI, Response
from starlette.responses import RedirectResponse

import module.services as _services
from config import HOST, PORT, DEBUG
from module.database import _orm
from module.services import create_database

app = FastAPI()
create_database()


@app.get('/targets')
async def get_factories(method: str = 'info', db: _orm.Session = fastapi.Depends(_services.get_db)):
    match method:
        case 'info':  # todo tests
            info = await _services.get_all_sources_info(db)  # todo tests
            return info


@app.get('/targets/{pool}')
async def test(pool: str, method: str = 'info', limit: int = 100, db: _orm.Session = fastapi.Depends(_services.get_db)):
    match method:
        case 'info':
            info = _services.info(db, pool)
            return info
        case 'pool':
            pool = _services.get_pool(db, pool, limit=limit)
            return Response(content='\n'.join([email.email for email in pool]))
        case 'pop':  # todo tests
            email = _services.get_available_email_from_pool(db, pool)
            return Response(content=email.email)


@app.get('/')
async def get_root():
    return RedirectResponse('/targets')


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=DEBUG)
