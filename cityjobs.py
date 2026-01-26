
'''
City Job Search App

to add:
- number of positions column

'''

# required for user interface
import tkinter as tk
from tkinter import ttk


import pandas as pd                     # dataframe functionality
from datetime import datetime

# allows opening links
import webbrowser


'''
Get Job Postings (API)
'''
def get_data():
    # Request data from API using maximum limit of 50,000 to override default limit of 1,000
    jobs_url = "https://data.cityofnewyork.us/resource/kpav-sd4t.csv?$limit=50000" # ABOUT: https://data.cityofnewyork.us/City-Government/Jobs-NYC-Postings/kpav-sd4t/about_data


    jobs_df = pd.read_csv(jobs_url)

    # Output date
    now = datetime.now()
    now_output_format = now.strftime("%B %d, %Y at %I:%M %p")
    print(f'NYC Open Data API accessed on {now_output_format}')

    # Output total jobs
    print(f'Total jobs returned by NYC Open Data: {len(jobs_df)}')

    # print(jobs_df.columns)
    # print(jobs_df["agency"].unique())
    # print(jobs_df[jobs_df['agency'] == 'DEPARTMENT OF TRANSPORTATION'].head(5))
    return jobs_df


'''  
Prepare data
- set posting_date to datetime format for sorting
- add url column to link to job posting
- sort all data by date, ascending (newest to oldest)
'''
def prepare_data(df):
    # Convert dates to datetime format
    df["posting_date"] = pd.to_datetime(df["posting_date"])

    # df["formatted_date"] = 

    # Add URL column
    df["url"] = ("https://cityjobs.nyc.gov/jobs?q=" + df["job_id"].astype(str) + "&options=&page=1")

    # Add column as text to show for URL link
    df["link_text"] = "Open Link"

    # Sort by date ascending
    df = df.sort_values(by='posting_date', ascending=False)
    return df


# _________________ TIME FUNCTIONS _________________
def get_last_24_hours(df):
    last_24h = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('24h')]
    return last_24h

def get_last_7_days(df):
    last_7d = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('7d')]
    return last_7d

def get_last_30_days(df):
    last_month = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('30d')]
    return last_month

# _________________ AGENCY FILTER FUNCTIONS _________________

def populate_agency_list(df):
    agencies = sorted(df["agency"].dropna().unique())
    for agency in agencies:
        agency_listbox.insert(tk.END, agency)

# _________________ CLEAR FILTERS _________________

def clear_filters():
    # Clear radio button selection (set to dummy button value)
    radio_selection.set("none")

    # Clear all agency selections
    agency_listbox.select_clear(0, tk.END)
    
    # Update results with original dataframe
    update_results(jobs_df)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def open_url(event):
    item_id = results_tree.focus()
    if item_id:
        url = results_tree.item(item_id, "tags")[0]  # get URL from tags
        webbrowser.open_new_tab(url)

# _________________ APPLY FILTER & SHOW RESULTS _________________

# Applies any filters
def apply_filters(event=None):
    # Apply posting date filters
    if radio_selection.get() == "24h":
        timeframe_df = get_last_24_hours(jobs_df)
    elif radio_selection.get() == "7d":
        timeframe_df = get_last_7_days(jobs_df)
    elif radio_selection.get() == "30d":
        timeframe_df = get_last_30_days(jobs_df)
    else:
        timeframe_df = jobs_df

    # Apply agency filters
    # Get selection from listbox
    selected_indices = agency_listbox.curselection()
    selected_agencies = [agency_listbox.get(i) for i in selected_indices]

    if selected_agencies:
        filtered_df = timeframe_df[timeframe_df["agency"].isin(selected_agencies)]
    else:
        filtered_df = timeframe_df

    # Update results displayed using filters
    update_results(filtered_df)

# Update results displayed
def update_results(df):
    # clear existing rows
    for row in results_tree.get_children():
        results_tree.delete(row)

    # add rows to Treeview
    for _, row in df.iterrows():
        results_tree.insert(
            "",
            tk.END,
            values=(
                row["business_title"],
                row["agency"],
                row["posting_date"],
                row["link_text"],
            ),
            tags=(row["url"])
        )

    
    # Show number of results in frame label
    results_frame.config(text=f" Results: {len(df)} jobs ")



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

jobs_df = prepare_data(get_data())


# __________ GUI Setup __________ #
root = tk.Tk()
root.title("City Jobs Search")
root.geometry("900x600")    # window width & height in pixels


# __________ Intro information __________ #

