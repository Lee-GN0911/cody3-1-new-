"""[1단계] 원자료를 읽어서 '주 단위 분석표' 한 장으로 만든다.

원자료는 두 개다.
  - 모기: 서울시 보건환경연구원 유문등 채집 자료 (엑셀, 연도별 시트 16장)
  - 기상: Open-Meteo ERA5 재분석 자료 (CSV, 일 단위 5,844일)

두 자료는 시간 단위가 다르다. 모기는 '주', 기상은 '일'이다.
그래서 기상 자료를 주 단위로 묶은 다음, 같은 연·월·주차끼리 옆으로 붙인다.
(값을 더하거나 섞는 게 아니라, 같은 시점의 값을 한 행에 나란히 놓는 것이다.)

실행:  python src/step1_preprocess.py
"""

import re

import pandas as pd

from config import (COVERAGE_CSV, FIRST_YEAR, LAST_YEAR, MONTHS, MOSQUITO_XLSX,
                    PROCESSED, WEATHER_CSV, WEEKLY_CSV)

# 원자료의 채집일 칸은 날짜가 아니라 "7월 3주" 같은 라벨이다.
WEEK_LABEL = re.compile(r"\s*(\d+)월\s*(\d+)주\s*")


def find_column(sheet, names, year):
    """시트 위쪽 4줄에서 머리글 칸을 찾아 (행, 열) 위치를 돌려준다.

    연도마다 시트 모양이 조금씩 다르다.
    2008~2010년은 머리글이 3번째 줄에 한글 종명으로 있고,
    2016년 이후는 학명 약어(Cx.pip.)와 한글명이 두 줄로 나뉘어 있다.
    그래서 '몇 번째 줄'로 고정하지 않고 이름으로 찾는다.
    """
    for row in range(min(4, len(sheet))):
        for col, cell in sheet.iloc[row].items():
            if isinstance(cell, str) and cell.strip() in names:
                return row, col
    raise ValueError(f"{year}년 시트에서 {names} 칸을 찾지 못했습니다.")


def read_mosquito_sheet(year):
    """한 해 시트에서 주차별 빨간집모기 수와 전체 모기 수를 뽑는다."""
    sheet = pd.read_excel(MOSQUITO_XLSX, sheet_name=str(year), header=None)

    date_row, date_col = find_column(sheet, {"채집일"}, year)
    culex_row, culex_col = find_column(sheet, {"빨간집모기"}, year)
    # 전체 합계 칸의 이름이 연도에 따라 '계' 또는 '모기 계'로 다르다.
    total_row, total_col = find_column(sheet, {"모기 계", "계"}, year)

    first_data_row = max(date_row, culex_row, total_row) + 1

    records = []
    for _, row in sheet.iloc[first_data_row:].iterrows():
        label = row.iloc[date_col]
        if not isinstance(label, str):
            continue
        matched = WEEK_LABEL.fullmatch(label.strip())
        if matched is None:
            continue  # '2023년 총계' 같은 합계 행은 여기서 걸러진다

        month, week = map(int, matched.groups())
        if month not in MONTHS:
            continue

        records.append({
            "year": year,
            "month": month,
            "week_of_month": week,
            # 연도에 따라 '6월1주'와 '6월 1주'가 섞여 있어 표기를 통일한다
            "week_label": f"{month}월 {week}주",
            "culex": pd.to_numeric(row.iloc[culex_col], errors="coerce"),
            "total_mosquito": pd.to_numeric(row.iloc[total_col], errors="coerce"),
        })
    return records


