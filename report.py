"""
db에 쌓인 최신 가격 + 특가 판정 결과를 docs/index.html 로 렌더링한다.
docs/ 를 GitHub Pages 소스로 지정하면, 커밋될 때마다 자동으로
https://<username>.github.io/<repo>/ 에서 결과를 확인할 수 있다. (완전 무료)
"""
from datetime import datetime
from db import get_all_latest
from analysis import evaluate_deal

OUTPUT_PATH = "docs/index.html"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>여행 특가 모니터링</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; padding: 0 16px; }}
  h1 {{ font-size: 20px; }}
  .updated {{ color: #888; font-size: 13px; margin-bottom: 24px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ text-align: left; padding: 10px 8px; border-bottom: 1px solid #eee; font-size: 14px; }}
  .deal {{ background: #fff4e5; font-weight: bold; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }}
  .badge-deal {{ background: #ffb020; color: #3d1f00; }}
  .badge-normal {{ background: #eee; color: #666; }}
</style>
</head>
<body>
  <h1>✈️ 여행 특가 모니터링</h1>
  <div class="updated">마지막 갱신: {updated_at} (UTC)</div>
  <table>
    <tr><th>구분</th><th>이름</th><th>현재가</th><th>판정</th><th>비고</th></tr>
    {rows}
  </table>
</body>
</html>
"""

ROW_TEMPLATE = """<tr class="{row_class}">
  <td>{item_type}</td>
  <td>{item_name}</td>
  <td>{price:,.0f} {currency}</td>
  <td><span class="badge {badge_class}">{badge_text}</span></td>
  <td>{reason}</td>
</tr>"""


def generate_report():
    rows_html = []
    for item_type, item_name, price, currency, checked_at in get_all_latest():
        verdict = evaluate_deal(item_name, price)
        is_deal = verdict["is_deal"]
        rows_html.append(
            ROW_TEMPLATE.format(
                row_class="deal" if is_deal else "",
                item_type="항공" if item_type == "flight" else "호텔",
                item_name=item_name,
                price=price,
                currency=currency,
                badge_class="badge-deal" if is_deal else "badge-normal",
                badge_text="특가" if is_deal else "일반",
                reason=verdict["reason"],
            )
        )

    html = HTML_TEMPLATE.format(
        updated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        rows="\n".join(rows_html) or "<tr><td colspan='5'>아직 데이터가 없습니다.</td></tr>",
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[report] {OUTPUT_PATH} 생성 완료")
