from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

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

@app.route('/county_data', methods=['POST'])
def county_data():
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Check for teapot
        if data.get('coffee') == 'teapot':
            return "I'm a teapot", 418

        # Validate required parameters
        zip_code = data.get('zip')
        measure_name = data.get('measure_name')

        if not zip_code or not measure_name:
            return jsonify({'error': 'Missing required parameters'}), 400

        if not (isinstance(zip_code, str) and len(zip_code) == 5 and zip_code.isdigit()):
            return jsonify({'error': 'Invalid ZIP code'}), 400

        if measure_name not in allowed_measures:
            return jsonify({'error': 'Invalid measure_name'}), 400

        # Connect to database
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
            return jsonify({'error': 'No data found'}), 404

        # Define column names
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

        # Convert to list of dictionaries
        results = [dict(zip(columns, row)) for row in rows]
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run()
