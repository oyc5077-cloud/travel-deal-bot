"""
fast-flights 라이브러리로 Google Flights 최저가를 조회한다.
가입/API 키가 전혀 필요 없다 (완전 무료).

주의:
- 공식 API가 아니라 Google Flights 페이지 구조를 이용한 방식이라,
  가끔 응답 없이 멈추는 요청이 있을 수 있어 요청마다 타임아웃을 강제한다.
- 라이브러리 버전이 올라가면 인터페이스가 또 바뀔 수 있습니다.
  최신 사용법: https://github.com/AWeirdDev/flights
"""
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from fast_flights import FlightQuery, Passengers, create_query, get_flights

REQUEST_TIMEOUT_SEC = 25   # 요청 1건당 최대 대기시간
MAX_DATE_SAMPLES = 4       # 노선당 조회할 날짜 샘플 개수 (많을수록 오래 걸림)


def fetch_cheapest_flight(origin: str, destination: str,
                           date_from: str, date_to: str,
                           currency: str = "KRW") -> dict | None:
    d_from = datetime.strptime(date_from, "%Y-%m-%d")
    d_to = datetime.strptime(date_to, "%Y-%m-%d")

    total_days = (d_to - d_from).days
    step = max(1, total_days // MAX_DATE_SAMPLES)

    best = None
    date = d_from
    checked = 0
    while date <= d_to and checked < MAX_DATE_SAMPLES:
        checked += 1
        result = _fetch_one_date_with_timeout(origin, destination, date.strftime("%Y-%m-%d"))
        if result is not None:
            if best is None or result < best["price"]:
                best = {"price": result, "currency": currency, "date": date.strftime("%Y-%m-%d")}
        date += timedelta(days=step)

    return best


def _fetch_one_date_with_timeout(origin: str, destination: str, date_str: str):
    """한 날짜 조회를 별도 스레드에서 실행하고, 정해진 시간 안에 안 끝나면 포기한다."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_fetch_one_date, origin, destination, date_str)
        try:
            return future.result(timeout=REQUEST_TIMEOUT_SEC)
        except FutureTimeoutError:
            print(f"  [flight_google] {date_str} 타임아웃({REQUEST_TIMEOUT_SEC}초) - 건너뜀")
            return None
        except Exception as e:
            print(f"  [flight_google] {date_str} 조회 실패: {e}")
            return None


def _fetch_one_date(origin: str, destination: str, date_str: str):
    query = create_query(
        flights=[FlightQuery(date=date_str, from_airport=origin, to_airport=destination)],
        trip="one-way",
        seat="economy",
        passengers=Passengers(adults=1),
    )
    results = get_flights(query)
    prices = [_parse_price(f.price) for f in results if getattr(f, "price", None)]
    return min(prices) if prices else None


def _parse_price(price_text) -> float:
    digits = "".join(ch for ch in str(price_text) if ch.isdigit())
    return float(digits) if digits else 0.0
