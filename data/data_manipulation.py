import os
import re
import pandas as pd
import datetime
import data.dropdowns as dd
from dash import html
from typing import Dict, List

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
                                    re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x).group(1) if re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x) else "", 
                                    "%Y-%m-%d %H:%M:%S"
                                                                    )
                            )
        latest_file = matching_files[-1]  # Get the most recent file

        PUBLICATIONS_DF = pd.read_csv(os.path.join(directory, latest_file)).fillna("").sort_values('PubID')
        PUBLICATIONS_DF['Feature Flag'] = PUBLICATIONS_DF['Feature Flag'].astype(str)
    return PUBLICATIONS_DF

def save_publications(df):
    directory = "Data backup"
    file_name = f"Publications_{datetime.datetime.now()}"
    def make_clickable(val, url, ID):
        return f"[{val} (ID:{ID})]({url})"
    df['Feature Flag'] = df['Feature Flag'].astype(str)
    df.loc[(df['Feature Flag'].isna()) | (df['Feature Flag'] == '') | (df['Feature Flag'] != 'True'), 'Feature Flag'] = 'False'
    df['Publication'] = df.apply(lambda row: make_clickable(row['Name'], row['Ticket'], row['PubID']), axis=1)
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
                                    re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x).group(1) if re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", x) else "", 
                                    "%Y-%m-%d %H:%M:%S"
                                                                    )
                            )

        latest_file = matching_files[-1]  # Get the most recent file

        STATUS_DF = pd.read_csv(os.path.join(directory, latest_file)).fillna("").sort_values(['PubID', 'Date'])
        
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
    # print('Save publication')
    print(df)
    if len(df) > 0:
        table_data, is_error_open, is_error_msg = is_null_inserted(data, publications_df[publications_df.PubID.isin(df.PubID.unique())].to_dict('records'), ['Name', 'Ticket', 'Platform', 'Planned Sites', 'Planned Devices', 'Planned Genders', 'Planned Languages'])
        df = pd.DataFrame(data=table_data)
        # print('Error open: ', is_error_open)
        # print('Error msg: ', is_error_msg)
    else:
        is_error_open = False
        is_error_msg = ""

    publications_df = publications_df[~publications_df.PubID.isin(df.PubID.unique())]
    publications_df = pd.concat([publications_df,
                                 df]
                                , ignore_index=True)
    
    save_publications(publications_df)
    return publications_df, is_error_open, is_error_msg



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
    return data
    
    
# Add these functions to the existing file

def format_list_value(value):
    """Convert list or string list to comma-separated string"""
    if isinstance(value, list):
        return ", ".join(list(set(value)))
    elif isinstance(value, str):
        if value.startswith('['):
            # Convert string representation of list to comma-separated string
            return value.strip("[]'").replace("'", "").replace(", ", ", ")
    return value if value else ''

def add_status(pub_id, status, date, sites, devices, genders, languages, comment):
    """Add a new status for a publication"""
    # Load current statuses
    statuses_df = load_statuses()
    
    # Get the next StatusID for this publication
    pub_statuses = statuses_df[statuses_df['PubID'] == int(pub_id)]
    next_status_id = 0 if pub_statuses.empty else pub_statuses['StatusID'].max() + 1
    
    # Format list values
    def format_list_value(value):
        if isinstance(value, (list, str)):
            if isinstance(value, str) and value.startswith('['):
                # Convert string representation of list to comma-separated string
                return value.strip("[]'").replace("'", "").replace(", ", ", ")
            elif isinstance(value, list):
                # Convert list to comma-separated string
                return ", ".join(list(set(value)))
                
        return value if value else ''
    
    # Create new status entry with formatted values
    new_status = {
        'PubID': int(pub_id),
        'StatusID': next_status_id,
        'Action': status,
        'Date': date,
        'Sites': format_list_value(sites),
        'Devices': format_list_value(devices),
        'Genders': format_list_value(genders),
        'Languages': format_list_value(languages),
        'Comment': comment if comment else ''
    }
    
    # Add new status to DataFrame
    statuses_df = pd.concat([
        statuses_df,
        pd.DataFrame([new_status])
    ], ignore_index=True)
    
    # Save updated statuses
    save_statuses(statuses_df)
    
    # Update publication's current status
    publications_df = load_publications()
    publications_df.loc[publications_df['PubID'] == int(pub_id), 'Current Status'] = status
    save_publications(publications_df)
    
    return True

