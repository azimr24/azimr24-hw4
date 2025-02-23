#!/usr/bin/env python3
"""
API endpoint for county_data

This function is intended to be deployed on Vercel as a serverless function.
It accepts HTTP POST requests with JSON content, which must include a 5-digit ZIP code and a measure_name.
It queries data.db (created previously) by joining the zip_county and county_health_rankings tables and returns matching results in JSON.

Special behavior:
- If the JSON data contains a key coffee with value teapot, it immediately returns HTTP 418.
- If required parameters are missing or invalid, it returns HTTP 400.
- If no matching records are found, it returns HTTP 404.

The allowed measure_name values are specified in allowed_measures.
"""

import json
import sqlite3
import os

allowed_measures = [
    "Violent crime rate",
    "Unemployment",
    "Children in poverty",
    "Diabetic screening",
    "Mammography screening",
    "Preventable hospital stays",
    "Uninsured",
    "Sexually transmitted infections",
    "Physical inactivity",
    "Adult obesity",
    "Premature Death",
    "Daily fine particulate matter"
]

def handler(request, response):
    try:
        # Only allow POST requests
        if request.method != 'POST':
            response.status_code = 404
            return response.send('Not Found')

        try:
            # Parse JSON body
            body = request.body.decode('utf-8') if isinstance(request.body, bytes) else request.body
            data = json.loads(body)
        except Exception as e:
            response.status_code = 400
            return response.send('Invalid JSON')

        # Check for coffee=teapot special behavior
        if data.get('coffee') == 'teapot':
            response.status_code = 418
            return response.send("I'm a teapot")

        # Validate required parameters zip and measure_name
        zip_code = data.get('zip')
        measure_name = data.get('measure_name')

        if not zip_code or not measure_name:
            response.status_code = 400
            return response.send('Missing required parameters')

        if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
            response.status_code = 400
            return response.send('Invalid ZIP code')

        if measure_name not in allowed_measures:
            response.status_code = 400
            return response.send('Invalid measure_name')

        # Connect to the SQLite database
        db_path = os.path.join(os.path.dirname(__file__), '..', 'data.db')
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        query = '''
        SELECT county_health_rankings.State,
               county_health_rankings.County,
               county_health_rankings.State_code,
               county_health_rankings.County_code,
               county_health_rankings.Year_span,
               county_health_rankings.Measure_name,
               county_health_rankings.Measure_id,
               county_health_rankings.Numerator,
               county_health_rankings.Denominator,
               county_health_rankings.Raw_value,
               county_health_rankings.Confidence_Interval_Lower_Bound,
               county_health_rankings.Confidence_Interval_Upper_Bound,
               county_health_rankings.Data_Release_Year,
               county_health_rankings.fipscode
        FROM zip_county 
        JOIN county_health_rankings 
          ON zip_county.county_code = county_health_rankings.County_code
        WHERE zip_county.zip = ?
          AND county_health_rankings.Measure_name = ?
        '''

        cur.execute(query, (zip_code, measure_name))
        rows = cur.fetchall()
        conn.close()

        if not rows:
            response.status_code = 404
            return response.send('Not Found')

        # Define output field names (lowercase with underscores)
        columns = [
            "state", 
            "county", 
            "state_code", 
            "county_code", 
            "year_span", 
            "measure_name", 
            "measure_id", 
            "numerator", 
            "denominator", 
            "raw_value", 
            "confidence_interval_lower_bound", 
            "confidence_interval_upper_bound", 
            "data_release_year", 
            "fipscode"
        ]

        results = [dict(zip(columns, row)) for row in rows]

        response.headers['Content-Type'] = 'application/json'
        return response.send(json.dumps(results))

    except Exception as e:
        response.status_code = 500
        return response.send(str(e))

__all__ = ['handler']
