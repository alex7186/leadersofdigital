import uvicorn

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Response


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



async def get_risk_zone_guys():
    risk_zone_guys = (
        (
        'Имя',
        'Отдел',
        'Начальник',
        'Возраст',
        'Прием',
        'Срок работы',
        'Оплата',
        'Возможная причина ухода',
        ),
        (
        'john johns', 
        'departament_id', 
        'director_id', 
        '24',
        'date_employed_aaa', 
        'duration of work_aaa', 
        'payment_$$$',
        'little payment'
        ),
        (
        'dave daves', 
        'departament_id2', 
        'director_id2', 
        '26',
        'date_employed_bbb', 
        'duration of work_bbb', 
        'payment_ррр',
        'bad departament'
        ),
    )
    return risk_zone_guys

@app.get('/')
async def main(request : Request):
    risk_zone_guys = await get_risk_zone_guys()

    # table = '<table> <tr>' + '</tr><tr>'.join([' '.join(map(
    #     (lambda x : f'<td>{str(x)}</td>'),
    #     row
    #     )) for row in risk_zone_guys]) + '<tr> </table>'


    return templates.TemplateResponse("index.html", {"request": request, "table": risk_zone_guys})

uvicorn.run(
    app, 
    port=8000, 
    host='0.0.0.0',

    )