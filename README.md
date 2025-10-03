# Ruminus Scraper

A web application to scrape and download data from the [minfin.com.ua](https://index.minfin.com.ua/en/russian-invading/casualties/) website.

## Features

*   **Get Today's Data:** Download a CSV file with the latest data for the current day.
*   **Get All Data:** Download a CSV file with all the historical data from February 2022 to the present day.

## Tech Stack

*   **Backend:** FastAPI, Python
*   **Frontend:** HTML, CSS, JavaScript
*   **Scraping:** httpx, BeautifulSoup

## How to run

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/ruminus-scraper.git
    ```
2.  Install the dependencies:
    ```bash
    uv pip install -e .
    ```
3.  Run the web service:
    ```bash
    uvicorn src.ruminus_scraper.main_web:app --reload
    ```
4.  Open your browser and go to `http://127.0.0.1:8000`
