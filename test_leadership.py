import urllib.request
import json

def test_leadership_api():
    print('Testing Leadership Simulation API...')
    print('=' * 50)

    # Test the leadership simulation start endpoint
    url = 'http://127.0.0.1:8080/api/leadership/simulation/start'
    data = json.dumps({'user_id': 'test_user', 'scenario_type': 'team_conflict'}).encode('utf-8')
    headers = {'Content-Type': 'application/json'}

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print('✓ Leadership Simulation Start - SUCCESS')
            print(f'Status Code: {response.getcode()}')
            print(f'Simulation ID: {result.get("simulation_id")}')
            print(f'Scenario: {result.get("scenario", {}).get("title")}')
            print(f'Team Size: {len(result.get("team", []))}')

            # Test getting current scenario
            sim_id = result.get('simulation_id')
            if sim_id:
                scenario_url = f'http://127.0.0.1:8080/api/leadership/simulation/{sim_id}/scenario'
                try:
                    req2 = urllib.request.Request(scenario_url)
                    with urllib.request.urlopen(req2) as resp2:
                        scenario_result = json.loads(resp2.read().decode('utf-8'))
                        print('\n✓ Get Scenario - SUCCESS')
                        print(f'Scenario Title: {scenario_result.get("title")}')
                        print(f'Description: {scenario_result.get("description")[:100]}...')
                except Exception as e2:
                    print(f'\n✗ Get Scenario - ERROR: {e2}')

    except Exception as e:
        print(f'✗ Leadership Simulation Start - ERROR: {e}')

if __name__ == '__main__':
    test_leadership_api()