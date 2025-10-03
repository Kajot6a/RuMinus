from fastapi import FastAPI
from pydantic import BaseModel
import re
import csv
from pathlib import Path
import os
from io import StringIO
from fastapi.responses import HTMLResponse, StreamingResponse
import httpx
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

app = FastAPI()

class InputData(BaseModel):
    data: str

def crate_dict(data: list):
    
    dict_file = Path("columns.txt")
    if dict_file.is_file():
        types = []
        with open("columns.txt", "r", encoding="utf-8") as f:
            for line in f:
                types.append(line.strip('\n'))
        return types
    else:
        types = set()
        for row in data:
            for key in row.keys():
                if key != "Date":
                    types.add(key)
        return list(types)

async def create_csv(data: list):
    output = StringIO()
    writer = None
    
    fieldnames = crate_dict(data)
    fieldnames.insert(0, "Date")
    fieldnames = [n.rstrip() for n in fieldnames]

    print(fieldnames)

    writer = csv.DictWriter(output, fieldnames=fieldnames, restval=0, dialect='excel')
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue()

@app.post("/process-today")
async def process_today():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://index.minfin.com.ua/en/russian-invading/casualties/")
        soup = BeautifulSoup(response.text, 'html.parser')
        data = []
        gold_element = soup.find(class_='gold')
        if gold_element.find_parent(class_='footer'):
            return
        date_str = gold_element.find(class_='black').text
        row = {"Date": date_str}
        for item in gold_element.find('ul').find_all('li'):
            parts = item.text.split('—')
            x = re.search(r"[0-9]+", parts[1].strip())
            number = x.group()
            row[parts[0].strip()] = number
        data.append(row)
        
        data.sort(key=lambda x: datetime.strptime(x['Date'], '%d.%m.%Y'))
        csv_data = await create_csv(data)
        today = date.today().strftime("%Y-%m-%d")
        filename = f"ruminus_data_{today}.csv"
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={f"Content-Disposition": f"attachment; filename={filename}"}
        )

@app.post("/process-all")
async def process_all():
    data = []
    dates = []
    start_date = date(2022, 2, 1)
    end_date = date.today()
    current_date = start_date
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December", "Due", "Cost of Russia's losses in Ukraine", "Sanctions against Russia", "Support for Ukraine in the world", "Casualties of Russia in Ukraine", "See also:", "Anti-War Coalition: Breaking News"]
    async with httpx.AsyncClient() as client:
        while current_date <= end_date:
            url = f"https://index.minfin.com.ua/en/russian-invading/casualties/{current_date.strftime('%Y-%m')}/"
            # print(url)
            response = await client.get(url)
            # print(response)
            soup = BeautifulSoup(response.text, 'html.parser')
            for gold_element in soup.find_all(class_='gold'):
                if gold_element.find(class_='black') is None:
                    continue
                if gold_element.find_parent(class_='idx-footer'):
                    continue
                if "idx-footer" in gold_element.parents:
                    continue
                date_str = gold_element.find(class_='black').text
                if date_str in dates:
                    continue
                dates.append(date_str)
                if date_str in months:
                    continue
                row = {"Date": date_str}
                # print(date_str)
                for item in gold_element.find('ul').find_all('li'):
                    if item.text.rstrip() in months:
                        continue
                    parts = item.text.split('—')
                    x = re.search(r"[0-9]+", parts[1].strip())
                    number = x.group()
                    row[parts[0].strip()] = number
                data.append(row)
            current_date += timedelta(days=32)
            current_date = current_date.replace(day=1)

    data.sort(key=lambda x: datetime.strptime(x['Date'], '%d.%m.%Y'), reverse=True)
    csv_data = await create_csv(data)
    # print(data)
    today = date.today().strftime("%Y-%m-%d")
    filename = f"ruminus_data_all_{today}.csv"
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={f"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>RuMinus Scraper</title>
            <style>
                body {
                    background-color: #222;
                    color: #eee;
                    font-family: 'Roboto', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    margin: 0;
                }
                h1 {
                    font-size: 3rem;
                    margin-bottom: 2rem;
                }
                button {
                    background-color: #007bff;
                    color: #fff;
                    border: none;
                    padding: 1rem 2rem;
                    font-size: 1.2rem;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    margin: 0.5rem;
                }
                button:hover {
                    background-color: #0056b3;
                }
                button:disabled {
                    background-color: #555;
                    cursor: not-allowed;
                }
                .loader {
                    border: 16px solid #f3f3f3;
                    border-radius: 50%;
                    border-top: 16px solid #3498db;
                    width: 120px;
                    height: 120px;
                    -webkit-animation: spin 2s linear infinite; /* Safari */
                    animation: spin 2s linear infinite;
                    display: none;
                }

                /* Safari */
                @-webkit-keyframes spin {
                    0% { -webkit-transform: rotate(0deg); }
                    100% { -webkit-transform: rotate(360deg); }
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <h1>RuMinus Scraper</h1>
            <div>
                <button id="process-today-btn" onclick="processToday()">Get Today's Data</button>
                <button id="process-all-btn" onclick="processAll()">Get All Data</button>
            </div>
            <div class="loader" id="loader"></div>
            <script>
                async function processToday() {
                    const processTodayBtn = document.getElementById('process-today-btn');
                    const loader = document.getElementById('loader');

                    processTodayBtn.disabled = true;
                    loader.style.display = 'block';

                    const response = await fetch('/process-today', {
                        method: 'POST',
                    });

                    processTodayBtn.disabled = false;
                    loader.style.display = 'none';

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    const today = new Date();
                    const dateString = today.toISOString().slice(0,10);
                    a.download = `ruminus_data_${dateString}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                }

                async function processAll() {
                    const processAllBtn = document.getElementById('process-all-btn');
                    const loader = document.getElementById('loader');

                    processAllBtn.disabled = true;
                    loader.style.display = 'block';

                    const response = await fetch('/process-all', {
                        method: 'POST',
                    });

                    processAllBtn.disabled = false;
                    loader.style.display = 'none';

                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    const today = new Date();
                    const dateString = today.toISOString().slice(0,10);
                    a.download = `ruminus_data_all_${dateString}.csv`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                }
            </script>
        </body>
    </html>
    '''
