
'''
City Job Search App
'''

import tkinter as tk                    # user interface module
from tkinter import ttk                 # user interface functionality
import pandas as pd                     # dataframe functionality
from datetime import datetime           # date and time functionality
import webbrowser                       # url link opening functionality

class CityJobsApp():
    '''
    Tkinter application for browsing and filtering city job postings.
    '''

    def __init__(self, root):
        '''
        Sets up interface and loads data
        '''
        # setup interface
        self.root = root
        self.root.title("City Jobs Search")
        self.root.geometry("900x600") # window size in pixels
        
        # Configure row weights so row 1 (bottom) expands
        self.root.rowconfigure(1, weight=1)

        # Configure column weights so column 1 (right side) expands
        self.root.columnconfigure(0, weight=0)  # Left column (radio buttons) - fixed
        self.root.columnconfigure(1, weight=1)  # Right column (main content) - flexible

        # Get and prepare dataset
        self.jobs_df = self.prepare_data(self.get_data())

        # Create interface areas
        self.create_intro()
        self.create_filters()
        self.create_results()
    
    def get_data(self):
        # Request data from API using maximum limit of 50,000 to override default limit of 1,000
        jobs_url = "https://data.cityofnewyork.us/resource/kpav-sd4t.csv?$limit=50000" # ABOUT: https://data.cityofnewyork.us/City-Government/Jobs-NYC-Postings/kpav-sd4t/about_data
        # Read data into dataframe
        jobs_df = pd.read_csv(jobs_url)
        return jobs_df

    def prepare_data(self, df):
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

    def create_intro(self):
        '''
        Shares basic information about the app and data with the user.
        '''
        now = datetime.now()
        now_output_format = now.strftime("%B %d, %Y at %I:%M %p")
        intro_text = (
            f"Jobs sorted by date (new to old). Data updated weekly; see cityjobs.nyc.gov for jobs posted between updates.\nNYC Open Data API accessed on {now_output_format}."
        )
        intro = tk.Label(self.root, text=intro_text, font=("Helvetica", 10), justify="left")
        intro.grid(row=0, column=0, columnspan=2, sticky="w", pady=10, padx=10)

    def create_filters(self):
        # Setup frame for filter interface features
        self.filter_frame = ttk.LabelFrame(self.root, text=" Filters ")
        self.filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # __________ TIMEFRAME SELECT __________ #
        # Variable for radio button selection
        self.radio_selection = tk.StringVar(value="none")  # Default to "none" to have invisible radio selected (visual glitch otherwise)

        # Radio buttons (variables not required)
        # 24 hours
        tk.Radiobutton(
            self.filter_frame, 
            text="Posted in last 24 hours", 
            variable=self.radio_selection, # connect to radio_selection var
            value="24h", 
            command=self.apply_filters, 
            font=("Helvetica", 10)
        ).grid(row=0, column=0, sticky="nw")
        # 7 days
        tk.Radiobutton(
            self.filter_frame, 
            text="Posted in last 7 days", 
            variable=self.radio_selection, 
            value="7d", 
            command=self.apply_filters, 
            font=("Helvetica", 10)
        ).grid(row=1, column=0, sticky="nw")
        # 30 days
        tk.Radiobutton(
            self.filter_frame, 
            text="Posted in last 30 days", 
            variable=self.radio_selection, 
            value="30d", 
            command=self.apply_filters, 
            font=("Helvetica", 10)
        ).grid(row=2, column=0, sticky="nw")

        # Invisible radio button required to create initial view with no selections
        dummy_radio_button = tk.Radiobutton(self.filter_frame, variable=None, value="none")
        dummy_radio_button.pack_forget()    # Makes button invisible

        # __________ AGENCY SELECT __________ #
        # Setup listbox to hold agency names
        self.agency_listbox = tk.Listbox(
            self.filter_frame,
            selectmode="multiple",
            height=10
        )
        self.agency_listbox.grid(row=3, column=0, sticky="nsew")

        # Listener to filter results whenever listbox item selected
        self.agency_listbox.bind("<<ListboxSelect>>", self.apply_filters)

        # Allow listbox to expand
        self.filter_frame.grid_rowconfigure(3, weight=1)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.filter_frame,
            orient="vertical",
            command=self.agency_listbox.yview
        )
        scrollbar.grid(row=3, column=1, sticky="ns")
        # Connect scrollbar to listbox
        self.agency_listbox.config(yscrollcommand=scrollbar.set)

        # Add agency names to list
        self.populate_agency_list()

        # __________ CLEAR FILTERS BUTTON __________ #
        # Setup button frame
        btn_frame = ttk.Frame(self.filter_frame)
        btn_frame.grid(row=4, column=0, pady=10, columnspan=2)

        # Clear all filters
        ttk.Button(
            btn_frame, 
            text="Clear Filters", 
            command=self.clear_filters
        ).grid(row=0, column=0)

    def create_results(self):
        # Create right-side frame for results
        self.results_frame = ttk.LabelFrame(self.root, text=f" Results ")
        self.results_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Make results frame expandable
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)

        # __________ Treeview setup __________ #
        # Treeview source columns in dataframe
        columns = ("business_title", "agency", "formatted_date", "link_text")
        self.results_tree = ttk.Treeview(
            self.results_frame,
            columns=columns,
            show="headings"
        )
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        # Set column headers
        self.results_tree.heading("business_title", text="Job Title")
        self.results_tree.heading("agency", text="Agency")
        self.results_tree.heading("formatted_date", text="Posted Date")
        self.results_tree.heading("link_text", text="Link")

        # Format columns
        self.results_tree.column("business_title", width=150, anchor="w")
        self.results_tree.column("agency", width=150, anchor="w")
        self.results_tree.column("formatted_date", width=30, anchor="w")
        self.results_tree.column("link_text", width=30, anchor="center")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            self.results_frame,
            orient="vertical",
            command=self.results_tree.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        # Link opening listener
        self.results_tree.bind("<Button-1>", self.open_url)

        # ============== INITIALIZE RESULTS ============== #
        self.update_results(self.jobs_df)

    def update_results(self, df):
        '''
        Updates results interface with filtered dataframe values.
        '''
        # Clear existing rows
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        # add rows to Treeview
        for _, row in df.iterrows():
            self.results_tree.insert(
                "",
                tk.END,
                values=(
                    row["business_title"],
                    row["agency"],
                    row["formatted_date"],
                    row["link_text"],       # sets text only to "Click Here"
                ),
                tags=(row["url"])           # links URL to row
            )
        
        # Show number of results in frame label
        self.results_frame.config(text=f" Results: {len(df)} jobs ")

    def apply_filters(self, event=None):
        # __________ Apply posting date filters __________
        if self.radio_selection.get() == "24h":
            timeframe_df = self.get_last_24_hours()
        elif self.radio_selection.get() == "7d":
            timeframe_df = self.get_last_7_days()
        elif self.radio_selection.get() == "30d":
            timeframe_df = self.get_last_30_days()
        else:
            timeframe_df = self.jobs_df

        # __________ Apply agency filters __________
        # Get selection from listbox
        selected_indices = self.agency_listbox.curselection()
        selected_agencies = [self.agency_listbox.get(i) for i in selected_indices]

        if selected_agencies:
            filtered_df = timeframe_df[timeframe_df["agency"].isin(selected_agencies)]
        else:
            filtered_df = timeframe_df

        # Update results displayed using filters
        self.update_results(filtered_df)

    def populate_agency_list(self):
        agencies = sorted(self.jobs_df["agency"].dropna().unique())
        for agency in agencies:
            self.agency_listbox.insert(tk.END, agency)

    # _________________ CLEAR FILTERS _________________ #
    def clear_filters(self):
        # Clear radio button selection (set to dummy button value)
        self.radio_selection.set("none")

        # Clear all agency selections
        self.agency_listbox.select_clear(0, tk.END)
        
        # Update results with original dataframe
        self.update_results(self.jobs_df)

    # _________________ SETUP LINK _________________ #
    def open_url(self, event=None):
        region = self.results_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.results_tree.identify_column(event.x)
        item = self.results_tree.identify_row(event.y)

        # URL column is column #4
        if column == "#4" and item:
            tags = self.results_tree.item(item, "tags")
            url = tags[0]  # first tag is the URL
            webbrowser.open_new_tab(url)


    # _________________ TIME FILTER METHODS _________________
    def get_last_24_hours(self):
        last_24h = self.jobs_df[self.jobs_df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('24h')]
        return last_24h

    def get_last_7_days(self):
        last_7d = self.jobs_df[self.jobs_df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('7d')]
        return last_7d

    def get_last_30_days(self):
        last_month = self.jobs_df[self.jobs_df['posting_date'] >= pd.Timestamp.now() - pd.Timedelta('30d')]
        return last_month

# _________________ MAIN _________________ #
if __name__ == "__main__":
    root = tk.Tk()
    app = CityJobsApp(root)
    root.mainloop()