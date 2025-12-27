from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

app = FastAPI(title="CurrencyConverterWebService")

templates = Jinja2Templates(directory="templates")


# ---------------- JSON Utility Functions ---------------- #

def load_rates():
    with open("exchange_rates.json", "r") as file:
        return json.load(file)  # returns dictionary

def save_rates(data):
    with open("exchange_rates.json", "w") as file:
        json.dump(data, file, indent=4)


# ---------------- FRONTEND PAGES ---------------- #

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/converter", response_class=HTMLResponse)
def converter_page(request: Request):
    return templates.TemplateResponse("converter.html", {"request": request})


# ---------------- BACKEND LOGIC ---------------- #

def get_exchange_rate(from_currency, to_currency):
    rates = load_rates()  # load from JSON

    try:
        amount_in_usd = 1 / rates[from_currency]
        rate = amount_in_usd * rates[to_currency]
        return rate
    except KeyError:
        return None


@app.get("/rate")
def exchange_rate(fromCurrency: str, toCurrency: str):
    rate = get_exchange_rate(fromCurrency, toCurrency)

    if rate is None:
        raise HTTPException(status_code=404, detail="Rate not found")

    return {
        "from": fromCurrency,
        "to": toCurrency,
        "rate": rate
    }


@app.get("/convert")
def convert_currency(fromCurrency: str, toCurrency: str, amount: float):
    rate = get_exchange_rate(fromCurrency, toCurrency)

    if rate is None:
        raise HTTPException(status_code=404, detail="Rate not found")

    converted_amount = amount * rate

    return {
        "from": fromCurrency,
        "to": toCurrency,
        "amount": amount,
        "convertedAmount": converted_amount
    }


# ---------------- Update Rates API (optional to use) ---------------- #

@app.post("/update-rate")
def update_rate(currency: str, rate: float):
    data = load_rates()
    data[currency] = rate  # add/update

    save_rates(data)

    return {"message": f"Rate for {currency} updated successfully!", "new_rate": rate}