def update_status(pub_id, new_statuses, dev_view = False):
    """
    Update statuses for a publication by replacing all its existing statuses with new ones.
    
    Args:
        pub_id (int): Publication ID
        new_statuses (list): List of dictionaries containing the new status records
    
    Returns:
        bool: True if update successful
    """
    # Load current statuses
    statuses_df = load_statuses()
    
    # Define the expected columns for the status table
    status_columns = ["PubID", "StatusID", "Action", "Date", "Sites", 
                     "Devices", "Genders", "Languages", "Comment"]
    
    # Remove all existing statuses for this publication
    statuses_df = statuses_df[statuses_df['PubID'] != int(pub_id)]
    
    # Add new statuses if any exist
    if new_statuses:
        # Convert new statuses to DataFrame and ensure proper formatting
        new_df = pd.DataFrame(new_statuses)
        
        new_df['Sites'] = new_df['Sites'].apply(format_list_value)
        new_df['Devices'] = new_df['Devices'].apply(format_list_value)
        new_df['Genders'] = new_df['Genders'].apply(format_list_value)
        new_df['Languages'] = new_df['Languages'].apply(format_list_value)

        # Keep only the required columns
        new_df = new_df[new_df['PubID'] == int(pub_id)][status_columns]
        if dev_view:
            df = load_statuses()
            old_statuses = df[df['PubID'] == int(pub_id)]
            new_df = pd.concat([old_statuses, new_df], ignore_index=True)

        # Combine with existing statuses
        statuses_df = pd.concat([statuses_df, new_df], ignore_index=True)
    
    # Save updated statuses
    save_statuses(statuses_df)


def get_publication_statuses(pub_id=None, platform=None, assignee=None, status=None):
    """Get filtered status history with publication details"""
    statuses_df = load_statuses()
    publications_df = load_publications()
    
    # Join statuses with publications
    filtered_df = pd.merge(
        publications_df,
        statuses_df,
       
        on='PubID',
        how='left'
    )
    
    # Apply filters
    if pub_id is not None:
        filtered_df = filtered_df[filtered_df['PubID'] == int(pub_id)]
    if platform is not None:
        filtered_df = filtered_df[filtered_df['Platform'].fillna('') == platform]
    if assignee is not None:
        filtered_df = filtered_df[filtered_df['Assignee'].fillna('') == assignee]
    if status is not None:
        filtered_df = filtered_df[filtered_df['Action'].fillna('') == status]
    
    # Sort by date and StatusID
    return filtered_df.sort_values(['PubID', 'Date', 'StatusID'], ascending=[True, True, True])
    

    
    
def expand_sites_options(planned_sites, platform, extra_values=None):
    """
    Expands sites abbreviations into full list based on platform.
    Returns a sorted list with abbreviations first, followed by individual options.
    
    Args:
        planned_sites (str): Comma-separated string of planned sites
        platform (str): 'Hard-coded' or 'Retention' for platform-specific options
        
    Returns:
        list: Sorted list of sites with abbreviations first
    """
    if not planned_sites and not extra_values:
        return []
    elif not planned_sites and extra_values:
        return extra_values
    
    sites = set(planned_sites.split(', '))
    expanded_sites = set()  # Using set for faster lookups and automatic deduplication
    abbreviations = {'All', 'Core CM', 'ELC+SLC'}  # Use set literal syntax
    is_all = False
    # First pass: collect abbreviations and their expansions
    for site in sites:
        if site == 'ELC+SLC':
            expanded_sites.update(dd.SITE_ELC_SLC_OPTIONS)
        elif site == 'Core CM':
            expanded_sites.update(dd.SITE_CORE_CM_DEVS_OPTIONS if platform == 'Hard-coded' 
                                else dd.SITE_CORE_CM_RETENTION_OPTIONS)
        elif site == 'All':
            expanded_sites.update(dd.SITE_ALL_DEVS_OPTIONS if platform == 'Hard-coded' 
                                else dd.SITE_ALL_RETENTION_OPTIONS)
            is_all = True
        else:
            expanded_sites.add(site)
    # print(f'expanded_sites: {expanded_sites}')
    # Split into abbreviations and other sites
    if is_all:
        sites.update(abbreviations)
    abbr_sites = sorted(set(sites) & set(abbreviations))  # Keep original abbreviations
    other_sites = sorted(expanded_sites - set(abbreviations))  # All other sites
    
    return abbr_sites + other_sites + extra_values if extra_values else abbr_sites + other_sites

