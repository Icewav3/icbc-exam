# ICBC exam | ICBC Bot
Automation to find free slots on ICBC road test exam.

As you know, there is a massive problem with lookup appointment free slots for the ICBC road test exam.
In my case, I found an appointment in 4 months. 
So I decided to automate the process, and after two hours, I found an appointment in a week.

Let's start with coffee :)
If you like what I'm doing, you can buy a coffee for me: https://www.buymeacoffee.com/ZanMax

There are 3 version:

- UI
- Python console
- Golang console


## Running
#### UI
##### Install necessary packages
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

##### WebDriver
Download webdriver for your platform:
https://chromedriver.chromium.org/downloads

##### Configs
You need to change configs like:
- last_name
- license_id
- code

Also you need set month and location:
- location = "Coquitlam"
- month = "December"

##### Telegram configuration
Steps to config telegram bot:
- Get the Bot API key from the BotFather
- Run command "telegram-send -configure"
- telegram-send will ask for the token you got from the botfather
- Send the code which you will receive from telegram-send to the Bot

##### Run
python3 ui/main.py


#### Console Python


#### Console Go