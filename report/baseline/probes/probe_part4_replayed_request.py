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
proc = subprocess.Popen(
    [
        sys.executable,
        "-c",
        f"from eventhub.web import create_app; create_app().run(port={port}, threaded=True)",
    ],
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
c = connect(db)
register(c, "B", "b@example.com", "correct-horse-battery")
c.close()
d = make_driver()
d.get(url + "/login")
d.find_element(By.ID, "email").send_keys("b@example.com")
d.find_element(By.ID, "password").send_keys("correct-horse-battery")
d.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]").click()
WebDriverWait(d, 8).until(lambda x: "/login" not in x.current_url)
d.get(url + "/checkout/2")
csrf = d.execute_script("return document.querySelector('[name=csrf_token]').value")
r = d.execute_async_script(
    """const done=arguments[arguments.length-1]; const f={csrf_token:arguments[0],quantity:'2',currency:'USD'}; const urls=[];
 (async()=>{for(let i=0;i<2;i++){const r=await fetch('/checkout/2',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(f)}); urls.push(r.url)} done(urls)})();""",
    csrf,
)
c = sqlite3.connect(db)
out = {
    "same_form_sent_twice_urls": r,
    "orders_for_event_2": c.execute(
        "select count(*) from orders where event_id=2"
    ).fetchone()[0],
    "tickets_left_of_80": c.execute(
        "select available from events where id=2"
    ).fetchone()[0],
    "tickets_taken_should_be_2_if_one_order": 80
    - c.execute("select available from events where id=2").fetchone()[0],
}
d.quit()
proc.terminate()
print(json.dumps(out, indent=1))
Path("/tmp/before/before_replay.json").write_text(json.dumps(out, indent=1))
