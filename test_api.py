import requests

API_KEY = "0b0ea324c3e482e035770aa4392b5b82"
city = "Delhi"

url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

response = requests.get(url)
print("Status Code:", response.status_code)
print("Response:", response.json())
