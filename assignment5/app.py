"""
strompris fastapi app entrypoint
"""
import datetime
from datetime import timedelta
import os
from typing import List, Optional

import altair as alt
from fastapi import FastAPI, Query, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from strompris import (
    ACTIVITIES,
    LOCATION_CODES,
    fetch_day_prices,
    fetch_prices,
    plot_activity_prices,
    plot_daily_prices,
    plot_prices,
    plot_activity_mean_price,
)
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(
    request: Request,
    location_codes: dict = LOCATION_CODES,
    today: Optional[datetime.date] = datetime.date.today(),
    days: Optional[int] = 7,
):
    """Render the home page.

    Args:
        - request (Request): The FastAPI Request object.

    Returns:
        - templates.TemplateResponse: The rendered home.html template with the
        provided data.
    """
    return templates.TemplateResponse(
        "strompris.html",
        {
            "request": request,
            "location_codes": location_codes,
            "today": today,
            "days": days,
        },
    )


@app.get("/plot_prices.json")
async def get_plot_prices(
    locations: Optional[List[str]] = Query(default=list(LOCATION_CODES.keys())),
    end: Optional[datetime.date] = None,
    days: Optional[int] = 7,
):
    """
    Get the vega-lite JSON chart for electricity prices.

    Args:
        - locations (Optional[List[str]]): A list of location codes for which to
        fetch prices. Defaults to all locations.
        - end (Optional[datetime.date]): The end date for fetching prices.
        Defaults to the current date.
        - days (Optional[int]): The number of days to fetch prices for.
        Defaults to 7.

    Returns:
        - dict: A dictionary containing the vega-lite JSON chart for electricity prices.
    """
    prices_df = fetch_prices(end, days, locations)

    prices_chart = plot_prices(prices_df)
    mean_chart = plot_daily_prices(prices_df)
    stacked_chart = alt.layer(mean_chart, prices_chart)

    return stacked_chart.to_dict()


@app.get("/activity")
async def get_activity(
    request: Request,
    location_codes: dict = LOCATION_CODES,
    activities: dict = ACTIVITIES,
    today: datetime.date = datetime.date.today(),
):
    """
    Get the activity template.

    Args:
        - request (Request): The FastAPI request object.
        - location_codes (dict): Dictionary mapping location codes to names.
        - activities (dict): Dictionary mapping activity names to energy values.
        - today (Optional[date]): The current date. Defaults to the current date.

    Returns:
        - templates.TemplateResponse: The FastAPI template response for the activity template.
    """
    return templates.TemplateResponse(
        "activity.html",
        {
            "request": request,
            "location_codes": location_codes,
            "activities": activities,
            "today": today,
        },
    )


@app.get("/plot_activity.json")
async def get_plot_activity(
    location: Optional[str] = "NO1",
    activity: Optional[str] = "shower",
    minutes: Optional[int] = 10,
    today: Optional[datetime.date] = None,
):
    """
    Get the JSON chart for the specified activity.

    Args:
        - location (Optional[str]): The location code. Defaults to "NO1".
        - activity (Optional[str]): The activity name. Defaults to "shower".
        - minutes (Optional[int]): The duration of the activity in minutes. Defaults to 10.
        - today (Optional[datetime.date]): The current date. Defaults to None.

    Returns:
        - dict: The JSON chart representing the specified activity.
    """
    df = fetch_day_prices(date=today, location=location)
    prices_chart = plot_activity_prices(df=df, activity=activity, minutes=minutes)
    mean_chart = plot_activity_mean_price(df=df, activity=activity, minutes=minutes)
    return alt.layer(mean_chart, prices_chart).to_dict()


# mount your docs directory as static files at `/help`
app.mount(
    "/help/",
    StaticFiles(directory=os.getcwd() + "/docs/_build/html", html=True),
    name="help",
)


def main():
    """Launches the application on port 5000 with uvicorn"""
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)


if __name__ == "__main__":
    main()
