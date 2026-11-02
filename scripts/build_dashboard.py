"""Build report/test_dashboard.html (one self-contained file) from the recorded results."""

import base64
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "grading"))
from check_test_traceability import EXEMPT, requirements, tagged_tests  # noqa: E402


def load(path, default=None):
    path = ROOT / path
    return json.loads(path.read_text()) if path.exists() else default


def pct(n, d):
    return f"{(100 * n / d):.0f}%" if d else "n/a"


def main():
    unit = (load("report/unit_run/results.json") or {}).get("tests", [])
    system = (load("report/system_run/results.json") or {}).get("tests", [])
    perf = load("report/system_run/performance.json")
    mutants = load("report/mutation_check.json", [])
    last = load("report/last_run.json", {"steps": []})
    reqs, tagged = requirements(ROOT), tagged_tests(ROOT)
    active = [k for k, v in reqs.items() if not v["superseded"]]
    covered = [k for k in active if k in tagged]
    tests = [dict(t, suite="system") for t in system] + [
        dict(t, suite="unit") for t in unit
    ]
    passed = sum(t["outcome"] == "passed" for t in tests)

    def card(label, value, sub=""):
        return f'<div class="card"><small>{label}</small><b>{value}</b><span>{sub}</span></div>'

    cards = "".join(
        [
            card(
                "Tests run",
                len(tests),
                f"{len(system)} browser + load, {len(unit)} unit/integration",
            ),
            card(
                "Passed",
                f"{passed}/{len(tests)}",
                "all green"
                if passed == len(tests)
                else f"{len(tests) - passed} not passing",
            ),
            card(
                "Requirements covered",
                f"{len(covered)}/{len(active)}",
                f"{len(EXEMPT)} exempt with a written reason",
            ),
            card(
                "Mutants caught",
                f"{sum(m['status'] == 'KILLED' for m in mutants)}/{len(mutants)}"
                if mutants
                else "n/a",
                "by a test that names the requirement",
            ),
            card(
                "Purchase p95",
                f"{perf['p95_ms']:.0f} ms" if perf else "n/a",
                f"{perf['concurrent_buyers']} buyers, placeholder budget {perf['budget_p95_ms']:.0f} ms"
                if perf
                else "",
            ),
        ]
    )
    gates = "".join(
        f"<tr><td>{'🟢' if s['ok'] else '🔴'}</td><td>{html.escape(s['name'])}</td><td>{s['seconds']}s</td>"
        f"<td class='mono'>{html.escape(s['summary'])}</td></tr>"
        for s in last["steps"]
    )

    def chips(t):
        out = "".join(f"<i>{html.escape(r)}</i>" for r in t["reqs"])
        for flag, label in (
            ("blackbox", "black-box"),
            ("whitebox", "white-box"),
            ("call5", "Call 5"),
            ("perf", "load"),
        ):
            if t.get(flag):
                out += f'<em class="{flag}">{label}</em>'
        return out

    rows = "".join(
        f"<tr data-o='{t['outcome']}' data-s='{t['suite']}' data-t='{'b' if t['blackbox'] else ''}{'w' if t['whitebox'] else ''}{'c' if t['call5'] else ''}'>"
        f"<td class='{t['outcome']}'>{'✓' if t['outcome'] == 'passed' else '✗'}</td><td>{t['suite']}</td>"
        f"<td><b>{html.escape(t['name'][:90])}</b><br><span class='mono dim'>{html.escape(t['file'])}</span>"
        f"{'<br><span class=dim>' + html.escape(t['doc']) + '</span>' if t['doc'] else ''}</td>"
        f"<td>{chips(t)}</td><td>{t['seconds']}s</td></tr>"
        for t in tests
    )
    cov_rows = "".join(
        f"<tr class='{'bad' if k not in tagged and k not in EXEMPT and not reqs[k]['superseded'] else ''}'><td class='mono'>{k}</td>"
        f"<td>{len(tagged.get(k, []))}</td><td>{'superseded' if reqs[k]['superseded'] else ('exempt: ' + html.escape(EXEMPT[k])) if k in EXEMPT else 'covered' if k in tagged else 'UNCOVERED'}</td></tr>"
        for k in sorted(reqs)
    )
    mut_rows = "".join(
        f"<tr><td class='mono'>{m['id']}</td><td>{'🟢' if m['status'] == 'KILLED' else '🟡' if m['status'].startswith('KILLED') else '🔴'} {m['status'].lower()}</td>"
        f"<td class='mono'>{m['req']}</td><td class='mono dim'>{html.escape(m['file'])}</td><td class='mono dim'>{html.escape(m.get('change', ''))}</td></tr>"
        for m in mutants
    )
    shots = ""
    for img in (
        sorted((ROOT / "report" / "system_run" / "evidence").glob("*.png"))
        if (ROOT / "report/system_run/evidence").exists()
        else []
    ):
        data = base64.b64encode(img.read_bytes()).decode()
        shots += f"<figure><img loading='lazy' src='data:image/png;base64,{data}'><figcaption>{img.stem.replace('_', ' ')}</figcaption></figure>"
    perf_html = ""
    if perf:
        perf_html = (
            "<table>"
            + "".join(
                f'<tr><td>{k.replace("_", " ")}</td><td class="mono">{v}</td></tr>'
                for k, v in perf.items()
            )
            + "</table>"
        )

    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>EventHub Part 5 test dashboard</title>
