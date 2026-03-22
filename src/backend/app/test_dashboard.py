import urllib.request
import json
import time

def test_dashboard_api():
    """ダッシュボード API をテスト"""
    time.sleep(2)  # サーバー起動待ち
    
    PORT = 12000  # Change port to 12000
    
    print("\n" + "="*70)
    print("KPI ダッシュボード API テスト (Port 8001)")
    print("="*70 + "\n")
    
    # テスト1: 個別ダッシュボード取得
    print("【テスト1】ソフトウェア開発事業のダッシュボード")
    print("-"*70)
    try:
        url = f"http://127.0.0.1:{PORT}/api/dashboard/biz_001?month=2026-03"
        with urllib.request.urlopen(url) as response:
            dashboard = json.loads(response.read().decode('utf-8'))
            print(f"✓ ダッシュボード取得成功")
            print(f"  事業名: {dashboard['business_name']}")
            print(f"  ヘルススコア: {dashboard['overall_health_score']} 点")
            print(f"  経営層向けサマリー: {dashboard['executive_summary']}")
            print(f"\n  【主要KPI】")
            print(f"  - 売上高: {dashboard['revenue_metrics']['current_value']:,.0f}円")
            print(f"    前月比: {dashboard['revenue_metrics']['month_over_month_change']:+.1f}%")
            print(f"  - 利益率: {dashboard['profit_margin_metrics']['current_value']:.1f}%")
            print(f"    前月比: {dashboard['profit_margin_metrics']['month_over_month_change']:+.1f}%ポイント")
            print(f"  - 原価率: {dashboard['cost_ratio_metrics']['current_value']:.1f}%")
            print(f"\n  【主要インサイト】")
            for insight in dashboard['key_insights'][:2]:
                print(f"  - {insight}")
            print(f"\n  【アクション提案】")
            for rec in dashboard['recommendations'][:2]:
                print(f"  - {rec}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    
    # テスト2: 月次報告書
    print("\n\n【テスト2】月次経営ダッシュボード報告書")
    print("-"*70)
    try:
        url = f"http://127.0.0.1:{PORT}/api/dashboard/report/2026-03"
        with urllib.request.urlopen(url) as response:
            report = json.loads(response.read().decode('utf-8'))
            print(f"✓ 報告書取得成功")
            print(f"  対象月: {report['report_month']}")
            print(f"  企業全体ヘルススコア: {report['company_health_score']} 点")
            print(f"  企業サマリー: {report['company_summary']}")
            print(f"\n  【事業別ダッシュボード数】: {len(report['business_dashboards'])}")
            for dashboard in report['business_dashboards'][:3]:
                print(f"    - {dashboard['business_name']}: ハルススコア {dashboard['overall_health_score']}")
            print(f"\n  【事業間比較インサイト】")
            for insight in report['cross_business_insights']:
                print(f"    - {insight}")
            print(f"\n  【経営層向け戦略提案】")
            for rec in report['strategic_recommendations'][:2]:
                print(f"    - {rec}")
            if report['urgent_alerts']:
                print(f"\n  【緊急アラート】")
                for alert in report['urgent_alerts']:
                    print(f"    ⚠ {alert['message']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    
    # テスト3: ヘルススコア取得
    print("\n\n【テスト3】クラウドサービス事業のヘルススコア")
    print("-"*70)
    try:
        url = f"http://127.0.0.1:{PORT}/api/dashboard/health-score/biz_003?month=2026-03"
        with urllib.request.urlopen(url) as response:
            health = json.loads(response.read().decode('utf-8'))
            print(f"✓ ヘルススコア取得成功")
            print(f"  事業名: {health['business_name']}")
            print(f"  ヘルススコア: {health['health_score']} 点")
            print(f"  レベル: {health['level']}")
            print(f"  サマリー: {health['summary']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    
    # テスト4: 企業全体比較
    print("\n\n【テスト4】企業全体の事業別KPI比較")
    print("-"*70)
    try:
        url = f"http://127.0.0.1:{PORT}/api/dashboard/comparison?month=2026-03"
        with urllib.request.urlopen(url) as response:
            comparison = json.loads(response.read().decode('utf-8'))
            print(f"✓ 比較データ取得成功")
            print(f"  企業全体ヘルススコア: {comparison['company_health_score']} 点")
            print(f"  総売上: {comparison['total_revenue']:,.0f}円")
            print(f"\n  【事業別ランキング】 (ヘルススコア順)")
            for i, biz in enumerate(comparison['businesses'][:3], 1):
                print(f"    {i}. {biz['business_name']}: {biz['health_score']} 点")
                print(f"       売上: {biz['revenue']:,.0f}円 | 利益率: {biz['profit_margin']:.1f}%")
            if comparison['alerts']:
                print(f"\n  【緊急アラート】")
                for alert in comparison['alerts']:
                    print(f"    - {alert['business_name']}: {alert['alert_type']}")
    except Exception as e:
        print(f"✗ エラー: {e}")
    
    print("\n" + "="*70)
    print("✓ すべてのテストが完了しました")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_dashboard_api()