def load_mosquito():
    """16개 연도 시트를 모두 읽어 하나의 표로 합친다."""
    rows = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        rows.extend(read_mosquito_sheet(year))

    data = pd.DataFrame(rows).sort_values(["year", "month", "week_of_month"])
    data = data.reset_index(drop=True)

    # --- 결측치 처리 ------------------------------------------------------
    # 2010년 4월 1주와 4월 5주는 종별 칸이 모두 비어 있고 '계'만 0으로 적혀 있다.
    # 전체 합이 0이면 그 안의 어떤 종도 반드시 0이다. 추측이 아니라 산술적으로
    # 확실하므로, 이 경우에만 0으로 채운다.
    fill = data["culex"].isna() & (data["total_mosquito"] == 0)
    if fill.any():
        print(f"[결측 처리] 전체 합이 0이라 빨간집모기를 0으로 채운 주: {fill.sum()}건")
        print(data.loc[fill, ["year", "week_label"]].to_string(index=False))
        data.loc[fill, "culex"] = 0

    # 위 규칙으로도 채워지지 않은 결측은 근거 없이 메우지 않고 멈춘다.
    if data["culex"].isna().any():
        raise ValueError("근거 없이 채울 수 없는 결측치가 있습니다.")

    # --- 이상치 처리: 같은 0이라도 성격이 다르다 --------------------------
    # 0마리인 주가 여럿 있는데, 옆 칸(전체 모기 수)을 보면 성격이 갈린다.
    #   전체도 0    → 진짜 0 (초봄·늦가을에 실제로 안 잡힘)
    #   전체가 1~2  → 채집이 거의 안 된 주 (장비 문제 등). 0으로 봐도 무방
    #   전체가 수십~수백 → 다른 종은 잡혔는데 전체의 86%를 차지하는 종만
    #                    정확히 0. 물리적으로 어렵다. 기록 오류로 본다.
    # 기록 오류는 0으로 두면 평년값과 회귀를 끌어내리므로 분석에서 뺀다.
    # 임의로 다른 값을 채워 넣지는 않는다. 모르는 것은 모르는 채로 둔다.
    suspicious = (data["culex"] == 0) & (data["total_mosquito"] >= 30)
    if suspicious.any():
        print(f"[이상치] 전체는 30마리 이상 잡혔는데 빨간집모기만 0 → 기록 오류로 제외: "
              f"{suspicious.sum()}건")
        print(data.loc[suspicious, ["year", "week_label", "culex", "total_mosquito"]]
              .to_string(index=False))
        data = data[~suspicious].reset_index(drop=True)

    zeros = data[data["culex"] == 0]
    if len(zeros):
        print(f"[이상치] 실제 0으로 남긴 주: {len(zeros)}건 (전체 모기도 거의 0이었음)")
    if (data["culex"] < 0).any():
        raise ValueError("빨간집모기 개체수가 음수인 행이 있습니다.")
    if data.duplicated(["year", "month", "week_of_month"]).any():
        raise ValueError("연·월·주차가 중복된 행이 있습니다.")

    data["culex"] = data["culex"].astype(int)
    data["total_mosquito"] = data["total_mosquito"].astype(int)
    return data


def load_weather_weekly():
    """일 단위 기상 자료를 주 단위로 묶는다.

    주차 나누는 규칙: 1~7일=1주, 8~14일=2주, 15~21일=3주, 22~28일=4주, 29일~=5주
    모기 자료의 '몇 월 몇 주' 라벨과 맞추기 위한 규칙이다.

    주의: 5주차는 2~3일밖에 없다. 그래서 강수량을 '주간 합계'로 만들면
    5주차만 값이 작게 나오는 착시가 생긴다. 이걸 피하려고 모든 기상 변수를
    '하루 평균'으로 통일한다. 강수량 단위는 mm/일이 된다.
    """
    weather = pd.read_csv(WEATHER_CSV, parse_dates=["date"])
    weather["year"] = weather["date"].dt.year
    weather["month"] = weather["date"].dt.month
    weather["week_of_month"] = (weather["date"].dt.day - 1) // 7 + 1
    weather = weather[weather["month"].isin(MONTHS)]

    weekly = weather.groupby(["year", "month", "week_of_month"], as_index=False).agg(
        week_start=("date", "min"),
        week_end=("date", "max"),
        weather_days=("date", "size"),
        avg_temp=("avg_temp", "mean"),        # 일평균기온의 주간 평균
        rain_per_day=("rainfall", "mean"),    # 하루 평균 강수량(mm/일)
        humidity=("humidity", "mean"),        # 일평균습도의 주간 평균
    )
    return weekly


