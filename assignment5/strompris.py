#!/usr/bin/env python3
"""
Fetch data from https://www.hvakosterstrommen.no/strompris-api
and visualize it.

Assignment 5
"""

from datetime import datetime, date, time, timezone, timedelta
import warnings

import altair as alt
import pandas as pd
import requests
import requests_cache

# install an HTTP request cache
# to avoid unnecessary repeat requests for the same data
# this will create the file http_cache.sqlite
requests_cache.install_cache()

# suppress a warning with altair 4 and latest pandas
warnings.filterwarnings("ignore", ".*convert_dtype.*", FutureWarning)


# task 5.1:


def fetch_day_prices(date: datetime.date = None, location: str = "NO1") -> pd.DataFrame:
    """Fetch one day of data for one location from hvakosterstrommen.no API.

    Args:
        - date (datetime.date, optional): The date for which to fetch prices. If None, the current date is used.
        - location (str, optional): The location for which to fetch prices. Defaults to "NO1".

    Returns:
        pd.DataFrame: A DataFrame containing the fetched data with columns:
            - 'NOK_per_KWh' (float): The price in Norwegian Krone per kilowatt-hour.
            - 'time_start' (datetime): The start time of the corresponding period.
            - 'location_code': Code for location (NO1, NO2, ...)
            - 'location': Name of location, derived from location_code
    """
    # Make call to get_date to get tupple of year, month, day
    if date is None:
        year, month, day = get_date()
    else:
        year, month, day = get_date(date)

    # Construct URL
    url = f"https://www.hvakosterstrommen.no/api/v1/prices/{year}/{month}-{day}_{location}.json"
    # Request data from API and parse results.
    result = requests.get(url).json()
    data = []
    for entry in result:
        data.append(
            [
                float(entry["NOK_per_kWh"]),
                datetime.fromisoformat((entry["time_start"])),
                location,
                LOCATION_CODES[location],
            ]
        )

    # Create and return dataframe from data
    df = pd.DataFrame(
        data, columns=["NOK_per_kWh", "time_start", "location_code", "location"]
    )
    return df


# LOCATION_CODES maps codes ("NO1") to names ("Oslo")
LOCATION_CODES = {
    "NO1": "Oslo",
    "NO2": "Kristiansand",
    "NO3": "Trondheim",
    "NO4": "Tromsø",
    "NO5": "Bergen",
}

# task 1:


