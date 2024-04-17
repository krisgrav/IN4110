# IN3110/IN4110 Strømpris

## Welcome to Strømpris

The web application Strømpris serves as a platform for visualizing and analyzing electricity prices and consumption-related data. Users can explore and compare energy prices across different locations, track daily and hourly variations, and assess the impact of activities on electricity costs. Additionally, the application offers interactive features, enabling users to select specific locations, activities, and time frames for a more personalized and insightful experience.

## Notes for Grader

### Tasks

| Implemented | Not implemented |
| ----------- | --------------- |
| 5.1 - 5.6   | 5.7             |

## How to use Strømpris

### To install dependencies, enter project directory and run:

    python3 -m pip install -e .

### To run web-application, run command

    python3 app.py

### To test methods in terminal, run command:

    python3 strompris.py

### Navigation

#### Activity Prices

This page lets the user monitor cost of using electrical appliances through-out the day.

#### Electricity Prices

This page lets the user review energy-prices and trends in selected locations and timeframes.

#### FastAPI docs

This navigation directs you to the automated documentation of the FastAPI applied in the web-application.

#### Help

This navigation directs you to the applications help-page, that contains overview and explanation of all methods used in the web-application.

## Dependencies

- altair==4.\*
- altair-viewer
- beautifulsoup4
- fastapi[all]
- pandas
- pytest
- requests
- requests-cache
- uvicorn