def summarize_coverage(data):
    """연도마다 관측된 월 범위와 주 수를 정리한다.

    연도별로 채집을 시작한 달과 끝낸 달이 다르다. 이걸 모르고 연도끼리 비교하면
    '자료가 없어서 적은 것'을 '모기가 줄어든 것'으로 잘못 읽게 된다.
    """
    rows = []
    for year, group in data.groupby("year"):
        months = sorted(group["month"].unique())
        rows.append({
            "year": year,
            "first_month": months[0],
            "last_month": months[-1],
            "n_months": len(months),
            "n_weeks": len(group),
            "missing_months": ",".join(str(m) for m in MONTHS if m not in months) or "-",
        })
    return pd.DataFrame(rows)


def scan_duplicate_years(data):
    """서로 다른 연도의 같은 주차에 똑같은 값이 있는지 살핀다.

    자연스러운 자료라면 다른 해의 같은 주차 값이 정확히 일치하는 일은 드물다.
    한 연도쌍에서만 여러 건이 몰려 나오면 원자료를 옮겨 적는 과정에서
    생긴 복사 오류일 수 있다. 자동으로 고치지는 않는다. 어느 쪽이 맞는지
    알 수 없기 때문이다. 대신 찾아서 알리고 리포트 한계점에 남긴다.
    """
    table = data[data["culex"] > 0].pivot_table(
        index="week_label", columns="year", values="culex", aggfunc="first")
    years = list(table.columns)
    rows = []
    for i, a in enumerate(years):
        for b in years[i + 1:]:
            pair = table[[a, b]].dropna()
            same = pair[pair[a] == pair[b]]
            if len(same):
                rows.append({"year_a": a, "year_b": b, "n_same": len(same),
                             "n_common": len(pair),
                             "weeks": ",".join(same.index)})
    found = pd.DataFrame(rows).sort_values("n_same", ascending=False)
    return found


def main():
    mosquito = load_mosquito()
    weather = load_weather_weekly()

    merged = mosquito.merge(
        weather,
        on=["year", "month", "week_of_month"],
        how="left",
        validate="one_to_one",  # 한 주에 한 행씩만 붙는지 확인
    )
    if merged["avg_temp"].isna().any():
        raise ValueError("기상 자료가 붙지 않은 주가 있습니다.")

    merged.round({
        "avg_temp": 2, "rain_per_day": 2, "humidity": 2,
    }).to_csv(WEEKLY_CSV, index=False, encoding="utf-8-sig")

    coverage = summarize_coverage(merged)
    coverage.to_csv(COVERAGE_CSV, index=False, encoding="utf-8-sig")

    print(f"주 단위 분석표: {WEEKLY_CSV.relative_to(WEEKLY_CSV.parents[2])} ({len(merged)}주)")
    print(f"기간: {merged['year'].min()}~{merged['year'].max()}년 "
          f"{min(MONTHS)}~{max(MONTHS)}월")
    print(f"빨간집모기 총 {merged['culex'].sum():,}마리 "
          f"(전체 모기의 {merged['culex'].sum() / merged['total_mosquito'].sum():.1%})")
    print("\n연도별 관측 범위")
    print(coverage.to_string(index=False))
    print("\n5주차(기상 2~3일)인 주:", (merged["weather_days"] < 7).sum(), "주")

    duplicates = scan_duplicate_years(merged)
    duplicates.to_csv(PROCESSED / "duplicate_year_scan.csv", index=False,
                      encoding="utf-8-sig")
    suspects = duplicates[duplicates["n_same"] >= 3]
    print("\n연도 간 값 복사 의심 검사")
    if len(suspects):
        for row in suspects.itertuples():
            print(f"  [의심] {row.year_a}·{row.year_b}: 공통 {row.n_common}주 중 "
                  f"{row.n_same}주가 값까지 동일 → {row.weeks}")
        others = duplicates[duplicates["n_same"] < 3]["n_same"]
        print(f"  (참고: 나머지 {len(others)}개 연도쌍은 최대 "
              f"{others.max() if len(others) else 0}주만 일치)")
        print("  자동으로 고치지 않는다. 어느 쪽이 맞는지 알 수 없으므로 리포트에 밝힌다.")
    else:
        print("  의심되는 연도쌍 없음")


if __name__ == "__main__":
    main()
