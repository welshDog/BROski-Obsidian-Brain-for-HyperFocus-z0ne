"""Static structure lock for the constellation page's community colouring.

Not a behaviour test — a D3 force-graph is verified by eye (see the plan's
manual checklists). This guards against a future edit silently removing the
v5 community machinery or landing a JS syntax error in the inline script.
"""
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / ".agents" / "mcp-bridge" / "constellation.html"


def _script() -> str:
    html = PAGE.read_text(encoding="utf-8")
    m = re.search(r"<script>\n(.*?)</script>", html, re.S)
    assert m, "inline <script> block not found"
    return m.group(1)


def test_page_is_one_wellformed_html_doc():
    html = PAGE.read_text(encoding="utf-8")
    depth = 0
    worst = 0

    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            nonlocal depth
            if tag not in ("br", "img", "meta", "link", "input", "hr"):
                depth += 1

        def handle_endtag(self, tag):
            nonlocal depth, worst
            if tag not in ("br", "img", "meta", "link", "input", "hr"):
                depth -= 1
                worst = min(worst, depth)

    P().feed(html)
    assert worst == 0, f"unbalanced tags (min depth {worst})"
    assert html.count("<script") == 2, "expected exactly 2 <script> tags (d3 CDN + inline)"


def test_inline_script_passes_node_check(tmp_path):
    if shutil.which("node") is None:
        import pytest
        pytest.skip("node not on PATH — JS syntax gate skipped")
    js = tmp_path / "const.js"
    js.write_text(_script(), encoding="utf-8")
    r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, f"node --check failed:\n{r.stderr}"


def test_community_machinery_present():
    s = _script()
    for ident in ("PALETTE", "MUTED", "communityColor", "communityColorMap",
                  "commSize", "realComms", "fillFor", "colorMode",
                  "focusedComms", "applyCommunityFocus", "renderLegend",
                  "community_label"):
        assert ident in s, f"missing identifier: {ident}"
    assert 'id="modeToggle"' in PAGE.read_text(encoding="utf-8")


def test_palette_shape():
    s = _script()
    m = re.search(r"const PALETTE = \[(.*?)\]", s, re.S)
    assert m, "PALETTE literal not found"
    hexes = re.findall(r'"(#[0-9a-fA-F]{6})"', m.group(1))
    assert len(hexes) >= 10, f"PALETTE has {len(hexes)} entries, want >= 10"
    assert hexes[:3] == ["#22d3ee", "#a78bfa", "#f59e0b"], "brand three must lead PALETTE"
    mm = re.search(r'const MUTED = "(#[0-9a-fA-F]{6})"', s)
    assert mm and mm.group(1).lower() not in [h.lower() for h in hexes], "MUTED must be distinct"


def test_no_regression_of_kept_features():
    s = _script()
    for ident in ("const COLORS", "const group", "const radius", "edgeColor",
                  "getElementById(\"search\")", "/graph/related/"):
        assert ident in s, f"spec 4.5 says this stays, but it's gone: {ident}"
