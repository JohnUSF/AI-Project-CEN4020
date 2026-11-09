"""Run the Call 5 scenarios against the UNTOUCHED Part 4 build to see what it really did."""

import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

BASE = Path("/home/claude/baseline_part4")
sys.path.insert(0, str(BASE))
sys.path.insert(0, "/home/claude/EventHub_Team5_Part5/Source_Code_and_System_Tests")
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from eventhub.db import connect
from eventhub.identity import register
from tests_system.conftest import make_driver

tmp = Path(tempfile.mkdtemp())
db = tmp / "p4.sqlite3"
s = socket.socket()
s.bind(("127.0.0.1", 0))
port = s.getsockname()[1]
s.close()
env = {
    **os.environ,
    "EVENTHUB_DB": str(db),
    "EVENTHUB_SECRET_KEY": "k" * 32,
    "EVENTHUB_DISCOUNT_PERCENT": "10",
    "PYTHONPATH": str(BASE),
}
code = (
    f"from eventhub.web import create_app; create_app().run(port={port}, threaded=True)"
)
proc = subprocess.Popen(
    [sys.executable, "-c", code],
    cwd=BASE,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
url = f"http://127.0.0.1:{port}"
for _ in range(60):
    try:
        urllib.request.urlopen(url + "/", timeout=1)
        break
    except Exception:
        time.sleep(0.2)


def q(sql, a=()):
    c = sqlite3.connect(db)
    r = c.execute(sql, a).fetchall()
    c.close()
    return r


c = connect(db)
register(c, "Before", "before@example.com", "correct-horse-battery")
c.close()
d = make_driver()
out = {}


def login():
    d.get(url + "/login")
    d.find_element(By.ID, "email").send_keys("before@example.com")
    d.find_element(By.ID, "password").send_keys("correct-horse-battery")
    d.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]").click()
    WebDriverWait(d, 8).until(lambda x: "/login" not in x.current_url)


login()
# 1. double-click the checkout button
d.get(url + "/checkout/2")
b = d.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]")
d.execute_script("arguments[0].scrollIntoView({block:'center',behavior:'instant'})", b)
ActionChains(d).double_click(b).perform()
time.sleep(2.5)
out["double_click_checkout_button_orders"] = q(
    "select count(*) from orders where event_id=2"
)[0][0]
out["stock_event2_after (80 at start, 1 ticket each)"] = q(
    "select available from events where id=2"
)[0][0]
# 2. three quick clicks on a card
d.get(url + "/")
card = d.find_element(By.CSS_SELECTOR, ".event-card")
d.execute_script(
    "for (const n of [1,2,3]) arguments[0].dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,detail:n}))",
    card,
)
time.sleep(2.5)
out["triple_click_card_orders"] = q("select count(*) from orders where event_id=1")[0][
    0
]
# 3. 200 purchase requests in a row from one signed-in browser
d.get(url + "/events/3")
csrf = d.execute_script("return document.querySelector('[name=csrf_token]').value")
res = d.execute_async_script(
    """const done=arguments[arguments.length-1]; let ok=0, other=0;
  (async()=>{for(let i=0;i<200;i++){const r=await fetch('/quick-buy/3',{method:'POST',credentials:'same-origin',redirect:'manual',
   headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({csrf_token:arguments[0]})}); if(r.type==='opaqueredirect') ok++; else other++;} done([ok,other])})();""".replace(
        "arguments[0]", "CSRF"
    ).replace("const done", f"const CSRF='{csrf}'; const done")
)
out["200_requests_accepted_vs_refused"] = res
out["orders_created_by_the_200"] = q("select count(*) from orders where event_id=3")[0][
    0
]
# 4. what the confirmation says, and where the currency came from
d.get(url + "/checkout/4")
d.execute_script("document.getElementById('currency').value='EUR'")
d.find_element(By.ID, "quantity").clear()
d.find_element(By.ID, "quantity").send_keys("2")
b = d.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]")
d.execute_script("arguments[0].scrollIntoView({block:'center',behavior:'instant'})", b)
b.click()
WebDriverWait(d, 8).until(lambda x: "/orders/" in x.current_url)
page = d.find_element(By.TAG_NAME, "body").text
out["confirmation_has_sentence_saying_what_was_charged"] = "charged" in page.lower()
out["confirmation_labels"] = [
    l
    for l in page.splitlines()
    if any(w in l for w in ("Total", "Currency", "discount", "EUR"))
]
d.save_screenshot("/tmp/before/part4_confirmation.png")
d.get(url + "/register")
out["register_page_has_currency_field"] = bool(d.find_elements(By.ID, "currency"))
d.get(url + "/")
out["header_has_currency_control"] = bool(d.find_elements(By.ID, "nav-currency"))
out["accounts_currency_after_registration"] = q("select currency from accounts")[0][0]
out["email_columns_ever_updated_in_source"] = subprocess.run(
    "grep -rniE 'set\\s+email' eventhub | wc -l",
    shell=True,
    cwd=BASE,
    capture_output=True,
    text=True,
).stdout.strip()
d.quit()
proc.terminate()
print(json.dumps(out, indent=1, ensure_ascii=False))
Path("/tmp/before/before_evidence.json").write_text(
    json.dumps(out, indent=1, ensure_ascii=False)
)
