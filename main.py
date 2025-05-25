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

# Serve the static folder at root
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# API MODEL
class BirthData(BaseModel):
    date: str
    time: str
    location: str
    latitude: float
    longitude: float

# Astrology calculation
def get_astro_data(date: str, time: str, lat: float, lon: float):
    dt = Datetime(date, time, "+00:00")
    pos = GeoPos(str(lat), str(lon))
    chart = Chart(dt, pos)
    sun = chart.get(const.SUN)
    moon = chart.get(const.MOON)
    asc = chart.get(const.ASC)
    saturn = chart.get(const.SATURN)
    return {
        "Sun": sun.sign,
        "Moon": moon.sign,
        "Ascendant": asc.sign,
        "Saturn": saturn.sign
    }

# Prompt generation
def build_prompt(astro):
    return f"""
    Generate a poetic, mystical quote under 20 words.
    Person's Sun is in {astro['Sun']}, Moon in {astro['Moon']}, Ascendant in {astro['Ascendant']}, Saturn in {astro['Saturn']}.
    The quote should reflect emotional depth, inner clarity, and cosmic awareness.
    Use a Zen or cryptic spiritual tone.
    """

# GPT-safe version with error handling
def get_quote(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        print("⚠️ OPENAI_API_KEY is missing")
        return "⚠️ Missing OpenAI API Key."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a poetic spiritual oracle."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=60
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        print("GPT Error:", e)
        return "⚠️ GPT API call failed."

# API endpoint
@app.post("/generate-quote")
async def generate_quote(data: BirthData):
    print("📥 Birth data received:", data)
    astro = get_astro_data(data.date, data.time, data.latitude, data.longitude)
    print("🔮 Astro data:", astro)
    prompt = build_prompt(astro)
    print("📝 Prompt:\n", prompt)
    quote = get_quote(prompt)
    print("💬 Quote:", quote)
    return {"quote": quote, "astrology": astro}
