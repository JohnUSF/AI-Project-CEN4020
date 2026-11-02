# First run: 110 passed, 27 failed. Every failure was a defect in the generated test, not in the app.

Raw output of that run: `first_run_output.txt`. The tests exactly as generated: `tests_system_as_generated/`.

| Class | Tests | Root cause | Fix | Changed |
|---|---:|---|---|---|
| A. Click intercepted | 13 | Buttons sat below the 757 px viewport and `html{scroll-behavior:smooth}` in style.css animates every scroll, so Selenium clicked while the page was still moving. My first fix (plain `scrollIntoView`) did not help for the same reason. | `helpers.click()`: `scrollIntoView({block:'center', behavior:'instant'})`; used by the helpers and two tests | test (second attempt) |
| B. Option not found | 10 | Admin page options are `<option>GBP</option>` with no `value=`; `select_by_value` looks for the attribute | `select_by_visible_text` on the admin page | test |
| C. Link not found | 1 | Link text is `Get tickets <span>↗</span>`; the exact-text locator did not match | `PARTIAL_LINK_TEXT 'Get tickets'` (2 tests) | test |
| D. Duplicate account | 1 | `grad@usf.edu` and `GRAD@USF.EDU` normalise to one address in a shared database | unique prefix per parameter, keeping the case and domain under test | test |
| E. Stale element | 1 | Reading page text while the page navigates raised `StaleElementReference` inside the wait | waits now ignore stale/no-such-element and retry | test |
| F. Triple click | 1 | `ActionChains` addressed the card after the page had started navigating | dispatch three real click events (detail 1,2,3) from the page | test |

## Found while verifying the fixes (not in the first run)

| Class | Tests | Root cause | Fix | Changed |
|---|---:|---|---|---|
| G. Direct clicks | 10 | Admin 'Save rate' and similar buttons were clicked with plain `.click()`, so the smooth-scroll race from class A applied to them too | every direct button click goes through `helpers.click()` | test |
| H. Sign-out race | 1 | Test navigated to `/orders` before the sign-out POST finished; it passed in the first run only by timing luck | wait until the signed-out page is showing | test |
