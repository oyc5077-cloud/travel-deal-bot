"""
전체 파이프라인 진입점.
GitHub Actions가 이 파일을 하루 몇 번 자동 실행한다.

흐름: config.yaml 읽기 -> 가격 수집 -> DB 저장 -> 리포트(HTML) 생성
"""
import json
import yaml

from db import init_db, insert_price
from collectors.flight_kiwi import fetch_cheapest_flight
from collectors.hotel_agoda import fetch_cheapest_hotel_price
from report import generate_report


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_flights(cfg: dict):
    for item in cfg.get("flights", []):
        print(f"[flight] {item['name']} 조회 중...")
        try:
            result = fetch_cheapest_flight(
                origin=item["origin"],
                destination=item["destination"],
                date_from=item["date_from"],
                date_to=item["date_to"],
                currency=item.get("currency", "KRW"),
            )
            if result:
                insert_price(
                    item_type="flight",
                    item_name=item["name"],
                    price=result["price"],
                    currency=result["currency"],
                    raw_meta=json.dumps(result, ensure_ascii=False),
                )
                print(f"  -> {result['price']} {result['currency']}")
            else:
                print("  -> 검색 결과 없음")
        except Exception as e:
            print(f"  -> 실패: {e}")


def run_hotels(cfg: dict):
    for item in cfg.get("hotels", []):
        print(f"[hotel] {item['name']} 조회 중...")
        try:
            result = fetch_cheapest_hotel_price(
                agoda_url=item["agoda_url"],
                check_in=item["check_in"],
                check_out=item["check_out"],
            )
            if result:
                insert_price(
                    item_type="hotel",
                    item_name=item["name"],
                    price=result["price"],
                    currency=result["currency"],
                    raw_meta=json.dumps(result, ensure_ascii=False),
                )
                print(f"  -> {result['price']} {result['currency']}")
            else:
                print("  -> 조회 실패")
        except Exception as e:
            print(f"  -> 실패: {e}")


def main():
    cfg = load_config()
    init_db()
    run_flights(cfg)
    run_hotels(cfg)
    generate_report()


if __name__ == "__main__":
    main()
