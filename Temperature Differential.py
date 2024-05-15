import requests
import math
import datetime
import json

#This Script currently only working with cooling not heating

#Project info
PROJECT_ID = "YOUR PROJECT ID"
DEVICE_ID = "YOUR NEST DEVICE ID"
refresh_token = 'Refresh Token that obtained from Google APIs'
client_id = 'Google OAuth2 Client Id'
client_secret = 'Google OAuth2 Client Secret'
api_url = 'https://smartdevicemanagement.googleapis.com/v1'

# API endpoint format
GET_TEMPERATURE_ENDPOINT = "https://smartdevicemanagement.googleapis.com/v1/enterprises/{project_id}/devices/{device_id}"
SET_TEMPERATURE_ENDPOINT = "https://smartdevicemanagement.googleapis.com/v1/enterprises/{project_id}/devices/{device_id}:executeCommand"

def is_token_valid(access_token): #Check if acess token is expired or not
    url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
    try:
        response = requests.get(url)
        return response.status_code == 200 and response.json()['expires_in'] > 10
    except requests.RequestException as e:
        print(f"Error occurred during token status check: {e}")
        return False
    
def get_new_access_token(refresh_token, client_id, client_secret): #Obtain new Access Token from refresh_token
    token_url = 'https://www.googleapis.com/oauth2/v4/token'
    payload = {
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'refresh_token'
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()
        response_json = response.json()
        access_token = response_json['access_token']
        return access_token
    except Exception as e:
        print("Error occurred while obtaining access token:", e)
        return None


def get_device_temperature_traits(access_token): #Call to Nest API to obtain all the information from your hvac system. They named it "traits"
    api_endpoint = GET_TEMPERATURE_ENDPOINT.format(project_id=PROJECT_ID, device_id=DEVICE_ID)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(api_endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        traits = data['traits']
        return traits
    else:
        return None

def set_device_temperature(access_token, temperature):
    api_endpoint = SET_TEMPERATURE_ENDPOINT.format(project_id=PROJECT_ID, device_id=DEVICE_ID)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "command": "sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool",
        "params": {
            "coolCelsius": temperature
        }
    }
    response = requests.post(api_endpoint, json=payload, headers=headers)
    if response.status_code == 200:
        return True
    else:
        return False

def f_to_c(fahrenheit): #Convert Celcius to Fahrenheit
    celsius = float(fahrenheit - 32) * 5 / 9
    return celsius

def c_to_f(celsius): #Convert Fahrenheit to Celcius
    fahrenheit = (float(celsius) * 9 / 5 + 32)
    return fahrenheit

def getTemperatureAfterPM(temp, after_pm): #I like to cool my house more at night at turn the temperature high up after 8 AM
    current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-5))) # Central Time
    if current_time.hour >= after_pm or current_time.hour < 8:  # For example: 8 PM to 8 AM
        return temp - 2
    else:
        return temp + 1
    
def read_config(filename): #Read the data from a local config file that stored temperature range, access token, and the time where we want to decrease tempreture at night
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{filename}'.")
        return None

def write_config(filename, config_data): #Write data bawck to the config json file
    try:
        with open(filename, 'w') as file:
            json.dump(config_data, file, indent=4)
        print(f"Config data has been written to '{filename}' successfully.")
    except Exception as e:
        print(f"Error occurred while writing to file '{filename}': {e}")

def main():
    #Pulling access token and other information from the data.json file
    now = datetime.datetime.now()
    print("The current time is:", now)
    filename = 'data.json'
    config_data = read_config(filename)
    access_token = config_data.get('access_token', '')
    desired_lower_temp = config_data.get('desired_lower_temp', 0)
    desired_upper_temp = config_data.get('desired_upper_temp', 0)
    after_pm = config_data.get('after_pm', 0)

    #If token expired, obtain new token
    if not is_token_valid(access_token):
        print("Token expired. Getting new auth token.")
        access_token = get_new_access_token(refresh_token, client_id, client_secret)
        config_data['access_token'] = access_token
        write_config(filename, config_data)
        print("New Access Token: " + access_token)

    #Getting the current state of your hvac
    traits = get_device_temperature_traits(access_token)
    current_temperature = c_to_f(traits['sdm.devices.traits.Temperature']['ambientTemperatureCelsius'])
    target_temperature = c_to_f(traits['sdm.devices.traits.ThermostatTemperatureSetpoint']['coolCelsius'])
    print('Current Temp: ' + str(current_temperature) + ". Target temp: " + str(target_temperature))
    lower_bound = getTemperatureAfterPM(desired_lower_temp, after_pm)
    upper_bound = getTemperatureAfterPM(desired_upper_temp, after_pm)
    print("Lowerbound: " + str(lower_bound) + ". Upperbound: " + str(upper_bound))
    
    #If it's too hot, set to lowerbound temp. If it's too cold, set to  upperbound temp
    if math.floor(current_temperature) >= upper_bound and round(target_temperature) > lower_bound:
        if set_device_temperature(access_token, f_to_c(lower_bound)):
            print("It's getting hot. Set temperature to " + str(lower_bound))
    elif math.ceil(current_temperature) <= lower_bound and round(target_temperature) < upper_bound:
        if set_device_temperature(access_token, f_to_c(upper_bound)):
            print("It's getting cold. Set temperature to " + str(upper_bound))


if __name__ == "__main__":
    main()
