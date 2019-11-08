import socket
import threading

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from httplib import HTTPException
from httplib2 import Http, ServerNotFoundError
from oauth2client import file, client, tools

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

        store = file.Storage('google-token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('google-credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        try:
            service = build('sheets', 'v4', http=creds.authorize(Http()))
            sheet = service.spreadsheets()
            value_input_option = 'USER_ENTERED'
            insert_data_option = 'INSERT_ROWS'
            value_range_body = {
                    'range': TIMES_RANGE_NAME,
                    'majorDimension': 'ROWS',
                    'values': spreadsheet_values
                    }
            request = service.spreadsheets().values().append(spreadsheetId=self.__spreadsheet_id, range=TIMES_RANGE_NAME, valueInputOption=value_input_option, insertDataOption=insert_data_option, body=value_range_body)
            response = request.execute()
            rows_added = response.get('updates').get('updatedRows')
            self.__commit_count += rows_added
            print('{0} rows updated'.format(rows_added))
        except HttpError as err:
            if err.resp.status in [403, 404, 500, 503]:
                print 'Error appending spreadsheet values: %s' % (err.resp.status,)
            else:
                raise
        except (HTTPException, ServerNotFoundError, socket.error) as err:
            print 'Could not append spreadsheet values'