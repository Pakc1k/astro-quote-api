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

# 🔐 Set your OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# 🔁 Serve static HTML from /static/index.html
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# 📩 Input model for POST
class BirthData(BaseModel):
    date: str       # Format: YYYY-MM-DD
    time: str       # Format: HH:MM (24-hour)
    location: str   # Optional placeholder for now
    latitude: float
    longitude: float

# 🔮 Calculate simplified birth chart
def get_astro_data(date: str, time: str, lat: float, lon: float):
    dt = Datetime(date, time, "+00:00")  # UTC assumed
    pos = GeoPos(str(lat), str(lon))
    chart = Chart(dt, pos)

    return {
        "Sun": chart.get(const.SUN).sign,
        "Moon": chart.get(const.MOON).sign,
        "Ascendant": chart.get(const.ASC).sign,
        "Saturn": chart.get(const.SATURN).sign
    }

# 🧠 Generate GPT prompt from astrology
def build_prompt(astro):
    return f"""
    Generate a poetic, mystical quote under 20 words.
    Person's Sun is in {astro['Sun']}, Moon in {astro['Moon']}, Ascendant in {astro['Ascendant']}, Saturn in {astro['Saturn']}.
    The quote should reflect emotional depth, inner clarity, and cosmic awareness.
    Use a Zen or cryptic spiritual tone.
    """

# ✨ Get quote from GPT
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

# 🚀 API endpoint
@app.post("/generate-quote")
async def generate_quote(data: BirthData):
    astro = get_astro_data(data.date, data.time, data.latitude, data.longitude)
    prompt = build_prompt(astro)
    quote = get_quote(prompt)
    return {"quote": quote, "astrology": astro}
