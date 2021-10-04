import uvicorn
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, Response

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

import db_manager as db

cursor = db.connection.cursor()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

async def make_piechart_1(count_of_employeed, count_of_quitting):
    buff = BytesIO()
    labels = ['Нормальное\nсостояние', 'Высокий риск\nувольнения', ]
    plt.tight_layout()
    plt.pie(
        [count_of_employeed - count_of_quitting, count_of_quitting], 
        labels = labels, 
        colors = sns.color_palette('pastel')[::-6], 
        autopct='%.0f%%', explode=(0, 0.2), 
        textprops={'Fontsize' : 13})

    plt.savefig(buff)
    plt.close()

    return base64.b64encode(buff.getbuffer()).decode("ascii")

async def make_piechart_2(data):
    buff = BytesIO()
    # fig, ax = plt.subplots(1, 1)
    plt.tight_layout()
    plt.pie(
        data, 
        labels=['Проблемы с\nзарплатой', 'Проблемы со\nстажем', 'Проблемы с \nвозрастом'],
        colors=sns.color_palette('pastel')[0::2],
        explode=(0.05, 0.05, 0.05),
        autopct='%.0f%%',
        textprops={'Fontsize' : 13}
    )
    plt.savefig(buff)
    plt.close()

    return base64.b64encode(buff.getbuffer()).decode("ascii")

async def get_risk_zone_guys():
    columns = (
        'Имя',
        'Пол',
        'Отдел',
        'Начальник ⇵',
        'Возраст ⇵',
        'Стаж с ⇵',
        'Оплата ⇵',
        'Срок работы',
        'Оценка стажа',
        'Оценка возраста',
        'Оценка зарплаты'
        )

    sql_str = 'select name, sex, departament, chief, age, hire_date, payment from employee where finish_date != "None"'
    
    base_data = pd.DataFrame(
        cursor.execute(sql_str).fetchall(), 
        columns=columns[:-4]
        )

    base_data['Стаж ⇵'] = pd.to_datetime(base_data['Стаж ⇵'], format='%d.%m.%Y', errors='coerce')
    base_data.dropna(inplace=True)
    count_of_employeed = base_data.shape[0]
    base_data['Стаж, дни'] = (pd.Timestamp.now() - base_data['Стаж ⇵']).apply(lambda x : x.days)

    base_data['Стаж ⇵'] = base_data['Стаж ⇵'].apply(lambda x : str(x)[:-9])

    std_stage_dict = dict((base_data[['Отдел', 'Стаж, дни']].groupby('Отдел').agg('mean') - base_data[['Отдел', 'Стаж, дни']].groupby('Отдел').agg(np.std)).to_records())
    std_age_dict = dict((base_data[['Отдел', 'Возраст ⇵']].groupby('Отдел').agg('mean') - base_data[['Отдел', 'Возраст ⇵']].groupby('Отдел').agg(np.std)).to_records())
    std_salary_dict = dict((base_data[['Отдел', 'Оплата ⇵']].groupby('Отдел').agg('mean') - base_data[['Отдел', 'Оплата ⇵']].groupby('Отдел').agg(np.std)).to_records())

    base_data = base_data.join(pd.DataFrame(base_data[['Отдел', 'Стаж, дни']].apply(lambda x : 1 if x[1] >= std_stage_dict[x[0]] else 0, axis=1), columns=['Оценка стажа']))
    base_data = base_data.join(pd.DataFrame(base_data[['Отдел', 'Возраст ⇵']].apply(lambda x : 1 if x[1] >= std_age_dict[x[0]] else 0, axis=1), columns=['Оценка возраста']))
    base_data = base_data.join(pd.DataFrame(base_data[['Отдел', 'Оплата ⇵']].apply(lambda x : 1 if x[1] >= std_salary_dict[x[0]] else 0, axis=1), columns=['Оценка зарплаты']))

    base_data = base_data[base_data[['Оценка стажа', 'Оценка возраста', 'Оценка зарплаты']].apply(lambda x : True if sum(x) < 2 else False, axis=1)]

    base_data.sort_values(['Оценка зарплаты', 'Оценка стажа', 'Оценка возраста'], inplace=True, ascending=True)
    count_of_quitting = base_data.shape[0]
    base_data = base_data.to_records(index=False)
    
    return (columns, *base_data), count_of_employeed, count_of_quitting, base_data[['Оценка зарплаты', 'Оценка стажа', 'Оценка возраста']]


@app.get('/')
async def main(request : Request):
    risk_zone_guys, count_of_employeed, count_of_quitting, problems_data = await get_risk_zone_guys()
    problems_data = np.array([[int(el) for el in row] for row in problems_data]).sum(axis=0)
    piechart2_src = await make_piechart_2(problems_data)
    piechart1_src = await make_piechart_1(count_of_employeed, count_of_quitting)
    

    return templates.TemplateResponse("index.html", 
        {
            "request": request, 
            "table": risk_zone_guys,
            'piechart1_src' : 'data:image/png;base64,' + str(piechart1_src),
            'piechart2_src' : 'data:image/png;base64,' + str(piechart2_src),
        }
    )

uvicorn.run(
    app, 
    port=8000, 
    host='0.0.0.0'
    )
