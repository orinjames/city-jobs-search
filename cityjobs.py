
'''
City Job Search App

to add:
- number of positions?
- reformat dates
- reformat agency names (normal case, )

'''

import tkinter as tk                    # user interface module
from tkinter import ttk                 # user interface
import pandas as pd                     # dataframe functionality
from datetime import datetime           # date and time functionality
import webbrowser                       # allows opening links

# _________________ DATA _________________

def get_data():
    # Request data from API using maximum limit of 50,000 to override default limit of 1,000
    jobs_url = "https://data.cityofnewyork.us/resource/kpav-sd4t.csv?$limit=50000" # ABOUT: https://data.cityofnewyork.us/City-Government/Jobs-NYC-Postings/kpav-sd4t/about_data
    jobs_df = pd.read_csv(jobs_url)
    return jobs_df

def prepare_data(df):
    # Convert dates to datetime format
    df["posting_date"] = pd.to_datetime(df["posting_date"])

    df["formatted_date"] = df["posting_date"].dt.strftime('%a %d %b %Y')

    # Add URL column
    df["url"] = ("https://cityjobs.nyc.gov/jobs?q=" + df["job_id"].astype(str) + "&options=&page=1")

    # Add column as text to show for URL link
    df["link_text"] = "Click Here"

    # Sort by date ascending
    df = df.sort_values(by='posting_date', ascending=False)
    return df

# _________________ TIME FILTER _________________
def get_last_24_hours(df):
    last_24h = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('24h')]
    return last_24h

def get_last_7_days(df):
    last_7d = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('7d')]
    return last_7d

def get_last_30_days(df):
    last_month = df[df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('30d')]
    return last_month

# _________________ AGENCY FILTER _________________

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

# _________________ RESULTS VIEW _________________

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
                row["formatted_date"],
                row["link_text"],
            ),
            tags=(row["url"])
        )
    
    # Show number of results in frame label
    results_frame.config(text=f" Results: {len(df)} jobs ")

# Adds option to open job posting online
# def open_url(event):
#     item_id = results_tree.focus()
#     if item_id:
#         url = results_tree.item(item_id, "tags")[0]  # get URL from tags
#         webbrowser.open_new_tab(url)

def open_url(event):
    region = results_tree.identify("region", event.x, event.y)
    if region != "cell":
        return

    column = results_tree.identify_column(event.x)
    item = results_tree.identify_row(event.y)

    # URL column is column #4
    if column == "#4" and item:
        tags = results_tree.item(item, "tags")
        url = tags[0]  # first tag is the URL
        webbrowser.open_new_tab(url)

#========================================================

# ============== MAIN ============== #

# Create dataframe of job postings
jobs_df = prepare_data(get_data())

# __________ GUI Setup __________ #
'''
Grid format
'''
root = tk.Tk()
root.title("City Jobs Search")
root.geometry("900x600")    # window width & height in pixels

# Configure row weights so row 1 (bottom) expands
root.rowconfigure(1, weight=1)

# Configure column weights so column 1 (right side) expands
root.columnconfigure(0, weight=0)  # Left column (radio buttons) - fixed
root.columnconfigure(1, weight=1)  # Right column (main content) - flexible 

# ============== Intro information ============== #

now = datetime.now()
now_output_format = now.strftime("%B %d, %Y at %I:%M %p")

# Tool overview/introduction
intro_text = (
    f"Jobs sorted by date (new to old). Close and restart to refresh data. NYC Open Data API accessed on {now_output_format}."
)
intro = tk.Label(root, text=intro_text, font=("Helvetica", 10), justify="left")
intro.grid(row=0, column=0, columnspan=2, sticky="w", pady=10, padx=10)

# ============== FILTERS INTERFACE ============== #

# Setup frame for filter interface features
filter_frame = ttk.LabelFrame(root, text=" Filters ")
filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

# __________ TIMEFRAME SELECT __________ #

# Variable for radio button selection
radio_selection = tk.StringVar(value="none")  # Default to "none" to have invisible radio selected (visual glitch otherwise)

# Radio buttons
radio_24h = tk.Radiobutton(filter_frame, text="Posted in last 24 hours", variable=radio_selection, value="24h", command=apply_filters, font=("Helvetica", 10))
radio_24h.grid(row=0, column=0, sticky="nw")

radio_7d = tk.Radiobutton(filter_frame, text="Posted in last 7 days", variable=radio_selection, value="7d", command=apply_filters, font=("Helvetica", 10))
radio_7d.grid(row=1, column=0, sticky="nw")

radio_1m = tk.Radiobutton(filter_frame, text="Posted in last 30 days", variable=radio_selection, value="30d", command=apply_filters, font=("Helvetica", 10))
radio_1m.grid(row=2, column=0, sticky="nw")

# Invisible radio button required to create initial view with no selections
dummy_radio_button = tk.Radiobutton(filter_frame, variable=radio_selection, value="none")
dummy_radio_button.pack_forget()    # Makes button invisible

# __________ AGENCY SELECT __________ #

# Setup listbox to hold agency names
agency_listbox = tk.Listbox(
    filter_frame,
    selectmode="multiple",
    height=10
)
agency_listbox.grid(row=3, column=0, sticky="nsew")

# Listener to filter results whenever listbox item selected
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

# Add agency names to list
populate_agency_list(jobs_df)

# BUTTONS
# Interface button setup
btn_frame = ttk.Frame(filter_frame)
btn_frame.grid(row=4, column=0, pady=10, columnspan=2)

# Clear all filters
ttk.Button(btn_frame, text="Clear Filters", command=clear_filters).grid(
    row=0,
    column=0,
)

# ============== RESULTS DISPLAY ============== #

# Create right-side frame for results
results_frame = ttk.LabelFrame(root, text=f" Results ")
results_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

# __________ Treeview setup __________ #
# Treeview columns
columns = ("business_title", "agency", "formatted_date", "link_text")

results_tree = ttk.Treeview(
    results_frame,
    columns=columns,
    show="headings"
)
results_tree.grid(row=0, column=0, sticky="nsew")

# Set column headers
results_tree.heading("business_title", text="Job Title")
results_tree.heading("agency", text="Agency")
results_tree.heading("formatted_date", text="Posted Date")
results_tree.heading("link_text", text="Link")

# Format columns
results_tree.column("business_title", width=150, anchor="w")
results_tree.column("agency", width=150, anchor="w")
results_tree.column("formatted_date", width=30, anchor="w")
results_tree.column("link_text", width=30, anchor="center")

# Add scrollbar
scrollbar = ttk.Scrollbar(
    results_frame,
    orient="vertical",
    command=results_tree.yview
)
scrollbar.grid(row=0, column=1, sticky="ns")
results_tree.configure(yscrollcommand=scrollbar.set)

# Link opening listener
# results_tree.bind("<Double-1>", open_url)
results_tree.bind("<Button-1>", open_url)


# Make results frame expandable
results_frame.columnconfigure(0, weight=1)
results_frame.rowconfigure(0, weight=1)

# ============== INITIAL RESULTS ============== #
update_results(jobs_df)

# ============== ROOT INTERFACE ============== #
root.mainloop() # Runs interface window