def expand_devices_options(planned_devices, extra_values=False):
    """
    Expands devices abbreviations into full list.
    Returns a sorted list with abbreviations first, followed by individual options.
    
    Args:
        planned_devices (str): Comma-separated string of planned devices
        
    Returns:
        list: Sorted list of devices with abbreviations first
    """
    if not planned_devices and not extra_values:
        return []
    elif not planned_devices and extra_values:
        return extra_values
    
    devices = set(planned_devices.split(', '))
    expanded_devices = set()  # Using set for faster lookups and automatic deduplication
    abbreviations = {'All', 'Web', 'App'}
    is_all = False
    # First pass: collect abbreviations and their expansions
    for device in devices:
        if device == 'All':
            expanded_devices.update(dd.DEVICE_ALL_OPTIONS)
            is_all = True
        elif device == 'Web':
            expanded_devices.update(dd.DEVICE_WEB_OPTIONS)
        elif device == 'App':
            expanded_devices.update(dd.DEVICE_APP_OPTIONS)
        else:
            expanded_devices.add(device)
    
    # Split into abbreviations and other devices
    if is_all:
        devices.update(abbreviations)
    abbr_devices = sorted(set(devices) & set(abbreviations))  # Keep original abbreviations
    other_devices = sorted(expanded_devices - set(abbreviations))  # All other devices
    
    return abbr_devices + other_devices + extra_values if extra_values else abbr_devices + other_devices

def expand_languages_options(planned_languages, extra_values=None):
    """
    Expands languages abbreviations into full list.
    Returns a sorted list with abbreviations first, followed by individual options.
    
    Args:
        planned_languages (str): Comma-separated string of planned languages
        
    Returns:
        list: Sorted list of languages with abbreviations first
    """
    if not planned_languages and not extra_values:
        return []
    elif not planned_languages and extra_values:
        return extra_values
        
    languages = set(planned_languages.split(', '))
    expanded_languages = set()  # Using set for faster lookups and automatic deduplication
    abbreviations = {'All', 'Main Languages (39)', 'Main Languages (25)'}
    is_all = False
    # First pass: collect abbreviations and their expansions
    for lang in languages:
        if lang == 'All':
            expanded_languages.update(dd.LANGUAGE_OPTIONS)
            is_all = True
        elif lang == 'Main Languages (39)':
            expanded_languages.update(dd.LANGUAGE_MAIN_LANGUAGES_39_OPTIONS)
        elif lang == 'Main Languages (25)':
            expanded_languages.update(dd.LANGUAGE_MAIN_LANGUAGES_25_OPTIONS)
        else:
            expanded_languages.add(lang)
    
    # Split into abbreviations and other languages
    if is_all:
        languages.update(abbreviations)
    abbr_languages = sorted(set(languages) & set(abbreviations))  # Keep original abbreviations
    other_languages = sorted(expanded_languages - set(abbreviations))  # All other languages
    
    return abbr_languages + other_languages + extra_values if extra_values else abbr_languages + other_languages