def fetch_prices(
    end_date: datetime.date = None,
    days: int = 7,
    locations: list[str] = tuple(LOCATION_CODES.keys()),
) -> pd.DataFrame:
    """Fetch prices for multiple days and locations into a single DataFrame.

    Args:
        - end_date (datetime.date, optional): The end date for fetching prices. Defaults to the current date.
        - days (int, optional): The number of days to fetch prices for. Defaults to 7 days.
        - locations (list[str], optional): A list of location codes for which to fetch prices. Defaults to all locations.

    Returns:
        - pd.DataFrame: A DataFrame containing prices for multiple days and locations.

    """

    if end_date is None:
        year, month, day = get_date()
        end_date = datetime(int(year), int(month), int(day))

    data_frames = []
    for loc in locations:
        for d in range(days - 1, -1, -1):
            year, month, day = get_date(end_date - timedelta(days=d))
            data = fetch_day_prices(datetime(int(year), int(month), int(day)), loc)

            data["time_start"] = pd.to_datetime(
                data["time_start"], utc=True
            ).dt.tz_convert("Europe/Oslo")

            # Makeshift way of solving problem with (daylight savings) 29.10 having 2 * 02:00am time_starts
            # If data-df has 25 entries, finds the matches and calculates average NOK_per_kWh
            if len(data) == 25:
                # Convert to datetime without timezone
                data["time_start"] = pd.to_datetime(
                    data["time_start"], format="%Y-%m-%d %H:%M:%S%z"
                ).dt.strftime("%Y-%m-%d %H:%M:%S")
                # Find indices with the same time_start
                duplicate_indices = data[
                    data.duplicated(subset=["time_start"], keep=False)
                ].index
                # Calculate the average of NOK_per_kWh for the matching indices
                average_price = data.loc[duplicate_indices, "NOK_per_kWh"].mean()
                # Replace the duplicate indices with the average price
                data.loc[duplicate_indices, "NOK_per_kWh"] = average_price
                # Drop duplicates based on time_start
                data = data.drop_duplicates(subset=["time_start"]).reset_index(
                    drop=True
                )

            # Convert timestamp back to correct type
            data["time_start"] = pd.to_datetime(
                data["time_start"], utc=True
            ).dt.strftime("%Y-%m-%d %H:%M:%S")

            data["time_start"] = pd.to_datetime(
                data["time_start"], utc=True
            ).dt.tz_convert("Europe/Oslo")

            # For each date, get tha data from the previous 24h for calculating change.
            h24_year, h24_month, h24_day = get_date(end_date - timedelta(days=d + 1))
            h24_data = fetch_day_prices(
                datetime(int(h24_year), int(h24_month), int(h24_day)), loc
            )
            h24_data["time_start"] = pd.to_datetime(
                data["time_start"], utc=True
            ).dt.tz_convert("Europe/Oslo")

            # For each date, get tha data from 7d ago for calculating change.
            d7_year, d7_month, d7_day = get_date(end_date - timedelta(days=d + 7))
            d7_data = fetch_day_prices(
                datetime(int(d7_year), int(d7_month), int(d7_day)), loc
            )
            d7_data["time_start"] = pd.to_datetime(
                data["time_start"], utc=True
            ).dt.tz_convert("Europe/Oslo")

            # Iterate over row in data-DF and calculate + add change.
            for index, row in data.iterrows():

                kWh = row[
                    "NOK_per_kWh"
                ]  # Get kWh price of current row for caluclating change.

                if (
                    index == 0
                ):  # If first timeframe of the day, use last timeframe from yesterday.
                    h1_kWh = h24_data.loc[len(h24_data) - 1]["NOK_per_kWh"]
                    percentage_change_1h = round(((kWh - h1_kWh) / h1_kWh) * 100, 1)
                    data.at[index, "1h_change"] = f"{percentage_change_1h}%"
                else:  # If not first timeframe of day, use data from last hour
                    h1_kWh = data.loc[index - 1]["NOK_per_kWh"]
                    percentage_change_1h = round(((kWh - h1_kWh) / h1_kWh) * 100, 1)
                    data.at[index, "1h_change"] = f"{percentage_change_1h}%"

                h24_kWh = h24_data.loc[index]["NOK_per_kWh"]
                d7_kWh = d7_data.loc[index]["NOK_per_kWh"]
                percentage_change_24h = round(((kWh - h24_kWh) / h24_kWh) * 100, 1)
                percentage_change_7d = round(((kWh - d7_kWh) / d7_kWh) * 100, 1)
                data.at[index, "24h_change"] = f"{percentage_change_24h}%"
                data.at[index, "7d_change"] = f"{percentage_change_7d}%"

            data_frames.append(data)

    data_frames = pd.concat(data_frames, ignore_index=True)
    data_frames = add_currencies(data_frames)
    return data_frames


# task 5.1:


