# Nest Thermostat Temperature Differential Management Script

## Problem
After installing a new HVAC system in my house, I found that it tends to cool the house too quickly, leading to short cycles and potential wear and tear on the system. Manually adjusting the thermostat temperature within a narrow range to prevent this is inconvenient and requires constant monitoring.

## Solution
To automate the management of the temperature differential and optimize the HVAC system's performance, I wrote a Python script that leverages the Nest Thermostat's API capabilities. This script allows for dynamic adjustment of the target temperature range based on predefined criteria, ensuring efficient cooling without the need for manual intervention.

## Setup
To use this script, you'll need to set up access to the Nest Thermostat API. Follow the steps outlined in [this guide](https://developers.google.com/nest/device-access/get-started) to authenticate your application and obtain the necessary credentials.

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
 