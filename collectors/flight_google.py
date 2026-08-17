"""
fast-flights 라이브러리로 Google Flights 최저가를 조회한다.
가입/API 키가 전혀 필요 없다 (완전 무료).

주의: 공식 API가 아니라 Google Flights 페이지 구조를 이용한 방식이라,
라이브러리 버전이 올라가면 인터페이스가 또 바뀔 수 있습니다.
문제가 생기면 최신 사용법을 확인하세요: https://github.com/AWeirdDev/flights
"""
from datetime import datetime, timedelta
from fast_flights import FlightQuery, Passengers, create_query, get_flights


def fetch_cheapest_flight(origin: str, destination: str,
                           date_from: str, date_to: str,
                           currency: str = "KRW") -> dict | None:
    d_from = datetime.strptime(date_from, "%Y-%m-%d")
    d_to = datetime.strptime(date_to, "%Y-%m-%d")

    total_days = (d_to - d_from).days
    step = max(1, total_days // 10)

    best = None
    date = d_from
    while date <= d_to:
        try:
            query = create_query(
                flights=[
                    FlightQuery(
                        date=date.strftime("%Y-%m-%d"),
                        from_airport=origin,
                        to_airport=destination,
                    )
                ],
                trip="one-way",
                seat="economy",
                passengers=Passengers(adults=1),
            )
            results = get_flights(query)

            prices = [
                _parse_price(f.price) for f in results if getattr(f, "price", None)
            ]
            if prices:
                cheapest_today = min(prices)
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


def _parse_price(price_text) -> float:
    digits = "".join(ch for ch in str(price_text) if ch.isdigit())
    return float(digits) if digits else 0.0


def _parse_price(price_text: str) -> float:
    digits = "".join(ch for ch in str(price_text) if ch.isdigit())
    return float(digits) if digits else 0.0
