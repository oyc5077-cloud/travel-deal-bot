# 여행 특가 모니터링 봇 (완전 무료 버전)

항공권/호텔 가격을 자동으로 주기 조회하고, 통계적으로 "평소보다 비정상적으로 싼가"를
판정해서 GitHub Pages 리포트로 보여주는 시스템입니다. 서버 비용, DB 비용, AI API 비용
없이 전부 무료 티어로만 구성되어 있습니다.

## 1. 필요한 것 (전부 무료)

1. **GitHub 계정** (이미 있다고 가정)
2. **Kiwi Tequila API 키** — https://tequila.kiwi.com/portal/login 에서 무료 가입 후 발급
   (일 호출 한도가 있지만 개인 모니터링 용도로는 충분합니다)
3. 이 프로젝트를 자신의 GitHub 저장소로 업로드

## 2. 설치 순서

### (1) 저장소 생성 및 업로드
```bash
# 로컬에서
cd travel-deal-bot
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/<your-id>/travel-deal-bot.git
git push -u origin main
```

### (2) GitHub Secrets에 API 키 등록
저장소 → Settings → Secrets and variables → Actions → New repository secret
- Name: `KIWI_API_KEY`
- Value: 발급받은 Kiwi API 키

### (3) GitHub Pages 활성화
저장소 → Settings → Pages → Source를 `main` 브랜치의 `/docs` 폴더로 지정
→ 저장하면 `https://<your-id>.github.io/travel-deal-bot/` 에서 리포트를 볼 수 있습니다.

### (4) Actions 권한 확인
저장소 → Settings → Actions → General → Workflow permissions에서
"Read and write permissions" 선택 (자동 커밋을 위해 필요)

### (5) 모니터링할 노선/호텔 수정
`config.yaml` 파일을 열어 원하는 출발지/도착지/날짜, 아고다 검색 URL로 수정하세요.
아고다 URL은 아고다에서 원하는 지역을 검색한 뒤 주소창의 URL을 그대로 복사하면 됩니다.

### (6) 첫 실행
저장소 → Actions 탭 → "Travel Deal Scan" → "Run workflow" 버튼으로 수동 실행해서
정상 작동하는지 확인하세요. 이후엔 매일 자동으로 하루 2회(한국시간 09시, 21시) 실행됩니다.

## 3. 결과 확인 (수동 확인 방식)

- `https://<your-id>.github.io/travel-deal-bot/` 접속 → 표에서 "특가" 배지가 붙은 항목 확인
- 더 깊게 분석하고 싶으면, 이 페이지 내용을 복사해서 **claude.ai 무료 웹 채팅**에 붙여넣고
  "이 중에 진짜 살만한 게 뭐야?", "이 노선 다음 달엔 더 싸질까?" 같은 질문을 자유롭게 하세요.
  (API를 안 쓰고 웹 채팅을 쓰면 이 부분도 0원입니다.)

## 4. 로컬에서 직접 테스트하고 싶다면

```bash
pip install -r requirements.txt
playwright install chromium
export KIWI_API_KEY="발급받은 키"
python main.py
```

## 5. 나중에 업그레이드하고 싶다면

- **탐지 민감도 조정**: `config.yaml`의 `anomaly.z_score_threshold` 값을 낮추면
  더 자주, 높이면 더 드물게 특가로 판정됩니다.
- **알림 추가**: 텔레그램 봇 토큰을 발급받아 `main.py` 끝에 발송 로직을 붙이면
  push 알림도 무료로 추가할 수 있습니다 (Telegram Bot API 자체는 완전 무료).
- **AI 판단 추가**: 예산이 생기면 `analysis.py`의 통계 판정 뒤에 Claude API 호출을
  붙여서, 통계로 걸러진 후보만 AI가 다시 한번 자연어로 검토하게 하면 비용을
  최소화하면서 AI 판단력을 더할 수 있습니다.

## 참고사항

- 아고다는 공식 개인용 가격 API가 없어 Playwright로 화면을 읽는 방식이라,
  아고다가 페이지 구조를 바꾸면 `collectors/hotel_agoda.py`의 셀렉터를 수정해야 할 수 있습니다.
- 자동화 스크래핑은 이용약관상 회색지대이니, 호출 빈도를 낮게 유지하고
  개인 모니터링 용도로만 사용하세요.
- 오류운임(직원 실수로 인한 초특가)은 시스템이 통계적으로 감지할 수는 있지만,
  발견 즉시 몇 분 안에 사라지는 경우가 많아 수동 확인 방식(하루 2회)으로는
  놓칠 가능성이 높습니다. 이런 걸 노리신다면 알림 추가(위 5번 항목)를 권장합니다.
