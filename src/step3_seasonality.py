"""[3단계] 계절을 걷어내고 본다 — 모기는 정말 줄었는가?

2단계에서 두 가지를 봤다. 계절에 따른 오르내림이 매우 크고, 연도마다
채집한 달이 다르다는 것. 이 상태로 연도별 평균을 비교하면 안 된다.
자료가 없어서 생긴 차이를 모기 수 변화로 잘못 읽게 된다.

해법은 한 줄이다. 각 주의 값을 '그 월·주차의 평년값'으로 나눈다.

    d["index"] = d.culex / d.groupby(["month", "week_of_month"]).culex.transform("mean")

7월 3주에 800마리, 7월 3주 평년이 534마리 → 1.50배.
이러면 4월이든 7월이든 모두 평년=1.0 기준이 되어 서로 비교할 수 있다.

실행:  python src/step3_seasonality.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from config import (C_MOSQUITO, C_TEMP, C_TEXT, EARLY, LATE, PROCESSED,
                    WEEKLY_CSV, save, setup_matplotlib, style_axis)
from analysis import load_with_anomaly

MONTH_NAMES = {m: f"{m}월" for m in range(4, 12)}
SUMMER = (6, 7, 8)


def monthly_profile(data, first_year, last_year):
    window = data[data["year"].between(first_year, last_year)]
    return window.groupby("month", as_index=False)["culex"].mean()


def season_trends(indexed):
    """여름과 봄·가을을 나눠 연도별 지수의 추세를 잰다.

    '여름은 줄고 봄가을은 늘었다'가 눈에 보이는 것과, 그게 우연이 아니라고
    말할 수 있는 것은 다르다. 후자를 확인하는 계산이다.
    """
    frame = indexed.copy()
    frame["season"] = np.where(frame["month"].isin(SUMMER), "여름", "봄·가을")
    annual = frame.pivot_table(index="year", columns="season",
                               values="index", aggfunc="mean")
    out = {}
    for name in annual.columns:
        trend = linregress(annual.index, annual[name])
        out[name] = {
            "early": annual.loc[EARLY[0]:EARLY[1], name].mean(),
            "late": annual.loc[LATE[0]:LATE[1], name].mean(),
            "slope": trend.slope, "p": trend.pvalue,
        }
    return annual, out


def draw(early, late, trends):
    figure, axis = plt.subplots(figsize=(12, 6.6))

    axis.plot(early["month"], early["culex"], marker="o", markersize=9,
              linewidth=2.6, color=C_TEMP)
    axis.plot(late["month"], late["culex"], marker="o", markersize=9,
              linewidth=2.6, color=C_MOSQUITO)

    # 범례 상자 대신 선 끝에 이름을 붙인다. 눈이 왔다갔다 하지 않아도 된다.
    axis.text(11.15, early["culex"].iloc[-1], f"  {EARLY[0]}~{EARLY[1]}년",
              va="center", ha="left", fontsize=12.5, color=C_TEMP, fontweight="bold")
    axis.text(11.15, late["culex"].iloc[-1], f"  {LATE[0]}~{LATE[1]}년",
              va="center", ha="left", fontsize=12.5, color=C_MOSQUITO, fontweight="bold")

    merged = early.merge(late, on="month", suffixes=("_early", "_late"))
    merged["change"] = (merged["culex_late"] - merged["culex_early"]) / merged["culex_early"] * 100
    for month in (7, 10):
        row = merged[merged["month"] == month].iloc[0]
        top = max(row["culex_early"], row["culex_late"])
        axis.annotate(f"{row['change']:+.0f}%", xy=(month, top), xytext=(0, 15),
                      textcoords="offset points", ha="center",
                      fontsize=13.5, fontweight="bold", color=C_TEXT)
        axis.plot([month, month], [row["culex_early"], row["culex_late"]],
                  color="#CCCCCC", linewidth=1.2, zorder=0)

    style_axis(axis)
    axis.set(xlabel="월", ylabel="주간 평균 관측량 (마리)")
    axis.set_title("여름 봉우리가 내려앉고, 봄과 가을이 올라왔다", pad=30)
    summer, shoulder = trends["여름"], trends["봄·가을"]
    # p값을 그대로 적는다. 0.05를 살짝 넘었다고 "관계 없음"이 되는 것도,
    # 살짝 밑돌았다고 "확실함"이 되는 것도 아니다. 숫자를 보여주고 판단은 맡긴다.
    axis.text(0.5, 1.015,
              f"여름 감소 p={summer['p']:.3f}, 봄·가을 증가 p={shoulder['p']:.3f} "
              "— 둘 다 0.05 경계선에 걸쳐 있다",
              transform=axis.transAxes, ha="center", fontsize=12.5, color="#6B7683")
    axis.set_xticks(list(MONTH_NAMES), [MONTH_NAMES[m] for m in MONTH_NAMES])
    axis.set_xlim(3.7, 12.3)
    # 봉우리 위에 % 라벨을 얹으므로 위쪽에 자리를 비워둔다
    axis.set_ylim(0, max(early["culex"].max(), late["culex"].max()) * 1.18)
    figure.tight_layout()
    save(figure, "03_seasonal_shift.png")


def main():
    setup_matplotlib()
    raw = pd.read_csv(WEEKLY_CSV)
    early = monthly_profile(raw, *EARLY)
    late = monthly_profile(raw, *LATE)

    indexed = load_with_anomaly()
    annual, trends = season_trends(indexed)
    annual.round(3).to_csv(PROCESSED / "annual_index_by_season.csv", encoding="utf-8-sig")
    draw(early, late, trends)

    merged = early.merge(late, on="month", suffixes=("_early", "_late"))
    merged["change"] = (merged["culex_late"] - merged["culex_early"]) / merged["culex_early"] * 100
    print(f"월별 주간 평균: {EARLY[0]}~{EARLY[1]}년 → {LATE[0]}~{LATE[1]}년")
    for row in merged.itertuples():
        print(f"  {MONTH_NAMES[row.month]:>4}  {row.culex_early:6.1f} → "
              f"{row.culex_late:6.1f}마리  ({row.change:+6.1f}%)")

    print("\n평년 대비 지수로 본 계절별 추세")
    for name, row in trends.items():
        print(f"  {name:<6} {row['early']:.2f}배 → {row['late']:.2f}배  "
              f"(연 {row['slope']:+.4f}, p={row['p']:.4f})")

    total = indexed.groupby("year")["index"].mean()
    overall = linregress(total.index, total.values)
    print(f"\n  전체   연 {overall.slope:+.4f}배 (p={overall.pvalue:.4f})")
    print("  → 전체가 평평한 이유: 여름의 감소와 봄·가을의 증가가 서로 상쇄됐다")
    print("  → 총량이 아니라 '시기'가 바뀌었다")


if __name__ == "__main__":
    main()