def plot_prices(df: pd.DataFrame) -> alt.Chart:
    """Plot energy prices over time.

    Args:
        - df (pd.DataFrame): The DataFrame containing the price data.

    Returns:
        - alt.Chart: An Altair chart object displaying the energy prices over time.

        - x-axis: time_start (datetime)
        - y-axis: NOK_per_kWh (float)
        - The chart includes interactive features:
            - Points are displayed on the lines.
            - Legends allow for the selection of specific locations.
            - Tooltips provide detailed information on data points.
    """

    # Selection for making location in chart legend clickable
    legend_selection = alt.selection_multi(fields=["location"], bind="legend")

    location_colors = {
        "Oslo": "blue",
        "Kristiansand": "green",
        "Trondheim": "purple",
        "Tromsø": "orange",
        "Bergen": "#e83e8c",  # Deep pink
    }

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X(
                "time_start:T", title="Date", axis=alt.Axis(format="%d.%m (%I %p)")
            ),
            y="NOK_per_kWh:Q",
            color=alt.Color(
                "location:N",
                scale=alt.Scale(
                    domain=list(location_colors.keys()),
                    range=list(location_colors.values()),
                ),
            ),
            tooltip=[
                alt.Tooltip("time_start:T", title="Time", format="%d.%m.%y (%I:%M %p)"),
                alt.Tooltip("NOK_per_kWh:Q", title="NOK per kWh", format=".4f"),
                alt.Tooltip("USD_per_kWh:Q", title="USD per kWh", format=".4f"),
                alt.Tooltip("EUR_per_kWh:Q", title="EUR per kWh", format=".4f"),
                alt.Tooltip("location:N", title="Location"),
                alt.Tooltip("1h_change:N", title="1 hour change"),
                alt.Tooltip("24h_change:N", title="24 hour change"),
                alt.Tooltip("7d_change:N", title="7 days change"),
            ],
            text=alt.Text("location:N"),
        )
        .properties(title="NOK per kWh Over Time", width=1000, height=400)
        .add_selection(legend_selection)
        .transform_filter(legend_selection)  # Add selection event
    )

    return chart


# Task 5.4


def plot_daily_prices(df: pd.DataFrame) -> alt.Chart:
    """Plot the daily average price.

    Args:
        - df (pd.DataFrame): The DataFrame containing the price data.

    Returns:
        - alt.Chart: An Altair chart object displaying the daily average energy prices.
    """
    chart = (
        alt.Chart(df)
        .mark_rule(color="grey", strokeDash=[2, 2])
        .encode(
            x=alt.X(
                "time_start:T", title="Date", axis=alt.Axis(format="%d.%m (%I %p)")
            ),
            y=alt.Y("mean(NOK_per_kWh):Q"),
            color=alt.value("grey"),
        )
        .properties(title="Avg daily NOK per kWh", width=1000, height=400)
    )
    return chart


# Task 5.6

ACTIVITIES = {"shower": 30, "baking": 2.5, "heat": 1}


def plot_activity_prices(
    df: pd.DataFrame, activity: str = "shower", minutes: float = 10
) -> alt.Chart:
    """
    Plot price for one activity by name,
    given a data frame of prices, and its duration in minutes.
    
    Args:
        - df (pd.DataFrame): The DataFrame containing the price data.
        - activity (str): Activity to plot price for.
        - minutes (float): Minutes to plot price for.

    Returns:
        - alt.Chart: An Altair chart object displaying the daily average energy prices.
    """
    df = calculate_price(df, activity, minutes)

    # Get date from first row in df (all rows should be same date)
    date = pd.to_datetime(df.iloc[0]["time_start"]).strftime("%d.%m.%y")

    # Create chart for activity prices
    legend_selection = alt.selection_multi(fields=["location"], bind="legend")
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X("time_start:T", title="Time", axis=alt.Axis(format="%H:%M")),
            y=alt.Y("price:Q", title="Price (NOK)"),
            color=alt.Color("location:N"),
            tooltip=[
                alt.Tooltip("time_start:T", title="Time", format="%d.%m.%y (%I:%M %p)"),
                alt.Tooltip("price:Q", title="Price (NOK)", format=".4f"),
            ],
        )
        .properties(
            title=f"Activity price for {activity} on date {date}",
            width=1000,
            height=400,
        )
        .add_selection(legend_selection)
        .transform_filter(legend_selection)  # Add selection event
    )

    # Calculate mean for all activity prices in df
    mean_price = df["price"].mean()

    # Create horizontal line showing the mean-price.
    mean_line = (
        alt.Chart(pd.DataFrame({"mean_price": [mean_price]}))
        .mark_rule(
            color="red", strokeDash=[2, 2]
        )  # You can customize the color and style
        .encode(y="mean_price:Q")
    )

    # Returned layered chart of activity prices and mean price.
    return chart


