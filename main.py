from fastapi import FastAPI, Request
from pydantic import BaseModel
from datetime import datetime
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib import const
import openai
import os

app = FastAPI()

# Replace with your OpenAI API key or set as environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---- MODELS ----
class BirthData(BaseModel):
    date: str       # Format: YYYY-MM-DD
    time: str       # Format: HH:MM (24-hour)
    location: str   # Placeholder (optional for now)
    latitude: float
    longitude: float

# ---- HELPER FUNCTIONS ----
def get_astro_data(date: str, time: str, lat: float, lon: float):
    dt = Datetime(date, time, "+00:00")  # Assuming UTC
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

def build_prompt(astro):
    return f"""
    Generate a poetic, mystical quote under 20 words.
    Person's Sun is in {astro['Sun']}, Moon in {astro['Moon']}, Ascendant in {astro['Ascendant']}, Saturn in {astro['Saturn']}.
    The quote should reflect emotional depth, inner clarity, and cosmic awareness.
    Use a Zen or cryptic spiritual tone.
    """

def get_quote(prompt):
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

# ---- API ENDPOINT ----
@app.post("/generate-quote")
async def generate_quote(data: BirthData):
    astro = get_astro_data(data.date, data.time, data.latitude, data.longitude)
    prompt = build_prompt(astro)
    quote = get_quote(prompt)
    return {"quote": quote, "astrology": astro}
