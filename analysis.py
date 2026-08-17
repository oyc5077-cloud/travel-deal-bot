"""
LLM 호출 없이 순수 통계로 '이건 특가인가?'를 판정한다.
방법: 최근 가격 이력의 평균/표준편차 대비 오늘 가격이 얼마나 떨어졌는지(Z-score) 계산.
Z-score가 음수로 클수록 '평소보다 비정상적으로 싸다'는 뜻.
"""
import statistics
from db import get_history


def evaluate_deal(item_name: str, today_price: float,
                   z_threshold: float = 2.0, min_history: int = 7) -> dict:
    history = get_history(item_name, limit_days=90)
    prices = [row[0] for row in history]

    if len(prices) < min_history:
        return {
            "is_deal": False,
            "reason": f"이력 데이터 부족 ({len(prices)}/{min_history}일) - 판정 보류",
            "z_score": None,
            "avg_price": None,
        }

    avg = statistics.mean(prices)
    stdev = statistics.pstdev(prices) or 1.0  # 0 나눗셈 방지
    z_score = (today_price - avg) / stdev

    is_deal = z_score <= -z_threshold
    drop_pct = round((1 - today_price / avg) * 100, 1)

    return {
        "is_deal": is_deal,
        "reason": (
            f"평균 대비 {drop_pct}% 하락 (z={z_score:.2f})"
            if is_deal
            else f"평균 대비 {drop_pct}% 변동 - 특가 기준 미달"
        ),
        "z_score": round(z_score, 2),
        "avg_price": round(avg),
    }
