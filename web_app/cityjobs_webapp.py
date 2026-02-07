from flask import Flask                 # Python webapp functionality
from flask import render_template       # render HTML templates
from flask import request               # read incoming form data
from flask import session               # allows caching api data rather than request each time
from flask import jsonify
import json

from datetime import datetime
import pandas as pd

# import my data modules
from data import get_data, prepare_data

now = datetime.now()
now_output_format = now.strftime("%B %d, %Y at %I:%M %p")
INTRO_TEXT = (
    f"Jobs sorted by posting date (new to old). Data updated weekly; see cityjobs.nyc.gov for jobs posted between updates.\nNYC Open Data API accessed on {now_output_format}."
)


# Start app
app = Flask(__name__)
app.secret_key = "top_secret_key"


# _________________ TIME FILTER METHODS _________________
def get_last_24_hours(df):
    last_24h = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('24h')]
    return last_24h

def get_last_7_days(df):
    last_7d = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('7d')]
    return last_7d

def get_last_30_days(df):
    last_month = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('30d')]
    return last_month

def apply_filters(df, time_filter, selected_agencies):
    # __________ Apply posting date filters __________
    if time_filter == "24h":
        timeframe_df = get_last_24_hours(df)
    elif time_filter == "7d":
        timeframe_df = get_last_7_days(df)
    elif time_filter == "30d":
        timeframe_df = get_last_30_days(df)
    else:
        timeframe_df = df

    # __________ Apply agency filters __________
    if selected_agencies:
        filtered_df = timeframe_df[timeframe_df["agency"].isin(selected_agencies)]
    else:
        filtered_df = timeframe_df

    return filtered_df


# Setup root URL "/" and methods for page loads/submits
@app.route("/", methods=["GET", "POST"])
def home():

    jobs_df = prepare_data(get_data())
    
    job_count = len(jobs_df)

    # Dataframe columns & labels for display
    results_columns_to_labels = {
        "business_title": "Title",
        "agency": "Agency",
        "formatted_date": "Posting Date",
        "link_text": "Posting Link",
    }

    agencies = sorted(jobs_df["agency"].dropna().unique())

    # Set default value for time_filter
    time_filter = None

    # Set default agency selection
    selected_agencies = []

    # Check if user submitted filters
    if request.method == "POST":
        # Get the radio button value
        time_filter = request.form.get("time_filter")
        print(time_filter)

        # Get selected agencies
        selected_agencies = request.form.getlist("agencies")
        print(selected_agencies)

        jobs_df = apply_filters(jobs_df, time_filter, selected_agencies)
        job_count = len(jobs_df)

    # Render HTML template, pass values to app
    return render_template(
        "index.html",
        intro_text = INTRO_TEXT,
        jobs_data = jobs_df,
        columns = results_columns_to_labels,
        job_count = job_count,
        agencies = agencies,
        selected_agencies = selected_agencies,
        )

@app.route("/filter", methods=["POST"])
def filter_jobs():
    """API endpoint that receives filter values and returns filtered jobs as JSON"""
    
    # Get the full dataset
    jobs_df = prepare_data(get_data())
    
    # Get filter values from the AJAX request
    time_filter = request.form.get("time_filter")
    selected_agencies = request.form.getlist("agencies")
    
    # Apply filter
    filtered_df = apply_filters(jobs_df, time_filter, selected_agencies)
    
    # Convert to JSON string first, then let Flask parse it
    jobs_json = filtered_df.to_json(orient='records')
    jobs_list = json.loads(jobs_json)

    result = {
        "jobs": jobs_list,  # This is a JSON string
        "count": len(filtered_df)
    }
    
    return jsonify(result)      # ensure JSON format
    
if __name__ == "__main__":
    app.run(debug=True)
