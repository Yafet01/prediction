import requests

url = 'http://127.0.0.1:5000/predict'
data = {
    'Year': 2024,
    'Month': 1,
    'Fever': False,
    'Malaria': True,
    'Pain': False,
    'Dry Season': False,
    'Wet Season': True,
    'Back Pain': False,
    'Common Cold': False,
    'Falciparum': True,
    'Headache': False,
    'Influenza': False,
    'Migraine': False,
    'Vivax': False
}

response = requests.post(url, json=data)
print(response.json())
