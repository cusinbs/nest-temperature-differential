# Nest Thermostat Temperature Differential Management Script

## Problem
After installing a new HVAC system in my house, I found that it tends to cool the house too quickly, leading to short cycles and potential wear and tear on the system. Manually adjusting the thermostat temperature within a narrow range to prevent this is inconvenient and requires constant monitoring.

## Solution
To automate the management of the temperature differential and optimize the HVAC system's performance, I wrote a Python script that leverages the Nest Thermostat's API capabilities. This script allows for dynamic adjustment of the target temperature range based on predefined criteria, ensuring efficient cooling without the need for manual intervention.

## Setup
For the script to run continuously, you must obtain a Refresh Token. This token is long-lived and will be used by the script to generate new, short-lived Access Tokens before every API call.

### Prerequisites
Google Cloud Project: A Google Cloud Project with the Smart Device Management API enabled.

Device Access Project: A Device Access Project created in the Device Access Console.

OAuth 2.0 Credentials: An OAuth 2.0 Client ID and Client Secret from the Google Cloud Console.

### Step-by-Step Authorization
This process performs the initial account linking to get your necessary tokens.

1. Retrieve Project Identifiers:

OAuth Client ID: Get this from your Google Cloud Console Credentials page (e.g., https://console.cloud.google.com/auth/clients/116917491970-lctkg2d7i7ttvil90oml3ddvto0hd4m4.apps.googleusercontent.com?project=smart-home-422713).

Project ID: Get this from your Device Access Console project information page (e.g., https://console.nest.google.com/device-access/project/80946680-0a6f-4a6d-8aa0-688034f0338d/information).

2. Link Nest Account (Get Authorization Code):
Open the following URL in your browser, replacing {{project-id}} and {{oauth2-client-id}} with your values. This links your Nest account and prompts you for permissions.

Code snippet

https://nestservices.google.com/partnerconnections/{{project-id}}/auth?redirect_uri=https://www.google.com&access_type=offline&prompt=consent&client_id={{oauth2-client-id}}&response_type=code&scope=https://www.googleapis.com/auth/sdm.service

The browser will redirect to https://www.google.com/?code=.... Copy the value of the code= parameter from the URL. This is your one-time Authorization Code.

3. Exchange Code for Tokens (Get Refresh Token):
Execute the following curl command in your terminal, replacing the bracketed placeholders with your values:

curl -X POST 'https://www.googleapis.com/oauth2/v4/token?client_id={{client_id}}&client_secret={{client_secret}}&code={{code_from_step_2}}&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsdm.service&grant_type=authorization_code&redirect_uri=https%3A%2F%2Fwww.google.com'

The response will be a JSON object containing your access_token and, most importantly, your refresh_token. Save the refresh_token securely.

I also found [this guide](https://geoffhudik.com/tech/2023/03/04/trying-google-nest-api-with-postman-and-python/) very helpful to setup the authorization 
## How to Run
1. Clone this repository to your local machine. This repo has a `data.json` file with the following format:
    ```json
    {
        "access_token": "",
        "desired_lower_temp": 73,
        "desired_upper_temp": 76,
        "after_pm": 21
    }
    ```
    When first run the script, it will update the empty string `"access_token"` with your Nest Thermostat access token (given that you have a refresh_token). Set the values for `"desired_lower_temp"` and `"desired_upper_temp"` to define the temperature range you want to maintain. `"after_pm"` specifies the hour (in 24-hour format) after which the script should start adjusting the temperature 2 degrees colder. You can modify the script to your liking.
2. Replace the placeholder values in the script with your Nest Thermostat credentials.
3. Decide on the run frequency of this script. You can run the script in a cron job every 3 to 5 minutes, or modify it to use a while loop with a timeout every 3 minutes per loop.
4. The command I use to run the script in my Raspberry Pi cron job tab:
    ```
    */3 * * * * python3 /path-to-folder/Temperature_Diff.py >> /path-to-folder/log_file 2>&1
    ```

Feel free to contribute to or modify this script to better suit your needs. Your feedback and suggestions are always welcome!
 
