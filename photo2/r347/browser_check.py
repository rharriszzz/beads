"""Check the local questionnaire, persistence, source identity and exports."""
from pathlib import Path
import json

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'photo2/r347/review'


def main():
    errors, failed = [], []
    questions = json.loads((OUT/'questions.json').read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1450, 'height': 1050})
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('requestfailed', lambda r: failed.append(r.url))
        page.goto((OUT/'index.html').as_uri())
        page.wait_for_function('window.R347_READY')
        page.evaluate('localStorage.clear()')
        page.reload()
        page.wait_for_function('window.R347_READY')
        assert page.locator('.question').count() == 10
        assert page.locator('.question:visible').count() == 3
        assert page.locator('#progress').inner_text().startswith('0/10')
        for q in questions:
            assert page.locator(f'#q{q["number"]} .key').inner_text().startswith('1: '+q['id'])
        page.screenshot(path=str(OUT/'desktop.png'), full_page=False)
        page.locator('#q1').screenshot(path=str(OUT/'question-1.png'))
        page.locator('#stage').select_option('completion')
        assert page.locator('.question:visible').count() == 7
        page.locator('#q5 details summary').click()
        page.locator('#q5 .reference-button', has_text='K-1740-1575').click()
        assert 'reference only' in page.locator('#q5 .view-reference').inner_text().lower()
        assert page.locator('#q5 .view-reference select').count() == 0
        page.locator('#context').select_option('100')
        page.locator('#numbers').uncheck()
        page.locator('#numbers').check()
        page.locator('#context').select_option('60')
        page.locator('#stage').select_option('contradictions')
        page.locator('#q1 select[data-field="identity"]').select_option('uncertain')
        page.locator('#q1 select[data-field="pigment"]').select_option('uncertain')
        page.locator('#q1 select[data-field="basis"]').select_option('current_photo')
        page.locator('#q1 textarea').fill('Interface test only; no maker judgment.')
        assert page.locator('#progress').inner_text().startswith('1/10')
        page.reload()
        page.wait_for_function('window.R347_READY')
        assert page.locator('#q1 select[data-field="pigment"]').input_value() == 'uncertain'
        assert page.locator('#q1 textarea').input_value().startswith('Interface test')
        candidate = page.evaluate('DATA.candidate')
        page.locator('#chart').fill(candidate[17:]+candidate[:17])
        assert 'Exact match' in page.locator('#chart-result').inner_text()
        page.locator('#chart').fill(candidate[::-1])
        assert 'reverse' in page.locator('#chart-result').inner_text()
        page.locator('#chart').fill('R Y B ?')
        assert 'Use only' in page.locator('#chart-result').inner_text()
        page.locator('#chart').fill('R Y B')
        assert 'differs' in page.locator('#chart-result').inner_text()
        page.locator('#chart').fill('')
        with page.expect_download() as pending:
            page.locator('#export').click()
        download = pending.value
        path = Path('/tmp/beads-r347-interface-test-answers.json')
        download.save_as(path)
        export = json.loads(path.read_text())
        assert len(export['question_manifest']) == 10
        assert export['answers'][questions[0]['id']]['pigment'] == 'uncertain'
        assert not any(q['id'] in export['answers'] for q in questions[1:])
        page.locator('#import').set_input_files(str(path))
        page.wait_for_function("document.querySelector('#save-status').textContent.startsWith('Imported answers')")
        assert 'Imported answers' in page.locator('#save-status').inner_text()
        page.locator('#copy').click()
        assert 'Q1 R332-R-0037-0040' in page.locator('#summary').input_value()
        page.evaluate('localStorage.clear()')
        page.reload()
        page.wait_for_function('window.R347_READY')
        assert page.locator('#progress').inner_text().startswith('0/10')
        page.set_viewport_size({'width': 390, 'height': 844})
        page.screenshot(path=str(OUT/'narrow.png'))
        overflow = page.evaluate("[...document.querySelectorAll('main *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1&&e.getBoundingClientRect().width).map(e=>({tag:e.tagName,id:e.id,width:e.getBoundingClientRect().width,text:e.textContent.slice(0,60)})).slice(0,12)")
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), overflow
        page.context.set_offline(True)
        page.reload()
        page.wait_for_function('window.R347_READY')
        assert page.locator('.question:visible').count() == 3
        assert page.evaluate('document.querySelectorAll("select[data-field=pigment]").length') == 10
        page.context.set_offline(False)
        page.goto('http://127.0.0.1:8347/photo2/r347/review/')
        page.wait_for_function('window.R347_READY')
        assert page.locator('#progress').inner_text().startswith('0/10')
        assert page.locator('#evidence').input_value() == 'both_pending'
        assert not errors, errors
        assert not failed, failed
        browser.close()
    (OUT/'browser-verification.json').write_text(json.dumps(dict(
        passed=True, questions=10, contradictions_first=3, completion_checks=7,
        initial_answers=0, prior_approvals_not_requestioned=True,
        native_keys_target1=True, wider_context=True, offline=True, narrow=True,
        local_persistence=True, JSON_export_import=True, summary_copy=True,
        localhost_URL=True,
        cyclic_chart_comparison=True, reverse_chart_comparison=True,
        test_answers='Synthetic UI test data only, saved under /tmp; not maker judgments',
        errors=errors, failed_requests=failed), indent=2)+'\n')
    print('PASS R347 questionnaire browser checks')


if __name__ == '__main__':
    main()
