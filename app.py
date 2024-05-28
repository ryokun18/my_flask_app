from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    company_names = [element.text for element in soup.find_all('div', class_='company-name')]
    email_addresses = [element.text for element in soup.find_all('div', class_='email-address')]
    return company_names, email_addresses

def authenticate_google_sheets(json_key):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
    client = gspread.authorize(creds)
    return client

def update_google_sheet(sheet_id, data):
    json_key = json.loads(os.environ.get('GOOGLE_SHEETS_JSON_KEY'))
    client = authenticate_google_sheets(json_key)
    sheet = client.open_by_key(sheet_id).sheet1
    for i, (company, email) in enumerate(data, start=2):
        sheet.update_cell(i, 1, company)
        sheet.update_cell(i, 2, email)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form['url']
    sheet_id = request.form['sheet_id']  # フォームの入力フィールド名を 'sheet_name' から 'sheet_id' に変更
    company_names, email_addresses = scrape_website(url)
    data = list(zip(company_names, email_addresses))
    update_google_sheet(sheet_id, data)
    return 'Data has been successfully scraped and updated in Google Sheet.'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
