import time, requests, json, re, datetime, os, threading, random, sys, signal

from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup


"""
Author:     Max Patecky
Contact:    max.patecky@stud.htw-dresden.de

Script-Version:     1.1.0
HTWD-Mobil-Version: 2.0.3

First Release:  2023-07-30
Latest Update:  2024-02-07

Ich übernehme keine Haftung für Schäden, die durch die Verwendung dieses Skripts entstehen.
Jede Verwendung erfolgt auf eigene Gefahr.

Dieses Skript loggt sich in den Notenbereich der HTW Dresden ein und überprüft in regelmäßigen Abständen, ob es neue Noten gibt.
Wenn neue Noten vorhanden sind, wird eine Pushbullet-Benachrichtigung gesendet.

Die Funktionsweise des Skripts basiert auf der Struktur der HTW-Noten-Seite mit der oben angegebenen Version.
"""


# =================================================================================================
# === SETUP 
# =================================================================================================

load_dotenv()

LOG_DIR = "logs/"
LOG_FILE = "latest.log"

# ====================================================
# === LOGGING
# ====================================================

# prints message with timestamp and saves it to log file
def log(message, log_type="INFO"):
    timestamp = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")
    log_message = f"[{timestamp}] [{log_type}] {message}"
    
    print(log_message)
    sys.stdout.flush()
    
    with open(LOG_DIR + LOG_FILE, "a") as log_file:
        log_file.write(log_message)

# ====================================================
# === NOTIFICATIONS
# ====================================================

SERVICES = []
if os.getenv('PUSHBULLET_ENABLED') == 'true':
    SERVICES.append('pushbullet')
if os.getenv('TELEGRAM_ENABLED') == 'true':
    SERVICES.append('telegram')

def send_notification(title, message):
    for service in SERVICES:
        if service == 'pushbullet':
            send_pushbullet_notification(title, message)
        elif service == 'telegram':
            send_telegram_notification(title, message)
        else:
            log("Ungültiger Benachrichtigungsdienst", "WARNING")

def send_pushbullet_notification(title, message):
    data = {
        'type': 'note',
        'title': title,
        'body': message
    }
    headers = {
        'Access-Token': os.getenv('PUSHBULLET_TOKEN'),
        'Content-Type': 'application/json'
    }
    response = requests.post("https://api.pushbullet.com/v2/pushes", data=json.dumps(data), headers=headers)
    if response.status_code != 200:
        log("Pushbullet-Benachrichtigung konnte nicht gesendet werden!", "WARNING")
        log("Response-Code: " + str(response.status_code), "WARNING")

def send_telegram_notification(title, message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    text = f"{title}\n{message}"
    
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={text}'
    
    response = requests.get(send_text)
    
    if response.status_code != 200:
        log("Telegram-Benachrichtigung konnte nicht gesendet werden!", "WARNING")
        log("Response-Code: " + str(response.status_code), "WARNING")

# ====================================================
# === SCRAPER
# ====================================================

# Login to the grades page of HTW Dresden
def login(username, password):
    with requests.session() as session:
        payload = {
            '__referrer[@extension]': 'Felogin',
            '__referrer@controller]': 'Login',
            '__referrer@action]': 'login',
            '__referrerarguments]': 'YTowOnt952eec09e0e12541d15fc1a1e8438e551752590ed',
            '__referrer@request]': '{"@extension":"Felogin","@controller":"Login","@action":"login"}425cf7642bb3ecf60c6c7cb2e9befc2e0de384f7',
            '__trustedProperties': '{"user":1,"pass":1,"submit":1,"logintype":1,"pid":1,"noredirect":1}580eca94edf193692ce394cae2c2eeec5596c9b4',
            'user': username,
            'pass': password,
            'submit': 'Anmelden',
            'logintype': 'login',
            'pid': '21@968399d1618f39ccb731fc883946c1e11b5c6a9f'
        }
        response = session.post(os.getenv('HTWD_URL'), data=payload)
        if response.status_code != 200:
            log("Login auf HTWD Mobil fehlgeschlagen!", "CRITICAL")
            return None
        return session

# ====================================================
# === GRADE CHECKER
# ====================================================

# Get the grades from the grades page of HTW Dresden
def get_current_grades(session):
    request = session.get(os.getenv('HTWD_URL')).text
    html = BeautifulSoup(request, "html.parser")
    
    grade_elements = html.select('.align-items-baseline.collapsed.list-group-item.list-group-custom-item')
    grades_json = []
    
    for element in grade_elements:
        grade = element.select_one('span').text.strip()
        module = element.select_one('div > h4').text.strip()
        if not re.match(r'^\d+,\d+$', grade):
            continue
        grades_json.append({
            'grade': grade,
            'module': module,
        })
    return grades_json, len(grades_json)

# start grade checker thread
def run_grade_checker(username, password):
    log("Konfigurierter Benutzer: " + username, "INFO")
    
    while True:
        # prevent requests during night time to reduce ban risk
        now = datetime.now().time()
        allowed_start = datetime.strptime("06:00", "%H:%M").time()
        allowed_end = datetime.strptime("22:00", "%H:%M").time()

        if not allowed_start < now < allowed_end:
            log("Es ist Nachtzeit, keine Anfragen werden gesendet.", "INFO")
            time.sleep(int(os.getenv('POLL_INTERVAL')))
            continue

        # create session and get grades
        session = login(username, password)
        
        if session is not None:
            grades_json, grades_count = get_current_grades(session)
            
            global prev_grades_count
            global prev_grades_json
            
            if grades_count > prev_grades_count:
                # Filter out new grades
                new_grades = []
                for grade in grades_json:
                    if grade not in prev_grades_json:
                        new_grades.append(grade)
                
                # Update prev_grades_json and send pushbullet notification for each new grade
                if prev_grades_count > 0:
                    send_notification("HTWD Noten Checker", "Es gibt neue Noten!")
                    if os.getenv('POST_GRADES') == 'true':
                        for grade in new_grades:
                            send_notification(grade['module'], "Note:" + grade['grade'])
                    
                # update prev_grades_count and prev_grades_json
                prev_grades_count = grades_count
                prev_grades_json = grades_json
            else:
                log("Keine neuen Noten! (" + str(grades_count) + " / " + str(prev_grades_count) + ")", "INFO")
                
        time.sleep(int(os.getenv('POLL_INTERVAL')))

# handle sigterm shutdown
def sigterm_handler(signal, frame):
    thread._stop()
    log("HTWD Noten-Checker wurde via SIGTERM beendet.", "INFO")
    sys.exit(0)

# =================================================================================================
# === RUNTIME 
# =================================================================================================

if __name__ == "__main__":
    # create log dir in current directory if not exists
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)
    
    global prev_grades_count
    prev_grades_count = 0
    
    global prev_grades_json
    prev_grades_json = []
    
    thread = threading.Thread(
        target=run_grade_checker, 
        args=(
            os.getenv('HTWD_USERNAME'), 
            os.getenv('HTWD_PASSWORD'))
        )
    thread.start()
    
    log("HTWD Noten-Checker gestartet!", "INFO")
    
    timestamp = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")
    send_notification("HTWD Noten-Checker", "Der Noten-Checker wurde gestartet ("+timestamp+")!")

    # handle cli shutdown
    try:
        while thread.is_alive():
            thread.join(1)
    except KeyboardInterrupt:
        thread._stop()
        log("HTWD Noten-Checker wurde via CLI beendet.", "INFO")

    # handle sigterm shutdown
    signal.signal(signal.SIGTERM, sigterm_handler)
