import os
import re
import pandas as pd
import datetime


# Find matching files Publications

def load_publications():
    directory = "Data backup"
    file_pattern = r"^Publications_\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?\.csv$"
    matching_files = []
    for filename in os.listdir(directory):
        if re.match(file_pattern, filename):
            matching_files.append(filename)
    if not matching_files:
        # No files found, create a new DataFrame
        PUBLICATIONS_DF = pd.DataFrame(columns=["PubID", "Ticket", "Name", "Platform", "Assignee", 
                                            "Start Date", "Feature Flag", "Planned Sites", 
                                            "Planned Devices", "Planned Genders", "Planned Languages", "Current Status", "Analytics"])
    else:
        # Files found, find the latest one
        matching_files.sort(
                            key=lambda x: datetime.datetime.strptime(
                                    re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x).group(1), "%Y-%m-%d %H:%M:%S"
                                                                    )
                            )
        latest_file = matching_files[-1]  # Get the most recent file

        PUBLICATIONS_DF = pd.read_csv(os.path.join(directory, latest_file)).fillna("").sort_values('PubID')
    return PUBLICATIONS_DF

def save_publications(df):
    directory = "Data backup"
    file_name = f"Publications_{datetime.datetime.now()}"
    def make_clickable(val, url):
        return f"[{val}]({url})"

    df['Publication'] = df.apply(lambda row: make_clickable(row['Name'], row['Ticket']), axis=1)
    pd.DataFrame(data = formal_lists(df.fillna("").to_dict('records'))).to_csv(f"{directory}/{file_name}.csv", index=False)
    
    
# Find matching files  Publication_statuses

def load_statuses():
    directory = "Data backup"
    file_pattern = r"Publication_statuses_\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?\.csv$"

    matching_files = []
    for filename in os.listdir(directory):
        if re.match(file_pattern, filename):
            matching_files.append(filename)

    if not matching_files:
        # No files found, create a new DataFrame
        STATUS_DF = pd.DataFrame(columns=["PubID", "StatusID", "Action", "Date", "Sites", 
                                       "Devices", "Genders", "Languages", "Comment"])

    else:
        # Files found, find the latest one
        matching_files.sort(
                            key=lambda x: datetime.datetime.strptime(
                                    re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x).group(1), "%Y-%m-%d %H:%M:%S"
                                                                    )
                            )

        latest_file = matching_files[-1]  # Get the most recent file

        STATUS_DF = pd.read_csv(os.path.join(directory, latest_file)).fillna("").sort_values(['PubID', 'StatusID'])
        
    return STATUS_DF

def save_statuses(df):
    directory = "Data backup"
    file_name = f"Publication_statuses_{datetime.datetime.now()}"
    pd.DataFrame(data = formal_lists(df.fillna("").sort_values('PubID').to_dict('records'))).to_csv(f"{directory}/{file_name}.csv", index=False)


# ["PubID", "Ticket", "Name", "Platform", "Assignee", 
#                                             "Start Date", "Feature Flag", "Planned Sites", 
#                                             "Planned Devices", "Planned Genders", "Planned Languages"]
# Add new publication 
def add_publication(Name, Ticket, Platform, Assignee, Start_Date, Feature_Flag, Planned_Sites, Planned_Devices, Planned_Genders, Planned_Languages):
    publications_df = load_publications()
    
    ID = max(publications_df.PubID)+1 if len(publications_df) > 0 else 0
   
    
    if Platform == 'Retention':
        Feature_Flag = False
    elif Platform == 'Hard-coded':
        if Feature_Flag != True:
            Feature_Flag = False
    
    if Start_Date == '':
        Start_Date = None
        
    Current_status = "Planned"
    
    publications_df = pd.concat([
        publications_df, 
        pd.DataFrame(data=[[ID, Ticket, Name, Platform, Assignee, Start_Date,
                           Feature_Flag, Planned_Sites, Planned_Devices,
                           Planned_Genders, Planned_Languages, Current_status, None, None]],
                     columns=["PubID", "Ticket", "Name", "Platform", "Assignee", 
                               "Start Date", "Feature Flag", "Planned Sites", 
                                "Planned Devices", "Planned Genders", 
                              "Planned Languages", "Current Status", "Analytics", "Publication"] )
    ], ignore_index=True)
    

    def make_clickable(val, url):
        return f"[{val}]({url})"

    publications_df['Publication'] = publications_df.apply(lambda row: make_clickable(row['Name'], row['Ticket']), axis=1)
    
    save_publications(publications_df.fillna(""))
            
            
    
# Update publications 
def update_publications(data):
    publications_df = load_publications()
    df = pd.DataFrame(data=data)
    publications_df = publications_df[~publications_df.PubID.isin(df.PubID.unique())]
    publications_df = pd.concat([publications_df,
                                 df]
                                , ignore_index=True)
    
    save_publications(publications_df)
    return publications_df



# format in publications
def formal_lists(data: dict):
    pattern = r"^\['[^']*'(?:, '[^']*')*\]$"
    for row in range(len(data)):
        for column in data[row]:
            if column in ("Planned Sites", "Planned Devices", "Planned Languages"):
                input_string = data[row][column]
                if re.match(pattern, input_string):
                    formatted_string = input_string.strip("[]").replace("'", "").replace(", ", ",").replace(",", ", ")
                    data[row][column] = formatted_string
                    print(formatted_string)
    return data
    
    