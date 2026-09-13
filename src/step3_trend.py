"""[3단계] 연도별 모기 관측량과 3년 이동평균으로 장기 흐름을 본다."""

import matplotlib.pyplot as plt
import pandas as pd

from config import (ANALYSIS_FIRST_YEAR, ANALYSIS_MONTHS, C_MOSQUITO, C_TEXT,
                    PROCESSED, WEEKLY_CSV, save, setup_matplotlib, style_axis)


def annual_mosquito(data):
    """월별 주간 평균을 먼저 구한 뒤 여섯 달을 같은 비중으로 평균낸다."""
    window = data[(data["year"] >= ANALYSIS_FIRST_YEAR)
                  & data["month"].isin(ANALYSIS_MONTHS)].copy()
    monthly = window.groupby(["year", "month"], as_index=False)["culex"].mean()
    annual = monthly.groupby("year", as_index=False)["culex"].mean()
    annual["moving_average_3y"] = annual["culex"].rolling(3, center=True).mean()
    return annual


def draw(annual):
    figure, axis = plt.subplots(figsize=(12, 6.2))
    axis.plot(annual["year"], annual["culex"], marker="o", markersize=7,
              linewidth=1.5, color="#B9B9B9", label="연도별 평균")
    axis.plot(annual["year"], annual["moving_average_3y"], marker="o",
              markersize=8, linewidth=3.2, color=C_MOSQUITO, label="3년 이동평균")
    style_axis(axis)
    axis.set(title="모기 관측량은 장기적으로 어떻게 변했을까?",
             xlabel="연도", ylabel="5~10월 주간 평균 관측량 (마리)")
    ticks = [y for y in annual["year"] if y % 2 == 0] + [int(annual["year"].iloc[-1])]
    axis.set_xticks(ticks)
    axis.legend(loc="upper right")
    axis.text(0, -0.14,
              "회색선은 해마다의 값, 주황선은 앞뒤 3개년 평균으로 단기 변동을 완화한 흐름이다.",
              transform=axis.transAxes, color=C_TEXT, fontsize=11.5)
    figure.tight_layout()
    save(figure, "03_mosquito_trend.png")


def main():
    setup_matplotlib()
    annual = annual_mosquito(pd.read_csv(WEEKLY_CSV))
    annual.round(2).to_csv(PROCESSED / "annual_mosquito_trend.csv", index=False,
                           encoding="utf-8-sig")
    draw(annual)
    print(annual.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
