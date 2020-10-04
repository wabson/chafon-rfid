import os.path
import pickle
import socket
import threading
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from googleapiclient.errors import HttpError
from http.client import HTTPException
from httplib2 import Http, ServerNotFoundError

SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
TIMES_RANGE_NAME = 'Chip Finishes!A1:D1'

class GoogleSheetAppender(threading.Thread):

    def __init__(self, spreadsheet_id):
        threading.Thread.__init__(self)
        self.__row_data = []
        self.__spreadsheet_id = spreadsheet_id
        self.__commit_count = 0
        self.running = True

    def run(self):
        while(self.running):
            self.__append_spreadsheet_values()
            time.sleep(5)

    def add_row(self, row_values):
        self.__row_data.append(row_values)

    def __append_spreadsheet_values(self):

        spreadsheet_values = self.__row_data[self.__commit_count:]
        if len(spreadsheet_values) == 0:
            return

        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_console()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        try:
            service = build('sheets', 'v4', credentials=creds)
            sheet = service.spreadsheets()
            value_input_option = 'USER_ENTERED'
            insert_data_option = 'INSERT_ROWS'
            value_range_body = {
                    'range': TIMES_RANGE_NAME,
                    'majorDimension': 'ROWS',
                    'values': spreadsheet_values
                    }
            request = sheet.values().append(spreadsheetId=self.__spreadsheet_id, range=TIMES_RANGE_NAME, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
            response = request.execute()
            rows_added = response.get('updates').get('updatedRows')
            self.__commit_count += rows_added
            print('{0} rows updated'.format(rows_added))
        except HttpError as err:
            if err.resp.status in [403, 404, 500, 503]:
                print('Error appending spreadsheet values: %s' % (err.resp.status,))
            else:
                raise
        except (HTTPException, ServerNotFoundError, socket.error) as err:
            print('Could not append spreadsheet values')