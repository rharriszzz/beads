"""Optional bounded browser QA. Requires Playwright and an installed Chromium."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8765/')
    parser.add_argument('--screenshots', type=Path)
    args = parser.parse_args()
    base = args.base_url.rstrip('/') + '/'
    if args.screenshots:
        args.screenshots.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1050}, device_scale_factor=1)
        errors, failed, requests = [], [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('requestfailed', lambda request: failed.append(request.url))
        page.on('request', lambda request: requests.append(request.url))
        response = page.goto(base, wait_until='networkidle')
        assert response.status == 200
        assert page.title().startswith('Beads —')
        if args.screenshots:
            page.screenshot(path=str(args.screenshots / 'desktop.png'))
        assert page.locator('#graph-paper .bead').count() == 984
        assert page.locator('#graph-paper [data-chosen="true"]').count() == 208
        assert '201 supported / 0 conflicting / 7 insufficient' in page.locator('#epoch-summary').inner_text()
        for epoch, n in [('r347', 7), ('r344', 9)]:
            page.select_option('#epoch', epoch)
            page.select_option('#interpretation', 'strict')
            unknowns = page.locator('#graph-paper [data-chosen="true"] .unknown').evaluate_all(
                '(xs) => xs.filter(x => getComputedStyle(x).display !== "none").length')
            assert unknowns == n, (epoch, unknowns)
            page.select_option('#interpretation', 'candidate')
            tentative = page.locator('#graph-paper [data-chosen="true"] ellipse[stroke-dasharray="4 3"]').count()
            assert tentative == n
        page.select_option('#epoch', 'r347')
        page.select_option('#interpretation', 'strict')
        page.locator('#position').fill('83'); page.locator('#position').dispatch_event('change')
        assert '6 yellow' in page.locator('#position-evidence').inner_text()
        assert 'R332-R-0037-0040' not in page.locator('#position-sources').inner_text()
        page.select_option('#epoch', 'r344')
        assert 'conflicting' in page.locator('#position-status').inner_text()
        assert 'R332-R-0037-0040' in page.locator('#position-sources').inner_text()
        page.select_option('#epoch', 'r347')
        page.locator('#position').fill('43'); page.locator('#position').dispatch_event('change')
        assert 'insufficient' in page.locator('#position-status').inner_text()
        assert page.locator('.bead.selected').count() > 1
        page.locator('#next-position').click()
        assert 'Position 44' == page.locator('#position-title').inner_text()
        page.locator('#numbers').check()
        assert page.locator('.paper-scroll').evaluate('(x) => x.classList.contains("show-numbers")')
        page.locator('#zoom').fill('2')
        page.locator('#zoom').dispatch_event('input')
        assert page.locator('#graph-paper').evaluate('(x) => x.style.width') == '200%'
        page.locator('#zoom').fill('1'); page.locator('#zoom').dispatch_event('input')
        # Select a displayed seam alias by actual browser event, then keyboard.
        alias = page.locator('.bead[data-side="right"]').first
        alias.dispatch_event('click')
        pos = alias.get_attribute('data-position')
        assert page.locator('#position-title').inner_text() == f'Position {pos}'
        member = page.locator('.bead[data-chosen="true"][data-position="17"]')
        member.focus(); page.keyboard.press('Enter')
        assert page.locator('#position-title').inner_text() == 'Position 17'
        if args.screenshots:
            page.locator('#pattern').scroll_into_view_if_needed()
            page.locator('.viewer').screenshot(path=str(args.screenshots / 'viewer.png'))
        results.append('desktop: two epochs, strict/provisional unknowns, sources, selection, seams, labels, zoom, keyboard')
        for width in [768, 390, 320]:
            page.set_viewport_size({'width': width, 'height': 844})
            page.goto(base, wait_until='networkidle')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
            page.locator('a[href="#pattern"]').first.click()
            page.select_option('#interpretation', 'candidate')
            page.locator('#position').fill('186'); page.locator('#position').dispatch_event('change')
            assert 'insufficient' in page.locator('#position-status').inner_text()
            if args.screenshots and width == 390:
                page.goto(base, wait_until='networkidle')
                page.screenshot(path=str(args.screenshots / 'mobile.png'))
            results.append(f'{width}px: no page overflow, navigation and controls work')
        # Verify loaded images including those inside initially closed details.
        page.set_viewport_size({'width': 1440, 'height': 1050})
        page.goto(base, wait_until='networkidle')
        page.evaluate('document.querySelectorAll("details").forEach(x => x.open = true)')
        for img in page.locator('img').all():
            img.scroll_into_view_if_needed()
            img.evaluate('(x) => x.loading = "eager"')
            img.evaluate('(x) => x.decode()')
            assert img.evaluate('(x) => x.naturalWidth > 0')
        page.goto(base + 'beads.html', wait_until='networkidle')
        assert page.locator('img').count() == 2
        assert all(img.evaluate('(x) => x.naturalWidth > 0') for img in page.locator('img').all())
        page.get_by_role('link', name='some simulated bracelets').click()
        assert page.locator('img').count() == 6
        page.get_by_role('link', name='movie', exact=True).click()
        assert 'not archived' in page.locator('h1').inner_text()
        assert not errors, errors
        assert not failed, failed
        assert all(urlsplit(url).netloc == urlsplit(base).netloc for url in requests), requests
        results.append('all image decodes; historical galleries; explicit missing-movie notice; zero script/request failures or external runtime requests')
        context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        nojs = context.new_page()
        nojs.goto(base, wait_until='networkidle')
        assert nojs.locator('#graph-paper .bead').count() == 984
        assert 'Independent confirmation is still missing' in nojs.locator('body').inner_text()
        assert nojs.locator('#viewer-controls').is_hidden()
        results.append('JavaScript disabled: narrative, SVG unknowns, limitations and links remain available')
        browser.close()
    print(json.dumps(dict(passed=True, base_url=base, checks=results), indent=2))


if __name__ == '__main__':
    main()
