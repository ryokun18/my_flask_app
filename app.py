from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    company_names = [element.text for element in soup.find_all('div', class_='company-name')]
    email_addresses = [element.text for element in soup.find_all('div', class_='email-address')]
    return company_names, email_addresses

def authenticate_google_sheets(json_keyfile):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client

def update_google_sheet(sheet_name, data):
    client = authenticate_google_sheets('path_to_your_json_keyfile.json')
    sheet = client.open(sheet_name).sheet1
    for i, (company, email) in enumerate(data, start=2):
        sheet.update_cell(i, 1, company)
        sheet.update_cell(i, 2, email)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    sheet_name = request.form['sheet_name']
    company_names, email_addresses = scrape_website(url)
    data = list(zip(company_names, email_addresses))
    update_google_sheet(sheet_name, data)
    return 'Data has been successfully scraped and updated in Google Sheet.'

if __name__ == '__main__':
    app.run(debug=True)
