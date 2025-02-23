#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler
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

def handle_request(request):
    try:
        # Parse JSON body
        body = json.loads(request.get('body', '{}'))

        # Check for coffee=teapot special behavior
        if body.get('coffee') == 'teapot':
            return {
                'statusCode': 418,
                'body': "I'm a teapot"
            }

        # Validate required parameters zip and measure_name
        zip_code = body.get('zip')
        measure_name = body.get('measure_name')

        if not zip_code or not measure_name:
            return {
                'statusCode': 400,
                'body': 'Missing required parameters'
            }

        if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
            return {
                'statusCode': 400,
                'body': 'Invalid ZIP code'
            }

        if measure_name not in allowed_measures:
            return {
                'statusCode': 400,
                'body': 'Invalid measure_name'
            }

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
            return {
                'statusCode': 404,
                'body': 'Not Found'
            }

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

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(results)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

def handler(request):
    if request.get('method') != 'POST':
        return {
            'statusCode': 404,
            'body': 'Not Found'
        }
    return handle_request(request)