# Output date and time
now = datetime.now()
now_output_format = now.strftime("%B %d, %Y at %I:%M %p")

# Tool overview/introduction
intro_text = (
    f"Find recently posted jobs and filter by attributes. NYC Open Data API accessed on {now_output_format}."
)

intro = tk.Label(root, text=intro_text, font=("Helvetica", 10), wraplength=700, justify="left")
intro.grid(row=0, column=0, columnspan=2, sticky="w", pady=5, padx=10)

# __________ FILTERS INTERFACE __________ #

# Setup interface frame
filter_frame = ttk.LabelFrame(root, text=" Filters ")
filter_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")


# __________ TIMEFRAME SELECT INTERFACE __________ #

# Holds radio button selection
radio_selection = tk.StringVar(value="none")  # Default to "none" to have invisible radio selected (visual glitch otherwise)


radio_24h = tk.Radiobutton(filter_frame, text="Posted in last 24 hours", variable=radio_selection, value="24h", command=apply_filters, font=("Helvetica", 10))
radio_24h.grid(row=0, column=0, sticky="nw")
radio_7d = tk.Radiobutton(filter_frame, text="Posted in last 7 days", variable=radio_selection, value="7d", command=apply_filters, font=("Helvetica", 10))
radio_7d.grid(row=1, column=0, sticky="nw")
radio_1m = tk.Radiobutton(filter_frame, text="Posted in last 30 days", variable=radio_selection, value="30d", command=apply_filters, font=("Helvetica", 10))
radio_1m.grid(row=2, column=0, sticky="nw")

# Invisible radio button required to create initial view with no selections
dummy_radio_button = tk.Radiobutton(filter_frame, variable=radio_selection, value="none")
dummy_radio_button.pack_forget()    # Makes button invisible
# __________ AGENCY SELECT INTERFACE __________ #

# Create list of agency names in results
agency_listbox = tk.Listbox(
    filter_frame,
    selectmode="multiple",
    height=10
)
agency_listbox.grid(row=3, column=0, sticky="nsew")
agency_listbox.bind("<<ListboxSelect>>", apply_filters)

# Allow listbox to expand
filter_frame.grid_rowconfigure(3, weight=1)

# Add scrollbar
scrollbar = ttk.Scrollbar(
    filter_frame,
    orient="vertical",
    command=agency_listbox.yview
)
scrollbar.grid(row=3, column=1, sticky="ns")
# Connect scrollbar to listbox
agency_listbox.config(yscrollcommand=scrollbar.set)

# __________ Agencies with job postings __________ #
# Add agency name results to list
populate_agency_list(jobs_df)

# __________ Button setup __________ #
# Interface button setup
btn_frame = ttk.Frame(filter_frame)
btn_frame.grid(row=4, column=0, pady=5, sticky="w")

# Clear all filters
ttk.Button(btn_frame, text="Clear Filters", command=clear_filters).grid(
    row=0, column=1
)

# _____________________________________________ #
# __________ RESULTS DISPLAY __________ #
# _____________________________________________ #

# Create right-side frame for results
results_frame = ttk.LabelFrame(root, text=f" Results ")
results_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# Make root expandable
root.columnconfigure(1, weight=1)
root.rowconfigure(1, weight=1)

# __________ Treeview setup __________ #
# Treeview columns
columns = ("business_title", "agency", "posting_date", "url")

results_tree = ttk.Treeview(
    results_frame,
    columns=columns,
    show="headings"
)
results_tree.grid(row=0, column=0, sticky="nsew")

# Set column headers
results_tree.heading("business_title", text="Job Title")
results_tree.heading("agency", text="Agency")
results_tree.heading("posting_date", text="Posted Date")
results_tree.heading("url", text="URL")

# Format columns
results_tree.column("business_title", width=100, anchor="w")
results_tree.column("agency", width=100, anchor="w")
results_tree.column("posting_date", width=100, anchor="w")
results_tree.column("url", width=100, anchor="w")

# Add scrollbar
scrollbar = ttk.Scrollbar(
    results_frame,
    orient="vertical",
    command=results_tree.yview
)
scrollbar.grid(row=0, column=1, sticky="ns")
results_tree.configure(yscrollcommand=scrollbar.set)

# Link opening listener
results_tree.bind("<Double-1>", open_url)


# Make results frame expandable
results_frame.columnconfigure(0, weight=1)
results_frame.rowconfigure(0, weight=1)


# __________ Start with all results __________ #
update_results(jobs_df)


# ____________________________________________________

# Runs GUI window
root.mainloop()