def plot_activity_mean_price(
    df: pd.DataFrame, activity: str = "shower", minutes: float = 10
) -> alt.Chart:
    """
    Plot a horizontal line representing the mean price of a specific activity.

    Args:
        - df (pd.DataFrame): Input DataFrame containing electricity consumption data.
        - activity (str): Name of the activity for which to calculate the mean price.
        - minutes (float): Duration of the activity in minutes.

    Returns:
        - alt.Chart: Altair Chart object representing the plot.
    """
    df = calculate_price(df, activity, minutes)
    # Calculate mean for all activity prices in df
    mean_price = df["price"].mean()

    # Create horizontal line showing the mean-price.
    chart = (
        alt.Chart(pd.DataFrame({"mean_price": [mean_price]}))
        .mark_rule(
            color="grey", strokeDash=[2, 2]
        )  # You can customize the color and style
        .encode(y="mean_price:Q")
    )

    return chart


def get_date(date_obj: datetime = None) -> tuple[str, str, str]:
    """
    Get the formatted date in the format of four-digit year, two-digit month, and two-digit day.

    Args:
        - date_obj (datetime.date, optional): A datetime.date object. If provided, the function
        will format this date; otherwise, the current date will be used.

    Returns:
        - tuple: A tuple containing the formatted year, month, and day as strings.
    """
    # Get the current date and time
    if date_obj is None:
        date_obj = datetime.now()

    # Extract year, month, and day from the current date
    year = date_obj.year
    month = date_obj.month
    day = date_obj.day

    # Convert year to four-digit and month, and day to two-digit format
    year_str = str(year).zfill(4)
    month_str = str(month).zfill(2)
    day_str = str(day).zfill(2)

    return year_str, month_str, day_str


def calculate_price(df: pd.DataFrame, activity: str, minutes: float) -> pd.DataFrame:
    """
    Calculate the price for a specific activity over time.

    Args:
        - df (pd.DataFrame): The DataFrame containing the price data.
        - activity (str): The name of the activity for which to calculate the price.
        - minutes (float): The duration of the activity in minutes.

    Returns:
        - pd.DataFrame: A new DataFrame containing columns for activity, time_start, location, and price.
    """
    activity_prices = []
    # Iterate all rows in the df, and calculate the price. Create new df with price, time, activity and location.
    for index, row in df.iterrows():
        price = ((minutes / 60) * ACTIVITIES[activity]) * row["NOK_per_kWh"]
        activity_prices.append([activity, row["time_start"], row["location"], price])
    df = pd.DataFrame(
        activity_prices, columns=["activity", "time_start", "location", "price"]
    )

    return df


def add_currencies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Adds columns to the provided DataFrame for equivalent prices in USD and EUR.

    Args:
        - dataframe (pd.DataFrame): The input DataFrame containing a column "NOK_per_kWh" with prices in Norwegian Krone.

    Returns:
        - pd.DataFrame: The updated DataFrame with additional columns "USD_per_kWh" and "EUR_per_kWh" representing equivalent prices in US Dollars and Euros, respectively.
    """
    for index, row in dataframe.iterrows():
        NOK = row["NOK_per_kWh"]
        dataframe.at[index, "USD_per_kWh"] = (
            NOK * 0.094
        )  # Current UDS conversion-rate (21.11.2023)
        dataframe.at[index, "EUR_per_kWh"] = (
            NOK * 0.086
        )  # Current EUR conversion-rate (21.11.2023)
    return dataframe


def main():
    """Allow running this module as a script for testing."""
    df = fetch_prices()
    print(df)
    price_chart = plot_prices(df)
    daily_avg_chart = plot_daily_prices(df)

    df = fetch_day_prices()
    print(df)
    activity_price_chart = plot_activity_prices(df)

    # showing the chart without requiring jupyter notebook or vs code for example
    # requires altair viewer: `pip install altair_viewer`
    price_chart.show()
    daily_avg_chart.show()
    activity_price_chart.show()


if __name__ == "__main__":
    main()