def expand_genders_options(planned_genders, extra_values=None):
    """
    Expands genders abbreviations into full list.
    Returns a sorted list with abbreviations first, followed by individual options.
    
    Args:
        planned_genders (str): Comma-separated string of planned genders
        
    Returns:
        list: Sorted list of genders with abbreviations first
    """
    if not planned_genders and not extra_values:
        return []
    elif not planned_genders and extra_values:
        return extra_values
        
    genders = planned_genders.split(', ')
    expanded_genders = set()  # Using set for faster lookups and automatic deduplication
    abbreviations = ['All']
    
    # First pass: collect abbreviations and their expansions
    for gender in genders:
        if gender == 'All':
            expanded_genders.update(dd.GENDER_ALL_OPTIONS)
        else:
            expanded_genders.add(gender)
    
    # Split into abbreviations and other genders
    abbr_genders = sorted(set(genders) & set(abbreviations))  # Keep original abbreviations
    other_genders = sorted(expanded_genders - set(abbreviations))  # All other genders
    
    return abbr_genders + other_genders + extra_values if extra_values else abbr_genders + other_genders
    
    
def get_platform_options(publications_df, filters=None):
    """
    Get platform options from publications DataFrame with optional filtering.
    
    Args:
        publications_df (pd.DataFrame): Publications DataFrame
        filters (dict, optional): Dictionary of filters to apply. Example:
            {
                'Platform': 'Hard-coded',
                'Assignee': 'John Doe',
                'Current Status': 'Planned'
            }
        
    Returns:
        list: List of platform option dictionaries
    """
    df = apply_filters(publications_df, filters)
    return [
        {'label': x, 'value': x} 
        for x in sorted(df['Platform'].unique())
        if pd.notna(x)
    ]

def get_assignee_options(publications_df, filters=None):
    """
    Get assignee options from publications DataFrame with optional filtering.
    
    Args:
        publications_df (pd.DataFrame): Publications DataFrame
        filters (dict, optional): Dictionary of filters to apply
        
    Returns:
        list: List of assignee option dictionaries
    """
    df = apply_filters(publications_df, filters)
    return [
        {'label': x, 'value': x} 
        for x in sorted(df['Assignee'].unique())
        if pd.notna(x)
    ]

def get_publication_options(publications_df, filters=None):
    """
    Get publication options from publications DataFrame with optional filtering.
    
    Args:
        publications_df (pd.DataFrame): Publications DataFrame
        filters (dict, optional): Dictionary of filters to apply
        
    Returns:
        list: List of publication option dictionaries
    """
    df = apply_filters(publications_df, filters)
    return [
        {'label': f"{row['Name']} (ID: {row['PubID']})", 
         'value': str(row['PubID'])}
        for _, row in df.iterrows()
        if pd.notna(row['Name'])
    ]

def get_status_options(publications_df, filters=None, platform=None):
    """
    Get status options from publications DataFrame with optional filtering.
    
    Args:
        publications_df (pd.DataFrame): Publications DataFrame
        filters (dict, optional): Dictionary of filters to apply
        platform (str, optional): Platform type to get specific status options
            - If 'Hard-coded': returns STATUS_DEVS_FLAG_OPTIONS or STATUS_DEVS_NO_FLAG_OPTIONS
            - If 'Retention': returns STATUS_RETENTION_OPTIONS
            - If None: returns unique statuses from DataFrame
        
    Returns:
        list: List of status option dictionaries
    """
    if platform:
        if platform == 'Hard-coded':
            # Check if feature flag exists in filters
            has_flag = filters.get('Feature Flag', '').lower() == 'True' if filters else False
            statuses = dd.STATUS_DEVS_FLAG_OPTIONS if has_flag else dd.STATUS_DEVS_NO_FLAG_OPTIONS
        else:  # Retention
            statuses = dd.STATUS_RETENTION_OPTIONS
        return [{'label': x, 'value': x} for x in statuses]
    
    # If no platform specified, get from DataFrame
    df = apply_filters(publications_df, filters)
    return [
        {'label': x, 'value': x} 
        for x in sorted(df['Current Status'].unique())
        if pd.notna(x)
    ]

