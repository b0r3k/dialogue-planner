# How to get the API working
- `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`
- the credentials are in the repository
- log in and grant permission, possibly request access to the test project
### When first creating the project
- in Google Cloud Platform create a project
- add the used APIs
- set up the OAuth consent screen, add users to testing
- generate the credentials, download them
- use the credentials, log in, grant permissions -> generate token

# Useful stuff from the Calendar API

## Building the service
```python
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('hw7/token.json'):
        creds = Credentials.from_authorized_user_file('hw7/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'hw7/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('hw7/token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
```

## Getting the list of events following some criteria
```python
events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime', q="test").execute()
events = events_result.get('items', [])
```

Note the `q=""` parameter allowing full-text search.

Each item has:

```python
kind = calendar#event
etag = "3238840170066000"
id = 40mvtfam5rb2jm4b86johmlulq
status = confirmed
htmlLink = https://www.google.com/calendar/event?eid=NDBtdnRmYW01cmIyam00Yjg2am9obWx1bHEgbGVnb2xhc29jemVAbQ
created = 2021-04-26T06:54:45.000Z
updated = 2021-04-26T06:54:45.033Z
summary = test
creator = {'email': 'legolasocze@gmail.com', 'self': True}
organizer = {'email': 'legolasocze@gmail.com', 'self': True}
start = {'dateTime': '2021-04-27T09:30:00+02:00'}
end = {'dateTime': '2021-04-27T10:30:00+02:00'}
iCalUID = 40mvtfam5rb2jm4b86johmlulq@google.com
sequence = 0
reminders = {'useDefault': True}
eventType = default
```
Especially important part is the `eventid` - most of the other functions take that as an argument.

[More info]( https://developers.google.com/calendar/v3/reference/events/list ) 

## [Adding new event]( https://developers.google.com/calendar/v3/reference/events/insert )

## [Updating an event]( https://developers.google.com/calendar/v3/reference/events/update )

## [Deleting an event]( https://developers.google.com/calendar/v3/reference/events/delete )