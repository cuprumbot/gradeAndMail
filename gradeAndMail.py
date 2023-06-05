import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError
import csv



# Web3 (remove for MOOCs other than Blockchain and Cryptocurrency)
from web3 import Web3



debug = True
sendMails = not debug



# Gmail API

# Enable Gmail API: https://console.cloud.google.com/apis/library/gmail.googleapis.com
# Create OAuth credentials: https://console.cloud.google.com/apis/credentials/oauthclient
#       (Desktop app, create and download JSON secret)
# Make sure OAuth is enabled: https://console.cloud.google.com/apis/credentials/consent
#       (Verification not required, In production)

# When running, it will open a browser and ask for permission to access your account
# Since the app is not verified, it is normal to get a "Google hasn’t verified this app" message
# Just dismiss it and give permissions

# About quotas: https://developers.google.com/gmail/api/reference/quota

SCOPES = [ "https://www.googleapis.com/auth/gmail.send" ]
if sendMails:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)

'''
    args:
    to          recipient email
    subject     subject of the mail to send
    body        content of the mail to send
'''
def sendSingleMail (to, subject, body):
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)      # change this if you need something more than plain text, https://docs.python.org/3/library/email.mime.html
    message['to'] = to
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'Sent message: {message}\nMessage Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None

#sendSingleMail("recipient@gmail.com", "API test", "Uno\nDos\nTres")



# CSV
'''
    args:
    filename    name of the file to open
    mailCol     number of column where the email address is located
    dataCol     number of coulmn where the data is located
'''
def readCSVFile (filename, mailCol=0, dataCol=1):
    mailAndData = {}    # dict with email address as key and submision data as value, will care only about last submision

    with open(filename, 'r') as file:
      csvreader = csv.reader(file)
      next(csvreader, None)    # skip header

      for row in csvreader:
        mail = row[mailCol]
        data = row[dataCol]
        mailAndData[mail] = data

    return mailAndData



# Web3 (remove for MOOCs other than Blockchain and Cryptocurrency)
w3 = Web3(Web3.HTTPProvider("https://YOUR-TESTNET-HERE.infura.io/v3/YOUR-ID-HERE"))

def transactionGrader (hash):
    try:
        result = w3.eth.get_transaction(hash)           # get transaction from hash
        value = result['value']                         # get sent value
        valueInEther = Web3.from_wei(value, 'ether')    # the value is expressed in wei, convert to eth
        return str(valueInEther)
    except Exception as e:
        print(e)
        return "Unexpected result"



# :)
def dummyGrader (data):
    return data + " :)"



'''
    args:
    subject     subject of the mail with the results, will use the same subject for all the mails
    grader      FUNCTION that will be called with the submission as argument, should return a string
    filename    name of the file to open
    mailCol     number of column where the email address is located
    dataCol     number of coulmn where the data is located
'''
def gradeAndSendMails (subject, grader, filename, mailCol=0, dataCol=0):

    mailAndData = readCSVFile(filename, mailCol, dataCol)       # read all mails and their submissions from file

    for (mail, data) in mailAndData.items():
        result = grader(data)                                   # call the grader function
        print("\nmail:", mail, "\nresult:", result)
        if sendMails:
            sendSingleMail(mail, subject, result)

gradeAndSendMails("Dummy grader test", dummyGrader, "./fileinput.csv", 0, 1)
#gradeAndSendMails("Transaction grader test", transactionGrader, "./fileinput.csv", 0, 1)