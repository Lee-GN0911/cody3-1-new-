"""[5단계] 기온·강수량·습도와 모기 관측량의 관련성을 비교한다."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from analysis import load_with_anomaly, zscore
from config import C_MOSQUITO, C_TEMP, C_TEXT, C_ZERO, PROCESSED, save, setup_matplotlib, style_axis

DISPLAY_TERMS = ["평균기온", "강수량", "습도"]


def fit_model(data):
    design = pd.DataFrame({
        "평균기온": zscore(data["avg_temp_dev"]),
        "강수량": zscore(data["rain_per_day_dev"]),
        "습도": zscore(data["humidity_dev"]),
        "연도": zscore(data["year"]),
    })
    model = sm.OLS(data["log_index"], sm.add_constant(design)).fit(
        cov_type="HAC", cov_kwds={"maxlags": 4})
    low, high = model.conf_int()[0], model.conf_int()[1]
    result = pd.DataFrame({
        "factor": DISPLAY_TERMS,
        "effect_pct": [(np.exp(model.params[t]) - 1) * 100 for t in DISPLAY_TERMS],
        "low_pct": [(np.exp(low[t]) - 1) * 100 for t in DISPLAY_TERMS],
        "high_pct": [(np.exp(high[t]) - 1) * 100 for t in DISPLAY_TERMS],
        "p_value": [model.pvalues[t] for t in DISPLAY_TERMS],
    })
    result["judgement"] = np.where(result["p_value"] < .05,
                                    "뚜렷한 관련", "뚜렷하지 않음")
    return model, result


def draw(model, result):
    figure, axis = plt.subplots(figsize=(11.5, 5.8))
    positions = np.arange(len(result))[::-1]
    limit = max(abs(result["low_pct"]).max(), abs(result["high_pct"]).max()) + 14

    for pos, row in zip(positions, result.itertuples()):
        clear = row.p_value < .05
        color = (C_MOSQUITO if row.effect_pct >= 0 else C_TEMP) if clear else "#B8B8B8"
        axis.plot([row.low_pct, row.high_pct], [pos, pos], color=color,
                  linewidth=3, solid_capstyle="round")
        axis.plot(row.effect_pct, pos, "o", markersize=13, color=color,
                  markerfacecolor="white", markeredgewidth=3)
        axis.text(limit * .48, pos, f"{row.effect_pct:+.0f}% · {row.judgement}",
                  va="center", fontsize=12.5, color=C_TEXT,
                  fontweight="bold" if clear else "normal")

    axis.axvline(0, color=C_ZERO, linewidth=1.2)
    style_axis(axis, grid=None)
    axis.set_yticks(positions, result["factor"])
    axis.set_xlim(-limit, limit)
    axis.set(title="모기 관측량과 가장 뚜렷하게 관련된 기상요인은 무엇일까?",
             xlabel="기상요인이 평년보다 한 단계 높을 때 모기 관측량 차이 (%)")
    axis.text(0, -0.20,
              "가로선이 0을 지나면 증가·감소 방향이 명확하지 않다. 관련성은 인과관계를 뜻하지 않는다.",
              transform=axis.transAxes, fontsize=11.5, color="#6B7683")
    figure.suptitle(f"기온·강수·습도와 연도를 함께 비교 · 설명력 {model.rsquared * 100:.1f}%",
                    fontsize=12.5, color="#6B7683", y=.98)
    figure.tight_layout()
    save(figure, "06_weather_factors.png")


def main():
    setup_matplotlib()
    model, result = fit_model(load_with_anomaly())
    result.round(4).to_csv(PROCESSED / "weather_factor_results.csv", index=False,
                           encoding="utf-8-sig")
    draw(model, result)
    print(result.round(3).to_string(index=False))
    print(f"\n설명력: {model.rsquared:.3f}")


if __name__ == "__main__":
    main()
