"""[0단계] 기상 자료를 내려받는다.

data/raw/seoul_weather_era5_2008_2023.csv 는 이 스크립트로 만든 파일이다.
저장소에 이미 들어 있으므로 평소에는 실행할 필요가 없다.
자료를 다시 받거나 기간을 바꾸고 싶을 때만 실행한다.

출처: Open-Meteo Historical Weather API (ERA5 재분석 자료)
      https://open-meteo.com/en/docs/historical-weather-api
      비상업적 이용 무료, 출처 표기 조건. 회원가입·API 키 불필요.

좌표는 서울시청(위도 37.5665, 경도 126.9780)이다. 격자 재분석 자료이므로
서울 안의 특정 관측소 실측값과는 조금 다를 수 있다.

실행:  python src/step0_collect_weather.py
"""

import pandas as pd
import requests

from config import FIRST_YEAR, LAST_YEAR, WEATHER_CSV

API_URL = "https://archive-api.open-meteo.com/v1/archive"

PARAMS = {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "start_date": f"{FIRST_YEAR}-01-01",
    "end_date": f"{LAST_YEAR}-12-31",
    "daily": ",".join([
        "temperature_2m_mean",
        "temperature_2m_max",
        "temperature_2m_min",
        "precipitation_sum",
        "relative_humidity_2m_mean",
    ]),
    "models": "era5",
    "timezone": "Asia/Seoul",
}

# 뒤 단계에서 쓰기 좋게 짧은 이름으로 바꾼다
RENAME = {
    "time": "date",
    "temperature_2m_mean": "avg_temp",
    "temperature_2m_max": "max_temp",
    "temperature_2m_min": "min_temp",
    "precipitation_sum": "rainfall",
    "relative_humidity_2m_mean": "humidity",
}


def main():
    response = requests.get(API_URL, params=PARAMS, timeout=60)
    response.raise_for_status()

    weather = pd.DataFrame(response.json()["daily"]).rename(columns=RENAME)
    weather = weather[list(RENAME.values())]

    if weather.isna().any().any():
        print("[주의] 값이 비어 있는 날이 있습니다:")
        print(weather[weather.isna().any(axis=1)].to_string(index=False))

    WEATHER_CSV.parent.mkdir(parents=True, exist_ok=True)
    weather.to_csv(WEATHER_CSV, index=False, encoding="utf-8-sig")

    print(f"저장: {WEATHER_CSV.name}")
    print(f"기간: {weather['date'].min()} ~ {weather['date'].max()} "
          f"(총 {len(weather):,}일)")


if __name__ == "__main__":
    main()
