import requests
import urllib.parse

BASE_URL = "https://api.sonicscan.org/api"
params = {
    "module": "account",
    "action": "tokentx",
    "contractaddress": "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38",
    "address": "0x87f16c31e32ae543278f5194cf94862f1cb1eee0",
    "page": "1",
    "offset": "100",
    "startblock": "0",
    "endblock": "27025780",
    "sort": "asc",
    "apikey": ""
}

# Construct the request URL
url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
print("API URL:", url)  # Check if this matches the working URL in the browser

# Make the request with a User-Agent header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}
response = requests.get(url, headers=headers)

print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())
