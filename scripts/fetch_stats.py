import json, os, datetime as d, collections, urllib.request as u
USER = 'matteocalviello'
def g(p):
    r = u.Request('https://api.github.com' + p, headers={'Authorization': 'Bearer ' + os.environ.get('GH_TOKEN', ''), 'Accept': 'application/vnd.github+json'})
    return json.load(u.urlopen(r))
me = g('/users/' + USER)
repos = [r for r in g(f'/users/{USER}/repos?per_page=100') if not r['fork']]
now = d.datetime.now(d.timezone.utc); weeks = [0] * 12
for pg in (1, 2, 3):
    for e in g(f'/users/{USER}/events/public?per_page=100&page={pg}'):
        if e['type'] != 'PushEvent': continue
        age = (now - d.datetime.fromisoformat(e['created_at'].replace('Z', '+00:00'))).days
        if age < 84: weeks[11 - age // 7] += e['payload'].get('size') or len(e['payload'].get('commits', []))
langs = collections.Counter(r['language'] for r in repos if r['language'])
os.makedirs('data', exist_ok=True)
json.dump({'updated': now.strftime('%b %d, %Y'), 'repos': me['public_repos'], 'followers': me['followers'],
           'stars': sum(r['stargazers_count'] for r in repos), 'commits': sum(weeks),
           'languages': dict(langs.most_common(6)), 'weeks': weeks}, open('data/stats.json', 'w'), indent=1)
