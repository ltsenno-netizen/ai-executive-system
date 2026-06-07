import requests

def test_api():
    base_url = 'http://127.0.0.1:12001/api'

    # Test units endpoint
    print("Testing /api/talent/units...")
    try:
        r = requests.get(f'{base_url}/talent/units')
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            units = r.json()
            print(f"Units count: {len(units)}")
            for unit in units:
                print(f"  - {unit['name']}: {unit['headcount']}名, roles: {unit['roles']}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test inbasket endpoint
    print("\nTesting /api/talent/unit/マネージャー課/inbasket...")
    try:
        r = requests.get(f'{base_url}/talent/unit/マネージャー課/inbasket?n=3')
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Unit: {data['unit_name']}")
            print(f"Inbasket count: {len(data['inbasket'])}")
            for task in data['inbasket'][:2]:  # Show first 2
                print(f"  - {task['title']} ({task['priority']})")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Test member creation
    print("\nTesting member creation...")
    member_data = {
        "id": "test_member_001",
        "name": "テスト太郎",
        "role": "Manager",
        "experience_years": 3,
        "strengths": ["リーダーシップ", "コミュニケーション"],
        "challenges": ["細かい作業"],
        "current_tasks": [],
        "development_plan_id": None
    }
    try:
        r = requests.post(f'{base_url}/talent/member', json=member_data)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Member created successfully")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()