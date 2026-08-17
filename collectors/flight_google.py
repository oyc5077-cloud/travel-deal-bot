"""
fast-flights 라이브러리로 Google Flights 최저가를 조회한다.
가입/API 키가 전혀 필요 없다 (완전 무료).

주의: 공식 API가 아니라 Google Flights 페이지 구조를 이용한 방식이라,
구글이 페이지를 바꾸면 라이브러리 업데이트가 필요할 수 있습니다.
GitHub: https://github.com/AWeirdDev/flights
"""
from fast_flights import FlightData, Passengers, get_flights


def fetch_cheapest_flight(origin: str, destination: str,
                           date_from: str, date_to: str,
                           currency: str = "KRW") -> dict | None:
    """
    date_from ~ date_to 사이 여러 날짜를 훑어서 가장 싼 편도 요금을 찾는다.
    (fast-flights는 특정 '한 날짜' 조회 방식이라, 날짜 범위를 순회한다)
    """
    from datetime import datetime, timedelta

    d_from = datetime.strptime(date_from, "%Y-%m-%d")
    d_to = datetime.strptime(date_to, "%Y-%m-%d")

    total_days = (d_to - d_from).days
    step = max(1, total_days // 10)

    best = None
    date = d_from
    while date <= d_to:
        try:
            result = get_flights(
                flight_data=[
                    FlightData(
                        date=date.strftime("%Y-%m-%d"),
                        from_airport=origin,
                        to_airport=destination,
                    )
                ],
                trip="one-way",
                seat="economy",
                passengers=Passengers(
                    adults=1, children=0, infants_in_seat=0, infants_on_lap=0
                ),
                fetch_mode="fallback",
            )
            if result.flights:
                cheapest_today = min(
                    _parse_price(f.price) for f in result.flights if f.price
                )
                if best is None or cheapest_today < best["price"]:
                    best = {
                        "price": cheapest_today,
                        "currency": currency,
                        "date": date.strftime("%Y-%m-%d"),
                    }
        except Exception as e:
            print(f"  [flight_google] {date.date()} 조회 실패: {e}")

        date += timedelta(days=step)

    return best


def _parse_price(price_text: str) -> float:
    digits = "".join(ch for ch in str(price_text) if ch.isdigit())
    return float(digits) if digits else 0.0
