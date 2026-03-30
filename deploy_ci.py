#!/usr/bin/env python3
"""
MPEP Pages — CI Deploy Script
Runs in GitHub Actions. Detects which HTML files changed in the last commit
and deploys only those to WordPress.
"""

import json, os, re, subprocess, sys
import requests
from requests.auth import HTTPBasicAuth

# ── Config ────────────────────────────────────────────────────────────────────
WP_BASE   = 'https://mechanicalpeexamprep.com/wp-json/wp/v2'
WP_USER   = 'dan'
WP_PASS   = os.environ['WP_PASSWORD']   # set as GitHub Secret
CACHE_URL = 'https://mechanicalpeexamprep.com/wp-json/elementor/v1/cache'

with open('pages.json') as f:
    PAGES = json.load(f)

# ── Helpers ───────────────────────────────────────────────────────────────────
def build_wp_content(html: str) -> str:
    """Convert standalone HTML file to WordPress wp:html block content."""
    head_m = re.search(r'<head>(.*?)</head>', html, re.DOTALL)
    body_m = re.search(r'<body>(.*?)</body>', html, re.DOTALL)
    head   = head_m.group(1) if head_m else ''
    body   = body_m.group(1) if body_m else html
    head_tags = '\n'.join(re.findall(r'<(?:link|style)[^>]*>(?:.*?</style>)?', head, re.DOTALL))
    return f'<!-- wp:html -->\n{head_tags}\n{body}\n<!-- /wp:html -->'

def deploy_page(filename: str) -> bool:
    info   = PAGES[filename]
    wp_id  = info['wp_id']
    title  = info['title']
    auth   = HTTPBasicAuth(WP_USER, WP_PASS)

    with open(filename) as f:
        html = f.read()

    content = build_wp_content(html)
    r = requests.post(
        f'{WP_BASE}/pages/{wp_id}',
        json={
            'content': content,
            'meta': {
                '_elementor_edit_mode': '',
                '_elementor_data': '[]',
                'template': 'elementor_canvas',
            }
        },
        auth=auth,
    )
    ok = r.status_code == 200
    status = '✅' if ok else f'❌ (HTTP {r.status_code})'
    print(f'  {status} {title} → mechanicalpeexamprep.com{info["url"]}')
    return ok

def clear_elementor_cache():
    auth = HTTPBasicAuth(WP_USER, WP_PASS)
    r = requests.delete(CACHE_URL, auth=auth)
    print(f'\n  Elementor cache cleared ({r.status_code})')

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    # Detect which HTML files changed in the last commit
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
        capture_output=True, text=True
    )
    changed = [f for f in result.stdout.strip().splitlines()
               if f.endswith('.html') and f in PAGES]

    if not changed:
        print('No HTML page files changed in this commit. Nothing to deploy.')
        sys.exit(0)

    print(f'Deploying {len(changed)} page(s)...\n')
    results = []
    for filename in changed:
        results.append(deploy_page(filename))

    clear_elementor_cache()

    failed = results.count(False)
    if failed:
        print(f'\n{failed} deployment(s) failed.')
        sys.exit(1)
    else:
        print(f'\nAll {len(changed)} page(s) deployed successfully.')

if __name__ == '__main__':
    main()