<meta name="viewport" content="width=device-width,initial-scale=1"><style>
:root{{--bg:#0c101c;--panel:#141c2c;--line:#2c3b50;--ink:#f0f4ff;--dim:#9caac0;--cy:#7fe8e3;--ok:#5be3a6;--bad:#ff7b86;--or:#f6ab74}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:32px 20px 80px}}
h1{{font-size:34px;letter-spacing:-.04em;margin:6px 0}}h2{{margin:44px 0 12px;font-size:20px}}.eyebrow{{color:var(--cy);font-size:11px;letter-spacing:.2em;font-weight:800}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-top:20px}}.card{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}}
.card small{{color:var(--dim);letter-spacing:.1em;text-transform:uppercase;font-size:11px}}.card b{{display:block;font-size:30px;color:var(--cy)}}.card span{{color:var(--dim);font-size:12px}}
table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}}td,th{{padding:8px 11px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--cy);font-size:12px}}
.mono{{font-family:ui-monospace,monospace;font-size:12px}}.dim{{color:var(--dim)}}.passed{{color:var(--ok);font-weight:800}}.failed{{color:var(--bad);font-weight:800}}tr.bad td{{color:var(--bad)}}
i{{font-style:normal;background:#1c2b3f;border:1px solid var(--line);border-radius:20px;padding:1px 8px;margin:2px 3px 2px 0;display:inline-block;font-size:11px;font-family:ui-monospace,monospace}}
em{{font-style:normal;font-size:11px;border-radius:20px;padding:1px 8px;margin-right:3px;display:inline-block}}.blackbox{{background:#243044;color:#cfd8ff}}.whitebox{{background:#33281c;color:var(--or)}}.call5{{background:#143a34;color:var(--ok)}}.perf{{background:#3a1c2a;color:#ffb0c8}}
.bar{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}}button,input{{background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 12px;font:inherit}}button.on{{border-color:var(--cy);color:var(--cy)}}
figure{{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px}}figure img{{width:100%;border-radius:6px}}figcaption{{color:var(--dim);margin-top:6px;text-transform:capitalize}}
.gal{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}}details{{margin-top:8px}}summary{{cursor:pointer;color:var(--cy)}}
</style><main><div class="eyebrow">CEN 4020 / TEAM 5 / PART 5</div><h1>EventHub test dashboard</h1>
<p class="dim">Generated {html.escape((load("report/last_run.json") or {}).get("finished_at", ""))}. Each test names the requirement it protects. Black-box tests were derived from the specification only, white-box tests from the source.</p>
<div class="cards">{cards}</div>
<h2>Checks that ran</h2><table>{gates or "<tr><td>Run <span class=mono>python run_all_tests.py</span> to fill this in.</td></tr>"}</table>
<h2>Every test</h2><div class="bar" id="f"><button data-k="all" class="on">All</button><button data-k="failed">Failing</button><button data-k="system">Browser</button><button data-k="unit">Unit/integration</button><button data-k="b">Black-box</button><button data-k="w">White-box</button><button data-k="c">Call 5</button><input id="q" placeholder="filter by name or requirement id"></div>
<table id="t"><tr><th></th><th>suite</th><th>test</th><th>protects</th><th>time</th></tr>{rows}</table>
<h2>Load measurement</h2>{perf_html or "<p class=dim>Not run.</p>"}<p class="dim">The latency budget is a team placeholder, not a customer requirement (open item Q13).</p>
<h2>Do the tests fail when the code breaks?</h2>{("<table><tr><th>id</th><th>result</th><th>guards</th><th>file</th><th>change</th></tr>" + mut_rows + "</table>") if mutants else "<p class=dim>Run with --with-mutation.</p>"}
<h2>Requirement coverage</h2><details><summary>{len(covered)} of {len(active)} active requirements have a test; {len(EXEMPT)} exempt</summary><table><tr><th>requirement</th><th>tests</th><th>status</th></tr>{cov_rows}</table></details>
<h2>Evidence screenshots</h2><div class="gal">{shots or "<p class=dim>None captured.</p>"}</div></main>
<script>const rows=[...document.querySelectorAll('#t tr[data-o]')];let key='all';
function apply(){{const q=document.getElementById('q').value.toLowerCase();rows.forEach(r=>{{const k=key==='all'||(key==='failed'&&r.dataset.o!=='passed')||r.dataset.s===key||r.dataset.t.includes(key);r.style.display=k&&r.textContent.toLowerCase().includes(q)?'':'none'}})}}
document.querySelectorAll('#f button').forEach(b=>b.onclick=()=>{{key=b.dataset.k;document.querySelectorAll('#f button').forEach(x=>x.classList.toggle('on',x===b));apply()}});document.getElementById('q').oninput=apply</script></html>"""
    out = ROOT / "report" / "test_dashboard.html"
    out.write_text(page, encoding="utf-8")
    print(
        f"dashboard written: {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)"
    )


if __name__ == "__main__":
    main()
