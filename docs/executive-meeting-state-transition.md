# Executive Meeting State Transition

```mermaid
flowchart TD
    A[Monthly Summary] --> B[Agenda Generation]
    B --> C[AI Agents Debate]
    C --> D[Decision Options (A/B/C)]
    D --> E[CEO Decision]
    E --> F[Apply Decision]
    F --> G[Meeting Minutes]
    G --> H[Dashboard Summary]
```

## フローの説明

- `Monthly Summary`: 月次レポートと数値をもとに会議の基礎データを構築します。
- `Agenda Generation`: 重要テーマを `MeetingAgendaItem` にまとめ、AI 役員向けに議題を整理します。
- `AI Agents Debate`: CFO / COO / CMO / CHRO がそれぞれの視点で議論を展開します。
- `Decision Options (A/B/C)`: 攻め・守り・バランスの選択肢を提示します。
- `CEO Decision`: CEO が最終案を選択します。
- `Apply Decision`: 選択された方針をシステムに反映し、予測を更新します。
- `Meeting Minutes`: 会議の議事録を生成し、意思決定の根拠を記録します。
- `Dashboard Summary`: 会議結果とリスク評価をダッシュボードに表示します。
