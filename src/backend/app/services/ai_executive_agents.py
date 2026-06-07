from typing import Dict, List

EXECUTIVE_ROLES = {
    'CFO': {
        'focus': 'Cash, investment, risk, capital policy',
        'concerns': [
            'cash reserves and liquidity',
            'investment / return balance',
            'financial risk management',
        ],
    },
    'COO': {
        'focus': 'Execution capacity, project load, operational risk',
        'concerns': [
            'resource overload and delays',
            'execution risk for tranches',
            'process reliability',
        ],
    },
    'CMO': {
        'focus': 'Market demand, competition, customer acquisition',
        'concerns': [
            'market momentum and timing',
            'go-to-market effectiveness',
            'brand and campaign ROI',
        ],
    },
    'CHRO': {
        'focus': 'Organization health, headcount, morale',
        'concerns': [
            'workload and retention',
            'capacity to hire and onboard',
            'culture and leadership alignment',
        ],
    },
}


def build_executive_agent(role: str, agenda: List[Dict[str, object]]) -> Dict[str, object]:
    profile = EXECUTIVE_ROLES.get(role, {})
    focus = profile.get('focus', 'Strategic leadership')
    concerns = profile.get('concerns', [])
    relevant_items = [item for item in agenda if role in item.get('category', '') or item.get('category') in {'PL', 'Portfolio', 'Operations', 'Issues', 'Improvements'}]

    summary_lines = []
    for item in relevant_items[:3]:
        summary_lines.append(f"{item.get('title')}: {item.get('summary')}")

    opening_statement = (
        f"As {role}, I am focused on {focus}. "
        f"Key points include {'; '.join(summary_lines[:2])}."
    )
    recommendation = (
        f"I recommend balancing {focus.lower()} with strategic continuity. "
        "Favor decisions that protect strengths without blocking growth."
    )

    return {
        'role': role,
        'focus': focus,
        'opening_statement': opening_statement,
        'recommendation': recommendation,
        'concerns': concerns,
    }
