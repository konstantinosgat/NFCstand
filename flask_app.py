from flask import Flask, redirect, request, abort
import gspread
from google.oauth2.service_account import Credentials
from urllib.parse import urlparse

app = Flask(__name__)

# Google Sheets authentication and access
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = "1YCyXH5R8Xg5LU0bk6pnEfgSgO9mebZ1I7UR1MhQPCmE"
sheet = client.open_by_key(sheet_id).sheet1  # Access the first sheet in the spreadsheet

def fetch_redirects():
    """
    Fetch redirects from Google Sheets on each request.
    """
    redirects = {}
    rows = sheet.get_all_values()  # Get all values from the sheet
    if not rows:
        return redirects

    header = rows[0]  # Assume the first row is the header
    for row in rows[1:]:  # Skip the header row
        if len(row) >= len(header):  # Ensure there are enough columns in the row
            route_number = str(row[header.index('Number')]).strip()
            target_url = row[header.index('Redirected Link')].strip()
            if route_number and target_url:  # Only add redirects with non-empty route numbers and URLs
                redirects[route_number] = normalize_url(target_url)
    return redirects

def normalize_url(url):
    """
    Normalize URLs to ensure they are in a standard format for redirection.
    """
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        # If no scheme, assume http
        url = f"http://{url}"
    return url

@app.route('/')
def home():
    return 'Welcome to My Flask App!'

@app.route('/<path:route_number>')
def dynamic_redirect(route_number):
    """
    Redirect based on the route number obtained from Google Sheets.
    """
    redirects = fetch_redirects()  # Fetch redirects from Google Sheets
    target_url = redirects.get(route_number)
    
    if target_url:
        return redirect(target_url)
    else:
        # If route_number is not found, return a 404 error or redirect to home
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
