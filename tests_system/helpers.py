"""Small page-level helpers shared by the system tests."""

import re
from pathlib import Path

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .conftest import PASSWORD, REPORT_DIR

TIMEOUT = 10


def wait(driver, timeout=TIMEOUT):
    # A page that is mid-navigation raises 'stale element' while we read it; that means 'not yet'.
    return WebDriverWait(
        driver,
        timeout,
        ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
    )


def click(driver, element):
    """Scroll to mid-screen first, instantly.

    style.css sets `scroll-behavior: smooth`, so scrolling is animated and Selenium clicks while the page is
    still moving (first-run failure class A). behavior:'instant' skips the animation.
    """
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element
    )
    element.click()


def css(driver, selector, timeout=TIMEOUT):
    return wait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def visible(driver, selector, timeout=TIMEOUT):
    return wait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )


def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text


def alerts(driver):
    return [e.text for e in driver.find_elements(By.CSS_SELECTOR, ".alert")]


def wait_for_text(driver, text, timeout=TIMEOUT):
    wait(driver, timeout).until(lambda d: text in body_text(d))


def wait_for_url(driver, fragment, timeout=TIMEOUT):
    wait(driver, timeout).until(lambda d: fragment in d.current_url)


def wait_for_url_not(driver, fragment, timeout=TIMEOUT):
    wait(driver, timeout).until(lambda d: fragment not in d.current_url)


def shot(driver, name):
    """Save an evidence screenshot for the report."""
    folder = REPORT_DIR / "evidence"
    folder.mkdir(parents=True, exist_ok=True)
    driver.save_screenshot(str(folder / f"{name}.png"))


def login(driver, base, email, password=PASSWORD, next_path=None):
    driver.get(base + "/login" + (f"?next={next_path}" if next_path else ""))
    css(driver, "#email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    click(
        driver, driver.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]")
    )


def signed_in(driver, base, user):
    login(driver, base, user["email"], user["password"])
    wait(driver).until(lambda d: "/login" not in d.current_url)


def register_ui(driver, base, name, email, password=PASSWORD, currency=None, raw=False):
    """Fill the registration form. raw=True switches off the browser's own validation."""
    driver.get(base + "/register")
    if raw:
        driver.execute_script("document.querySelector('form.panel').noValidate = true;")
    css(driver, "#name").send_keys(name) if not raw else driver.execute_script(
        "document.getElementById('name').removeAttribute('maxlength'); document.getElementById('name').value = arguments[0];",
        name,
    )
    if raw:
        driver.execute_script(
            "const e=document.getElementById('email'); e.type='text'; e.value=arguments[0];"
            "const p=document.getElementById('password'); p.removeAttribute('minlength'); p.value=arguments[1];",
            email,
            password,
        )
    else:
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
    if currency:
        sel = driver.find_element(By.ID, "currency")
        if raw and currency not in [
            o.get_attribute("value") for o in Select(sel).options
        ]:
            driver.execute_script(
                "const s=document.getElementById('currency'); const o=document.createElement('option');"
                "o.value=arguments[0]; o.text=arguments[0]; s.add(o); s.value=arguments[0];",
                currency,
            )
        else:
            Select(sel).select_by_value(currency)
    click(
        driver, driver.find_element(By.CSS_SELECTOR, "form.panel button[type=submit]")
    )


def submit_checkout_raw(driver, quantity, currency=None):
    """Submit the checkout form with whatever the test wants, bypassing browser validation."""
    driver.execute_script(
        """
        const f = document.getElementById('checkout-form'); f.noValidate = true;
        const q = f.querySelector('[name=quantity]'); q.type = 'text';
        q.removeAttribute('min'); q.removeAttribute('max'); q.value = arguments[0];
        const c = f.querySelector('[name=currency]');
        if (arguments[1] !== null) {
          let o = [...c.options].find(x => x.value === arguments[1]);
          if (!o) { o = document.createElement('option'); o.value = arguments[1]; o.text = arguments[1]; c.add(o); }
          c.value = arguments[1];
        }
        f.requestSubmit();""",
        quantity,
        currency,
    )


def buy_via_checkout(driver, base, event_id, quantity="1", currency=None):
    """The normal buyer path: open checkout, set the form, submit. Returns the order page text."""
    driver.get(f"{base}/checkout/{event_id}")
    css(driver, "#checkout-form")
    if currency:
        Select(driver.find_element(By.ID, "currency")).select_by_value(currency)
    q = driver.find_element(By.ID, "quantity")
    q.clear()
    q.send_keys(str(quantity))
    click(
        driver,
        driver.find_element(By.CSS_SELECTOR, "#checkout-form button[type=submit]"),
    )
    wait(driver).until(lambda d: "/checkout/" not in d.current_url)
    return body_text(driver)


def order_id_from_url(driver):
    m = re.search(r"/orders/(\d+)", driver.current_url)
    return int(m.group(1)) if m else None


def csrf_and_token(driver):
    """Read the hidden CSRF and purchase token from the page the browser is on."""
    return driver.execute_script(
        "return {csrf: document.querySelector('[name=csrf_token]').value,"
        " token: (document.querySelector('[name=purchase_token]') || {}).value};"
    )


def fetch_post(driver, path, fields):
    """POST form fields from the page's own origin using the browser's session cookie.

    Returns {status, url, text, retryAfter}. Redirects are followed like a browser would.
    """
    return driver.execute_async_script(
        """
        const done = arguments[arguments.length - 1];
        const body = new URLSearchParams(arguments[1]);
        fetch(arguments[0], {method: 'POST', body, credentials: 'same-origin',
              headers: {'Content-Type': 'application/x-www-form-urlencoded'}})
          .then(async r => done({status: r.status, url: r.url, text: await r.text(),
                                 retryAfter: r.headers.get('Retry-After')}))
          .catch(e => done({status: 0, url: '', text: String(e), retryAfter: null}));""",
        path,
        fields,
    )
