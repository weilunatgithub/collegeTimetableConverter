from datetime import date, timedelta, datetime
import requests 
from bs4 import BeautifulSoup

from googleapiclient.discovery import build 
from google.oauth2 import service_account
import os.path 

def get_week_start() -> date: 
    today = date.today()
    num_days_until_next_week = 7 - today.weekday()
    next_week_start = today + timedelta(days=num_days_until_next_week)
    return next_week_start

def fetch_time_table(week, intake_code, intake_group): 
    # https://api.apiit.edu.my/timetable-print/index.php?Week=2025-04-28&Intake=APU2F2411SE&Intake_Group=All&print_request=print_tt
    response = requests.get(f"https://api.apiit.edu.my/timetable-print/index.php?Week={week}&Intake={intake_code}&Intake_Group={intake_group}&print_request=print_tt") # return API response 
    soup = BeautifulSoup(response.text, "html.parser") # return webpage source 
    return soup.find("table", class_ ="table") # find the first occurence of "table" TAG with CLASS ATTRIBUTE "table"

def get_credentials(SCOPES): 
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'service_account.json')

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes = SCOPES
    )
    return creds


def create_event(service, entry): 
    calendarId = "168e05e968d4ed7c92c56a1328a5e25285cbfd9b3fcd6e55f9f51975cbb98feb@group.calendar.google.com"
    date_str = entry['Date']
    time_str = entry['Time']

    date = datetime.strptime(date_str, "%a, %d-%b-%Y")
    start_time_str, end_time_str = time_str.split("-")
    start_time = datetime.strptime(start_time_str.strip(), "%H:%M")
    end_time = datetime.strptime(end_time_str.strip(), "%H:%M")
    start_datetime = date.replace(hour = start_time.hour, minute= start_time.minute)
    end_datetime = date.replace(hour = end_time.hour, minute= end_time.minute)

    # ISO conversion of datetime format
    start_isoformat = start_datetime.isoformat()
    end_isoformat = end_datetime.isoformat()

    # Refer to the Python quickstart on how to setup the environment:
    # https://developers.google.com/workspace/calendar/quickstart/python
    # Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
    # stored credentials.
    
    event = {
        'summary': f"{entry['Subject/Module']}",
        'location': f"{entry['Classroom']}",
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': f"{start_isoformat}",# '2015-05-28T09:00:00-07:00'
            'timeZone': 'America/Los_Angeles',
        },

        'end': {
            'dateTime': f"{end_isoformat}", #2015-05-28T17:00:00-07:00',
            'timeZone': 'Asia/Kuala_Lumpur',
        },
    }

    event = service.events().insert(calendarId= calendarId, body=event).execute()
    return event 
    # print 'Event created: %s' % (event.get('htmlLink'))
 

    
def main(): 
    intake = "APU2F2411SE"
    intake_group ="G1" 
    remove_list = [""] # to filter the elective modules     
    week_start = get_week_start()

    timetable_table = fetch_time_table(week_start, intake, intake_group= intake_group)

    if timetable_table: # check the truthy value 
        timetable_data = [] 
        rows = timetable_table.find_all("tr")#[2:] # to ignore the first 2 "tr" tag contents (headers)
        print(rows)

        if rows: 
            for row in rows: 
                cells = row.find_all("td")

                date = cells[0].text.strip() 
                time = cells[1].text.strip() 
                classroom = cells[2].text.strip() 
                location = cells[3].text.strip() 
                subject = cells[4].text.strip() 
                lecturer = cells[5].text.strip() 

                module_name = subject.split("-")[3]

                if module_name not in remove_list: 
                    timetable_data.append({
                        "Date" : date, 
                        "Time" : time, 
                        "Classroom" : classroom, 
                        "Location" : location, 
                        "Subject/Module" : subject, 
                        "Lecturer" : lecturer, 
                    })

if __name__ == "__main__": 
    main()

# print(type(get_week_start()))
# print(type(fetch_time_table(get_week_start(), "APU2F2411SE", "G1")))

