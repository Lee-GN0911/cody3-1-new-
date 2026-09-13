"""5~7단계가 함께 쓰는 계산들.

같은 계산을 세 파일에 복사해 두면 한 곳만 고쳤을 때 결과가 어긋난다.
그래서 '평년 대비'로 바꾸는 계산은 여기 한 번만 적어두고 불러다 쓴다.
"""

import numpy as np
import pandas as pd

from config import WEEKLY_CSV

MIN_YEARS = 5           # 평년값을 만들 때 필요한 최소 연도 수
CLIMATE = ["avg_temp", "peak_temp", "hot_day_ratio", "rain_per_day", "humidity"]
LABELS = {
    "avg_temp": "평균기온",
    "peak_temp": "주간 최고기온",
    "hot_day_ratio": "폭염일 비율(33℃↑)",
    "rain_per_day": "강수량",
    "humidity": "습도",
}


def load_with_anomaly():
    """주 단위 자료를 읽고 '평년 대비' 값을 붙인다.

    같은 7월 3주끼리 비교해야 계절 효과에 속지 않는다. 그래서 모든 변수를
    '그 월·주차의 16년 평균'과 견준 값으로 바꿔둔다.
      - 모기: 평년 대비 배수 (index).  1.0이면 평년 수준
      - 기후: 평년 대비 차이 (_dev).   0이면 평년 수준
    """
    data = pd.read_csv(WEEKLY_CSV, parse_dates=["week_start"])
    group = data.groupby(["month", "week_of_month"])

    data["n_years"] = group["culex"].transform("size")
    data["culex_normal"] = group["culex"].transform("mean")
    for column in CLIMATE:
        data[f"{column}_normal"] = group[column].transform("mean")

    # 평년값을 만들 근거가 부족한 주차는 뺀다 (예: 4월 1주는 2개 연도뿐)
    data = data[data["n_years"] >= MIN_YEARS].copy()

    data["index"] = data["culex"] / data["culex_normal"]
    # 로그를 씌우면 '몇 % 변했나'로 읽을 수 있고, 큰 값의 영향도 줄어든다.
    # 0마리인 주가 있어 +1을 해준다.
    data["log_index"] = np.log((data["culex"] + 1) / (data["culex_normal"] + 1))
    for column in CLIMATE:
        data[f"{column}_dev"] = data[column] - data[f"{column}_normal"]

    # 몇 주 전인지 세기 위한 통짜 주차 번호 (4월 1주 = 1 … 11월 5주 = 40)
    data["week_seq"] = (data["month"] - 4) * 5 + data["week_of_month"]
    return data.sort_values(["year", "week_seq"]).reset_index(drop=True)


def shift_weeks(data, columns, lag):
    """`lag`주 전의 값을 같은 행에 붙여준다.

    단순히 한 칸씩 밀면(shift) 안 된다. 겨울에는 자료가 없어서
    '작년 11월'과 '올해 4월'이 이웃처럼 붙어버리기 때문이다.
    그래서 같은 연도 안에서, 주차 번호를 기준으로 맞춘다.
    """
    past = data[["year", "week_seq"] + columns].copy()
    past["week_seq"] = past["week_seq"] + lag
    past = past.rename(columns={c: f"{c}_lag{lag}" for c in columns})
    return data.merge(past, on=["year", "week_seq"], how="inner")


def zscore(series):
    """평균 0, 표준편차 1로 바꾼다. 단위가 다른 요인을 나란히 비교하려면 필요하다."""
    return (series - series.mean()) / series.std(ddof=0)
