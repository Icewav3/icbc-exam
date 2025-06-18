import os
import random
import time
from datetime import datetime, time as dt_time
from dotenv import load_dotenv
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

# ─────────────────────────────────────────────────────────
#  Load .env variables
# ─────────────────────────────────────────────────────────
load_dotenv()

# Credentials
last_name = os.getenv("ICBC_LASTNAME")
license_id = os.getenv("ICBC_LICENCENUMBER")
code = os.getenv("ICBC_KEYWORD")

# Search term for city; typing this into the modal search box
location_query = os.getenv("ICBC_LOCATION", "Richmond")

# Time window filters (optional)
after_date_str = os.getenv("ICBC_EXPECT_AFTERDATE")
before_date_str = os.getenv("ICBC_EXPECT_BEFOREDATE")
after_time_str = os.getenv("ICBC_EXPECT_AFTERTIME")
before_time_str = os.getenv("ICBC_EXPECT_BEFORETIME")

AFTER_DATE = parser.parse(after_date_str).date() if after_date_str else None
BEFORE_DATE = parser.parse(before_date_str).date() if before_date_str else None
AFTER_TIME = parser.parse(after_time_str).time() if after_time_str else None
BEFORE_TIME = parser.parse(before_time_str).time() if before_time_str else None

# Debug / timing
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
time_waiting = float(os.getenv("ACTION_DELAY", 1.5))

# ─────────────────────────────────────────────────────────
#  Selenium driver setup
# ─────────────────────────────────────────────────────────
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
url = "https://onlinebusiness.icbc.com/webdeas-ui/home"
driver_bin = os.getenv("CHROMEDRIVER_PATH", os.path.join(APP_ROOT, "chromedriver.exe"))
service = Service(driver_bin)
driver = webdriver.Chrome(service=service)

# ---------- helpers ----------

def debug_wait(msg=""):
    """Sleep only when DEBUG is true, with a label."""
    if DEBUG:
        print("[DEBUG]", msg)
        time.sleep(time_waiting)

def wait_footer():
    try:
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CLASS_NAME, "footer-content"))
        )
    except TimeoutException:
        pass

def slow_type(elem, text):
    for ch in text:
        elem.send_keys(ch)
        time.sleep(random.uniform(0.03, 0.1))

# Feedback / Qualtrics pop‑up can re‑render → use JS click to avoid stale refs

def dismiss_feedback_popup():
    try:
        popup_xpath = "/html/body/div[3]/div[2]/div/div[2]/button[2]"
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, popup_xpath))
        )
        driver.execute_script("document.querySelector('[tabindex\\=\'0\'] button:nth-child(2)')?.click()")
        debug_wait("dismiss popup")
    except TimeoutException:
        pass


def click_department(dept_elem):
    """Try to click the right‑arrow inside a department card; fall back to card itself."""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dept_elem)
        arrow = dept_elem.find_element(By.CSS_SELECTOR, ".right-arrow")
        driver.execute_script("arguments[0].click();", arrow)
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", dept_elem)
        except Exception:
            return False
    return True

# ---------- main flow ----------
print("[INFO] Opening ICBC portal …")
driver.get(url)
wait_footer()
driver.maximize_window(); debug_wait("maximize")

driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

debug_wait("scroll to bottom")

# Begin booking
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-home/mat-card/div[3]/div[3]/button"))
).click(); debug_wait("clicked book btn")

# Login inputs
inputs = {
    "last name": ("/html/body/app-root/app-login/mat-card/mat-card-content/form/span[1]/div/div[1]/div/mat-form-field/div/div[1]/div[3]/input", last_name),
    "licence":   ("/html/body/app-root/app-login/mat-card/mat-card-content/form/span[1]/div/div[2]/div/mat-form-field/div/div[1]/div[3]/input", license_id),
    "keyword":   ("/html/body/app-root/app-login/mat-card/mat-card-content/form/span[2]/div[2]/mat-form-field/div/div[1]/div[3]/input", code),
}
for label, (xp, val) in inputs.items():
    inp = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xp)))
    inp.clear(); inp.send_keys(val); debug_wait(f"{label} set")

driver.find_element(By.CLASS_NAME, "mat-checkbox-inner-container").click(); debug_wait("terms")
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-login/mat-card/mat-card-content/form/div[2]/div[2]/button"))
).click(); debug_wait("sign in")

# Location search modal
loc_inp = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "mat-input-3")))
loc_inp.clear(); slow_type(loc_inp, location_query); debug_wait("typed city")
loc_inp.send_keys(Keys.ENTER)

WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div/div/mat-dialog-container/app-search-modal/div/div/form/div[2]/button"))
).click(); debug_wait("search")

print("[INFO] Sniping loop… press Ctrl+C to stop")

while True:
    dismiss_feedback_popup()
    department_cards = driver.find_elements(By.CLASS_NAME, "department-container")

    for dept in department_cards:
        try:
            title = dept.find_element(By.CLASS_NAME, "department-title").text.lower().strip()
        except Exception:
            continue

        # We accept both Richmond offices (Elmbridge Way + Lansdowne)
        if not title.startswith("richmond"):
            continue

        if click_department(dept):
            debug_wait(f"opened {title[:40]}…")
        else:
            continue

        # Now parse date slots
        for slot in driver.find_elements(By.CLASS_NAME, "date-title"):
            txt = slot.text.strip()
            try:
                dt_obj = parser.parse(txt)
            except Exception:
                continue
            d, t = dt_obj.date(), dt_obj.time()
            if ((AFTER_DATE is None or d >= AFTER_DATE) and
                (BEFORE_DATE is None or d <= BEFORE_DATE) and
                (AFTER_TIME is None or t >= AFTER_TIME) and
                (BEFORE_TIME is None or t <= BEFORE_TIME)):
                print("✅", dt_obj, "-", title)

    time.sleep(2)  # throttle loop
