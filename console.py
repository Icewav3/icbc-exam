import json
from datetime import datetime

import requests as requests

headers = {'Content-type': 'application/json',
           'Accept': 'application/json, text/plain, */*',
           'Referer': 'https://onlinebusiness.icbc.com/webdeas-ui/login;type=driver',
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
           'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
           'sec-ch-ua-mobile': '?0',
           'sec-ch-ua-platform': '"macOS"',
           }


def load_config():
    with open('config.json') as config_file:
        return json.load(config_file)


def get_token(last_name, license_id, code):
    login_url = "https://onlinebusiness.icbc.com/deas-api/v1/webLogin/webLogin"

    payload = {
        "drvrLastName": last_name,
        "licenceNumber": license_id,
        "keyword": code
    }
    response = requests.put(login_url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        return response.headers["Authorization"]
    return "error"


def get_appointments(token, last_name, license_id, exam_class, after_date):
    appointment_url = "https://onlinebusiness.icbc.com/deas-api/v1/web/getAvailableAppointments"
    headers['Authorization'] = token
    point_grey = {
        "aPosID": 9,
        "examType": str(exam_class) + "-R-1",
        "examDate": after_date,
        "ignoreReserveTime": "false",
        "prfDaysOfWeek": "[0,1,2,3,4,5,6]",
        "prfPartsOfDay": "[0,1]",
        "lastName": last_name,
        "licenseNumber": license_id
    }
    response = requests.post(appointment_url, data=json.dumps(point_grey), headers=headers)

    if response.status_code == 200:
        return response.json()
    print('Authorization Error')
    return []


if __name__ == "__main__":
    configs = load_config()
    date_format = "%Y-%m-%d"
    auth_token = get_token(configs['LastName'], configs['LicenceNumber'], configs['Keyword'])
    if auth_token != "error":
        while True:
            appointments = get_appointments(auth_token, configs['LastName'], configs['LicenceNumber'], configs['Class'],
                                            configs['AfterDate'])

            after = datetime.strptime(configs['AfterDate'], date_format)
            before = datetime.strptime(configs['BeforeDate'], date_format)

            for appointment in appointments:
                check = datetime.strptime(appointment['appointmentDt']['date'], date_format)
                if after <= check <= before:
                    print("Found")
