"""[4단계] 그런데 온도는 정말 올랐는가?

"더워서 모기가 줄었다"를 따지려면 두 가지를 먼저 확인해야 한다.
  ① 모기가 줄었는가  → 3단계에서 확인했다 (총량은 아니고, 여름만)
  ② 더워졌는가       → 아직 확인하지 않았다

전제를 확인하지 않고 결론부터 따지는 것은 흔한 실수다. 여기서 확인한다.

기온도 모기와 같은 문제를 안고 있다. 7월이 4월보다 더운 건 당연하고,
연도마다 채집한 달이 다르다. 그래서 기온도 '같은 월·주차의 평년과 견준
차이'로 바꿔서 본다. 모기에 쓴 것과 똑같은 방법이다.

실행:  python src/step4_temperature.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

from config import (C_MOSQUITO, C_TEMP, C_TEXT, C_ZERO, EARLY, LATE, WEEKLY_CSV,
                    save, setup_matplotlib, style_axis)
from analysis import load_with_anomaly

SUMMER = (6, 7, 8)


def annual_series(data):
    """연도별로 두 가지를 만든다.

    ① 평년 대비 기온 차이의 연평균 — 그해가 평년보다 몇 도 따뜻했나
    ② 여름 폭염일수 — 6~8월에 일 최고기온이 33℃를 넘은 날이 며칠이었나
    """
    warm = data.groupby("year", as_index=False)["avg_temp_dev"].mean()

    raw = pd.read_csv(WEEKLY_CSV)
    summer = raw[raw["month"].isin(SUMMER)]
    heat = summer.groupby("year", as_index=False)["hot_days"].sum()
    return warm.merge(heat, on="year")


def draw(series):
    figure, (left, right) = plt.subplots(1, 2, figsize=(14, 5.8))

    panels = [
        (left, "avg_temp_dev", C_TEMP, "① 평균기온은 완만히 올랐다",
         "평년 대비 기온 차이 (℃)", "{:+.3f}℃"),
        (right, "hot_days", C_MOSQUITO, "② 폭염일은 가파르게 늘었다",
         "여름(6~8월) 폭염일수 (일)", "{:+.2f}일"),
    ]
    for axis, column, color, title, ylabel, fmt in panels:
        trend = linregress(series["year"], series[column])
        axis.plot(series["year"], series[column], marker="o", markersize=8,
                  linewidth=2.2, color=color, alpha=0.85,
                  markerfacecolor="white", markeredgewidth=2.2)
        axis.plot(series["year"], trend.intercept + trend.slope * series["year"],
                  linestyle="--", linewidth=2.4, color=color)
        if column == "avg_temp_dev":
            # 0 = 평년 수준. 위아래를 가르는 기준선이라 의미가 있다.
            axis.axhline(0, color=C_ZERO, linewidth=1)
        style_axis(axis)
        axis.set(title=title, xlabel="연도", ylabel=ylabel)
        axis.set_xticks(series["year"][::3])
        axis.text(0.03, 0.94, f"연 {fmt.format(trend.slope)}\np = {trend.pvalue:.3f}",
                  transform=axis.transAxes, va="top", ha="left",
                  fontsize=13, fontweight="bold", color=color, linespacing=1.6)

    figure.suptitle("전제 확인: 서울은 더워졌는가", fontsize=16, y=1.02)
    figure.text(0.5, -0.02,
                "두 지표 모두 오르는 방향이지만 p는 0.05~0.10 사이다. "
                "16개 점으로 추세를 확정하기는 짧다.",
                ha="center", fontsize=12.5, color="#6B7683")
    figure.tight_layout()
    save(figure, "04_temperature_trend.png")


def main():
    setup_matplotlib()
    data = load_with_anomaly()
    series = annual_series(data)
    draw(series)

    print("연도별 기온 지표")
    print(f"  {'연도':<6}{'평년 대비 기온':>14}{'여름 폭염일수':>14}")
    for row in series.itertuples():
        print(f"  {row.year:<6}{row.avg_temp_dev:>+13.2f}℃{row.hot_days:>13}일")

    for column, name, unit in [("avg_temp_dev", "평년 대비 기온", "℃"),
                               ("hot_days", "여름 폭염일수", "일")]:
        trend = linregress(series["year"], series[column])
        print(f"\n{name}: 연 {trend.slope:+.3f}{unit}  p={trend.pvalue:.4f}")
        early = series[series["year"] <= EARLY[1]][column].mean()
        late = series[series["year"] >= LATE[0]][column].mean()
        print(f"  전반 8년 {early:.2f} → 후반 8년 {late:.2f}  (차이 {late - early:+.2f}{unit})")

    print("\n→ 두 지표 모두 오르는 방향이다. 다만 p는 0.05~0.10 사이로,")
    print("  16개 점만으로 추세를 확정하기는 짧다는 뜻이다.")
    print("  (연도별로 묶지 않고 478주 전체로 검정하면 p는 더 작아지지만,")
    print("   그 경우 같은 해의 주들이 서로 닮아 있어 p가 과소평가된다.")
    print("   여기서는 보수적인 쪽인 연도 단위 검정 결과를 쓴다.)")
    print("\n→ 그리고 '평균이 조금 오른 것'과 '폭염이 크게 늘어난 것'은")
    print("  다른 이야기다. 6단계에서 나눠서 따진다.")


if __name__ == "__main__":
    main()
