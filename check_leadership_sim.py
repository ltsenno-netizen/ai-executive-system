import urllib.request, json

js = json.dumps({'user_id': 'test_user', 'scenario_type': 'team_conflict', 'difficulty': 'medium'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8081/api/leadership/simulation/start', data=js, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as resp:
    print('status', resp.getcode())
    print(json.dumps(json.load(resp), ensure_ascii=False, indent=2))
