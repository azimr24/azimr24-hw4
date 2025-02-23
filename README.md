# County Health Rankings API

This project provides an API to access county health rankings data. The API is deployed on Vercel and accessible at [https://azimr24-hw4.vercel.app/county_data](https://azimr24-hw4.vercel.app/county_data).

## Project Structure

- `api/county_data.py`: Main Flask application that serves the API endpoint
- `csv_to_sqlite.py`: Utility script to convert CSV data into SQLite database
- `data.db`: SQLite database containing the county health rankings data
- `vercel.json`: Vercel deployment configuration
- `csv_data/`: Directory containing the default CSV data files
- `.gitignore`: Specifies which files Git should ignore

## Setup and Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create the SQLite database using the provided CSV data:
```bash
python csv_to_sqlite.py data.db csv_data/county_health_rankings.csv
```

## Database Setup (`csv_to_sqlite.py`)

The `csv_to_sqlite.py` script converts CSV data into an SQLite database. It's used to create the `data.db` file that powers the API.

Usage:
```bash
python csv_to_sqlite.py <database_file> <csv_file>
```

Example using the default data in the csv_data directory:
```bash
python csv_to_sqlite.py data.db csv_data/county_health_rankings.csv
```

You can also use your own CSV files as long as they follow the same structure as the provided data.

## API Usage (`county_data.py`)

The API provides a single endpoint at `/county_data` that accepts both GET and POST requests:

- GET `/county_data`: Returns an HTML interface for testing the API
- POST `/county_data`: Accepts JSON data and returns county health rankings data

### POST Request Parameters

```json
{
    "zip": "string",         // Required: 5-digit ZIP code
    "measure_name": "string", // Required: One of the allowed measures
    "limit": number,         // Optional: Number of results to return (default: 10)
    "coffee": "teapot"      // Optional: Returns HTTP 418 response
}
```

### Allowed Measures

- Violent crime rate
- Unemployment
- Children in poverty
- Diabetic screening
- Mammography screening
- Preventable hospital stays
- Uninsured
- Sexually transmitted infections
- Physical inactivity
- Adult obesity
- Premature Death
- Daily fine particulate matter

### Example Response

```json
[
    {
        "state": "Massachusetts",
        "county": "Middlesex County",
        "state_code": "25",
        "county_code": "017",
        "year_span": "2014",
        "measure_name": "Adult obesity",
        "measure_id": "OBESITY",
        "numerator": "null",
        "denominator": "null",
        "raw_value": "20.0",
        "confidence_interval_lower_bound": "19.0",
        "confidence_interval_upper_bound": "21.0",
        "data_release_year": "2014",
        "fipscode": "25017"
    }
]
```

### CURL Examples

1. Basic request:
```bash
curl -X POST https://azimr24-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip": "02138", "measure_name": "Adult obesity", "limit": 5}'
```

2. Teapot response:
```bash
curl -X POST https://azimr24-hw4.vercel.app/county_data \
  -H "Content-Type: application/json" \
  -d '{"zip": "02138", "measure_name": "Adult obesity", "coffee": "teapot"}'
```

## Live Demo

The API is deployed and accessible at: [https://azimr24-hw4.vercel.app/county_data](https://azimr24-hw4.vercel.app/county_data)

Visit this URL to:
1. Test the API through a user-friendly interface
2. Submit requests with different parameters
3. Try the famous HTTP 418 "I'm a teapot" response
