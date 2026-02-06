import pandas as pd


def get_data():
    # Request data from API using maximum limit of 50,000 to override default limit of 1,000
    jobs_url = "https://data.cityofnewyork.us/resource/kpav-sd4t.csv?$limit=50000" # ABOUT: https://data.cityofnewyork.us/City-Government/Jobs-NYC-Postings/kpav-sd4t/about_data
    # Read data into dataframe
    jobs_df = pd.read_csv(jobs_url)
    return jobs_df

def prepare_data(df):
    # Convert dates to datetime format
    df["posting_date"] = pd.to_datetime(df["posting_date"])
    # Format dates
    df["formatted_date"] = df["posting_date"].dt.strftime('%a %d %b %Y')

    # Add URL column
    df["url"] = ("https://cityjobs.nyc.gov/jobs?q=" + df["job_id"].astype(str) + "&options=&page=1")
    # Add text only column to show for URL link
    df["link_text"] = "Click Here"

    # Sort by date ascending (new to old)
    df = df.sort_values(by='posting_date', ascending=False)
    return df