from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import openai
import os

app = FastAPI()
print("🔥 main.py is running")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/ping")
async def ping():
    return {"status": "alive"}

class BirthData(BaseModel):
    date: str
    time: str
    location: str
    latitude: float
    longitude: float

def get_astro_data(date, time, lat, lon):
    dt = Datetime(date, time, "+00:00")
    pos = GeoPos(str(lat), str(lon))
    chart = Chart(dt, pos)
    return {
        "Sun": chart.get(const.SUN).sign,
        "Moon": chart.get(const.MOON).sign,
        "Ascendant": chart.get(const.ASC).sign,
        "Saturn": chart.get(const.SATURN).sign
    }

def build_prompt(astro):
    return f"""
    Generate a poetic, mystical quote under 20 words.
    Sun: {astro['Sun']}, Moon: {astro['Moon']}, Asc: {astro['Ascendant']}, Saturn: {astro['Saturn']}.
    Zen or cryptic tone.
    """

def get_quote(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        return "⚠️ Missing API key"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a poetic oracle."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.8
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("❌ GPT Error:", e)
        return "⚠️ GPT error"

@app.post("/generate-quote")
async def generate_quote(data: BirthData):
    astro = get_astro_data(data.date, data.time, data.latitude, data.longitude)
    prompt = build_prompt(astro)
    quote = get_quote(prompt)
    return {"quote": quote, "astrology": astro}
