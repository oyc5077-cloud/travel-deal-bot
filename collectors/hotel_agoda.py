"""
아고다는 개인이 쓸 수 있는 공식 가격 조회 API가 없어서,
Playwright로 검색 결과 페이지를 열어 화면에 보이는 최저가를 읽어온다.

주의:
- 아고다 이용약관상 자동화 접근은 회색지대입니다. 요청 빈도를 낮게(하루 1~2회)
  유지하고, 개인 모니터링 용도로만 사용하세요.
- 페이지 구조는 아고다가 언제든 바꿀 수 있어서, 셀렉터가 깨지면 손봐야 합니다.
"""
from playwright.sync_api import sync_playwright

PRICE_SELECTOR = "[data-selenium='display-price']"


def fetch_cheapest_hotel_price(agoda_url: str, check_in: str, check_out: str) -> dict | None:
    full_url = f"{agoda_url}&checkIn={check_in}&checkOut={check_out}&sortBy=PriceAsc"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
            )
        )
        try:
            page.goto(full_url, timeout=30000)
            page.wait_for_selector(PRICE_SELECTOR, timeout=15000)
            price_text = page.locator(PRICE_SELECTOR).first.inner_text()
            price = _parse_price(price_text)
            return {"price": price, "currency": "KRW", "url": full_url}
        except Exception as e:
            print(f"[hotel_agoda] 조회 실패: {e}")
            return None
        finally:
            browser.close()


def _parse_price(text: str) -> float:
    digits = "".join(ch for ch in text if ch.isdigit())
    return float(digits) if digits else 0.0