def apply_filters(df, filters):
    """
    Apply filters to DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame to filter
        filters (dict, optional): Dictionary of filters to apply
            Example: {'Platform': 'Hard-coded', 'Assignee': 'John Doe'}
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if not filters:
        return df
    
    filtered_df = df.copy()
    for column, value in filters.items():
        if value:
            if isinstance(value, list):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df
    
def card_content_insert(parameters, pub_info):
        lst = [html.H4("Publication Details", className="mb-3")]
        # print(f'pub_info: {pub_info}')
        for parameter in parameters:
            if parameter == 'Name':
                lst.append(html.Div([
                                    html.Strong("Name: "),
                                    html.Span(pub_info['Name'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Platform':
                lst.append(html.Div([
                                    html.Strong("Platform: "),
                                    html.Span(pub_info['Platform'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Assignee':
                lst.append(html.Div([
                                    html.Strong("Assignee: "),
                                    html.Span(pub_info['Assignee'] if pd.notna(pub_info['Assignee']) and pub_info['Assignee'] != '' else 'Not set')]
                                    , className="mb-2")
                            )
            elif parameter == 'Start Date':
                lst.append(html.Div([
                                    html.Strong("Start Date: "),
                                    html.Span(pub_info['Start Date'] if pd.notna(pub_info['Start Date']) and pub_info['Start Date'] != '' else 'Not set')]
                                    , className="mb-2")
                            )
            elif parameter == 'Current Status':
                lst.append(html.Div([
                                    html.Strong("Current Status: "),
                                    html.Span(pub_info['Current Status'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Feature Flag':
                lst.append(html.Div([
                                    html.Strong("Feature Flag: "),
                                    html.Span("Yes" if pub_info['Feature Flag'] else "No")]
                                    , className="mb-2")
                            )
            elif parameter == 'Sites':
                lst.append(html.Div([
                                    html.Strong("Planned Sites: "),
                                    html.Span(pub_info['Planned Sites'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Devices':
                lst.append(html.Div([
                                    html.Strong("Planned Devices: "),
                                    html.Span(pub_info['Planned Devices'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Languages':
                lst.append(html.Div([
                                    html.Strong("Planned Languages: "),
                                    html.Span(pub_info['Planned Languages'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Genders':
                lst.append(html.Div([
                                    html.Strong("Planned Genders: "),
                                    html.Span(pub_info['Planned Genders'])]
                                    , className="mb-2")
                            )
            elif parameter == 'StatusID':
                lst.append(html.Div([
                                    html.Strong("StatusID: "),
                                    html.Span(pub_info['StatusID'])]
                                    , className="mb-2")
                            )
            elif parameter == 'Analytics':
                lst.append(html.Div([
                                    html.Strong("Analytics: "),
                                    html.Span(pub_info['Analytics'])]
                                    , className="mb-2")
                            )
        return lst

def date_validation(data, data_previous, col, empty = True):
     date_error_open = False
     date_error_msg = ""
     modified_row = []
     if type(col) == str:
         col = [col]
     for i, (curr_row, prev_row) in enumerate(zip(data, data_previous)):
        for c in col:
            # print(f'check date curr_row[c]: {curr_row[c]}')
            # print(f'check date prev_row[c]: {prev_row[c]}')
            
            if curr_row.get(c) != prev_row.get(c):
                modified_row.append(i)

     if len(modified_row) > 0:
        for i in modified_row:
            for c in col:
                print(f'check date data[i][c]: {data[i][c]}')
                try:
            
                    if data[i][c] != 'Excluded':
                        if (empty and data[i][c] is not None and data[i][c] != "") or (not empty and (data[i][c] is None or data[i][c] == "")):
                            datetime.datetime.strptime(data[i][c], '%Y-%m-%d')
                    

                except ValueError:                                                        
                    data[i][c] = data_previous[i][c]

                    date_error_open =  True
                    date_error_msg = "Invalid date format. Please use YYYY-MM-DD format."

     return data, date_error_open, date_error_msg

def is_null_inserted(data, data_previous, col):
     date_error_open = False
     date_error_msg = ""
     modified_row = []
     if type(col) == str:
         col = [col]
     for i, (curr_row, prev_row) in enumerate(zip(data, data_previous)):
        for c in col:
            # print(f'Column: {c}')
            # print(f'curr_row: {curr_row.get(c)}')
            # print(f'prev_row: {prev_row.get(c)}')
            if curr_row.get(c) != prev_row.get(c):
                modified_row.append(i)
    #  print(f'modified_rows: {modified_row}')
     if len(modified_row) > 0:
        for i in modified_row:
            for c in col:
                if col == 'Feature Flag':
                    print(f'data[i][c]: {data[i][c]}')
                if data[i][c] is None or data[i][c] == "":
                    data[i][c] = data_previous[i][c]
                    date_error_open = True
                    date_error_msg = "Null value inserted. The values are reverted."

     return data, date_error_open, date_error_msg

def get_site_statuses(publication, device, data):
        publications_df = load_publications()
        statuses_df = load_statuses()
        
        pub_details = publications_df[publications_df['PubID'] == int(publication)].iloc[0]

        

        stat_details = statuses_df[statuses_df['PubID'] == int(publication)].sort_values(['Date', 'StatusID'], ascending=[False, False])
        
        planned_sites = expand_sites_options(pub_details['Planned Sites'], pub_details['Platform']) if pub_details['Planned Sites'] else []
        has_feature_flag = pub_details['Feature Flag'] if pub_details['Feature Flag'] == 'True' else False
        planned_devices = expand_devices_options(pub_details['Planned Devices']) if pub_details['Planned Sites'] else []
                
        stat_details['List of Sites'] = stat_details['Sites'].apply(lambda i: ','.join(expand_sites_options(i, pub_details['Platform'])))
        stat_details['List of Devices'] = stat_details['Devices'].apply(lambda i: ','.join(expand_devices_options(i)))
        
        device_lst = expand_devices_options(device)
        statuses = {}

        for site in dd.SITE_ALL_DEVS_OPTIONS:
            device_statuses = []
            device_dates = []
            all_good = True
            planned = True if site in planned_sites else False
            for device_i in device_lst:
                last_status = stat_details[(stat_details['List of Sites'].str.contains(site)) & (stat_details['List of Devices'].str.contains(device_i))]
                if len(last_status) > 0:
                    device_statuses.append(last_status.Action.iloc[0])
                    device_dates.append(last_status.Date.iloc[0])
                else:
                    device_statuses.append(None)
                    device_dates.append(None)
                    all_good = False
            statuses[site] = [planned, all_good, device_statuses, device_dates]

        deployed = ['Deployed', "Expansion", 'Feature flag on', 'Roll Out']
        feature_flag = ['Feature flag on', 'Roll Out']
        new_data = []
        for data_i in data:
            new_data_i = data_i.copy()
            # print(f'data_i["site"]: {data_i["site"]}')
            # print(f'statuses[data_i["site"]][0]: {statuses[data_i["site"]][0]}')
            # print(f'has_feature_flag: {has_feature_flag}')
            if data_i['site'] in statuses.keys() and statuses[data_i['site']][0]:
                all_good, device_statuses, device_dates = statuses[data_i['site']][1:] # Fix
            
                if all_good:
                    if all(status in deployed for status in device_statuses):
                        new_data_i['code_deployed'] = 'True'
                        new_data_i['deployment_date'] = max(device_dates)
                    else:
                        new_data_i['code_deployed'] = 'False'
                        new_data_i['deployment_date'] = None

                    if all(status in feature_flag for status in device_statuses):
                        new_data_i['feature_flag'] = 'True'
                        new_data_i['feature_flag_date'] = max(device_dates)
                    else:
                        new_data_i['feature_flag'] = 'False'
                        new_data_i['feature_flag_date'] = None
                else:
                    new_data_i['code_deployed'] = 'False'
                    new_data_i['deployment_date'] = None
                    new_data_i['feature_flag'] = 'False'
                    new_data_i['feature_flag_date'] = None
            else:
                new_data_i['code_deployed'] = 'Excluded'
                new_data_i['deployment_date'] = 'Excluded'
                new_data_i['feature_flag'] = 'Excluded'
                new_data_i['feature_flag_date'] = 'Excluded'

            if not has_feature_flag:
                new_data_i['feature_flag'] = 'Excluded'
                new_data_i['feature_flag_date'] = 'Excluded'
            new_data.append(new_data_i)
            
        data = new_data.copy()
        # Add styling for feature flag columns if feature flag is off
        return data