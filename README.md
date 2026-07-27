# SportTracker 🏃‍♂️

A modern, responsive fitness tracking web app built with Flask, SQLite,
Chart.js, and Leaflet.js (OpenStreetMap).

## Features

- **Home page** with hero section and feature highlights
- **Auth**: register, login, logout, profile management
- **Dashboard**: steps, distance, calories, running time, avg speed, water
  intake, and daily goal progress bars
- **Running Tracker**: start/stop timer, live GPS route on an OpenStreetMap
  (Leaflet.js) map, distance + speed calculation, running history
- **Calories Calculator**: estimate calories burned from age, weight,
  duration, and distance
- **Water Tracker**: quick-add buttons, custom amounts, progress ring
- **Activity History**: full table of past daily activity
- **Weekly Charts**: steps / distance / calories via Chart.js
- **Contact page** with a form, and social links

## Project Structure

```
sporttracker/
├── app.py                 # Flask app: routes, auth, DB logic
├── requirements.txt
├── database/
│   ├── schema.sql         # Reference schema (tables auto-created by app.py)
│   └── sports.db          # Created automatically on first run
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html / register.html / profile.html
│   ├── dashboard.html
│   ├── running.html
│   ├── calories.html
│   ├── water.html
│   ├── history.html
│   ├── about.html
│   └── contact.html
└── static/
    ├── css/style.css
    ├── js/main.js, map.js, running.js, charts.js
    └── images/
```

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

The app will be available at **http://127.0.0.1:5000**. The SQLite database
(`database/sports.db`) and all tables are created automatically the first
time you run it.

## Notes

- The Running Tracker uses the browser's Geolocation API — allow location
  access when prompted, and use **HTTPS or localhost** (browsers block
  geolocation on plain HTTP for non-localhost hosts).
- Calories burned during a run are estimated using a MET-based formula
  factoring in your profile weight.
- All map tiles come from the free OpenStreetMap tile server via Leaflet.js —
  no API key required.
- For production use, replace `app.secret_key` in `app.py` with a securely
  generated secret, and set `debug=False`.
