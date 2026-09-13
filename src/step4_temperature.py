"""[4단계] 5~10월의 연도별 평균기온과 3년 이동평균을 그린다."""

import matplotlib.pyplot as plt
import pandas as pd
from config import (ANALYSIS_FIRST_YEAR, ANALYSIS_MONTHS, C_TEMP, C_TEXT,
                    PROCESSED, WEATHER_CSV, save, setup_matplotlib, style_axis)


def annual_temperature():
    weather = pd.read_csv(WEATHER_CSV, parse_dates=["date"])
    weather = weather[(weather["date"].dt.year >= ANALYSIS_FIRST_YEAR)
                      & weather["date"].dt.month.isin(ANALYSIS_MONTHS)].copy()
    annual = (weather.assign(year=weather["date"].dt.year)
              .groupby("year", as_index=False)["avg_temp"].mean())
    annual["moving_average_3y"] = annual["avg_temp"].rolling(3, center=True).mean()
    return annual


def draw(annual):
    figure, axis = plt.subplots(figsize=(12, 6.2))
    axis.plot(annual["year"], annual["avg_temp"], marker="o", markersize=7,
              linewidth=1.5, color="#B9B9B9", label="연도별 평균기온")
    axis.plot(annual["year"], annual["moving_average_3y"], marker="o",
              markersize=8, linewidth=3.2, color=C_TEMP, label="3년 이동평균")
    style_axis(axis)
    axis.set(title="같은 기간의 평균기온은 어떻게 변했을까?",
             xlabel="연도", ylabel="5~10월 평균기온 (°C)")
    ticks = [y for y in annual["year"] if y % 2 == 0] + [int(annual["year"].iloc[-1])]
    axis.set_xticks(ticks)
    axis.legend(loc="upper left")
    axis.text(0, -0.14,
              "모기 분석과 같은 2010~2023년 5~10월만 사용해 비교 기간을 맞췄다.",
              transform=axis.transAxes, color=C_TEXT, fontsize=11.5)
    figure.tight_layout()
    save(figure, "04_temperature_trend.png")


def main():
    setup_matplotlib()
    annual = annual_temperature()
    annual.round(2).to_csv(PROCESSED / "annual_temperature_trend.csv", index=False,
                           encoding="utf-8-sig")
    draw(annual)
    print(annual.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
