from flask import Flask                 # Python webapp functionality
from flask import render_template       # render HTML templates
from flask import request               # read incoming form data

from datetime import datetime

# import my data modules
from data import get_data, prepare_data

now = datetime.now()
now_output_format = now.strftime("%B %d, %Y at %I:%M %p")
INTRO_TEXT = (
    f"Jobs sorted by posting date (new to old). Data updated weekly; see cityjobs.nyc.gov for jobs posted between updates.\nNYC Open Data API accessed on {now_output_format}."
)


# Start app
app = Flask(__name__)

# Setup root URL "/" and methods for page loads/submits
@app.route("/", methods=["GET", "POST"])

def home():

    df = get_data()
    jobs_df = prepare_data(df)
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
    
if __name__ == "__main__":
    app.run(debug=True)
