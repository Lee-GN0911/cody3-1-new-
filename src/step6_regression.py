"""[7단계] 회귀분석 — 여러 요인을 한꺼번에 놓고 세기를 비교한다.

6단계까지는 요인을 하나씩 봤다. 그런데 더운 주는 대체로 습하기도 하다.
하나씩 보면 습도가 기온의 공을 가로챌 수 있다. 회귀분석은 나머지 조건을
같게 맞춰놓고 각 요인의 몫을 따로 떼어낸다.

계수를 읽기 쉽게 만드는 두 가지 장치를 쓴다.
  1. 종속변수에 로그를 씌운다 → 계수가 '몇 % 변하는가'가 된다
  2. 독립변수를 표준화한다   → 단위가 다른 요인을 같은 잣대로 비교할 수 있다
합치면 이렇게 읽힌다: "평년보다 1표준편차 따뜻한 주에는 모기가 21% 많다"

실행:  python src/step7_regression.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import (C_MOSQUITO, C_TEMP, C_TEXT, C_ZERO, EARLY, LATE, PROCESSED,
                    save, setup_matplotlib, style_axis)
from analysis import load_with_anomaly, zscore

TERMS = {
    "평년보다 따뜻함": "그 주가 같은 시기 평년보다 따뜻했는가",
    "폭염일 많음": "일 최고기온 33℃ 이상인 날이 많았는가",
    "비 많음": "그 주에 비가 많이 왔는가",
    "습함": "그 주가 습했는가",
    "연도": "날씨로 설명되지 않는 장기 변화",
}


def build_design(data):
    """네 가지 날씨 요인과 연도를 한 표에 담는다.

    모두 '같은 시기 평년과 견준 차이'다. 그리고 표준화해서 단위를 맞춘다.
    ℃와 %와 mm를 그대로 두면 계수 크기를 비교할 수 없다.
    """
    merged = data.copy()
    design = pd.DataFrame({
        "평년보다 따뜻함": zscore(merged["avg_temp_dev"]),
        "폭염일 많음": zscore(merged["hot_day_ratio_dev"]),
        "비 많음": zscore(merged["rain_per_day_dev"]),
        "습함": zscore(merged["humidity_dev"]),
        "연도": zscore(merged["year"]),
    })
    return merged, design


def fit(target, design):
    """최소제곱 회귀. 자기상관을 감안한 HAC 표준오차를 쓴다.

    이웃한 주는 서로 닮아 있다(이번 주에 많으면 다음 주도 많다).
    무시하면 p-value가 실제보다 작게 나와 없는 관계를 있다고 말하게 된다.
    """
    model = sm.OLS(target, sm.add_constant(design)).fit(
        cov_type="HAC", cov_kwds={"maxlags": 4})
    low, high = model.conf_int()[0], model.conf_int()[1]
    to_pct = lambda s: (np.exp(s[design.columns]) - 1) * 100
    return model, pd.DataFrame({
        "term": design.columns,
        "p_value": model.pvalues[design.columns].values,
        "effect_pct": to_pct(model.params).values,
        "low_pct": to_pct(low).values,
        "high_pct": to_pct(high).values,
    })


def draw(model, result):
    """계수는 막대가 아니라 점과 선으로 그린다.

    막대는 '길이'를 보게 만드는데, 여기서 중요한 건 길이가 아니라
    '어디쯤이고 얼마나 불확실한가'다. 점 하나와 신뢰구간 선이 그 일을 한다.
    """
    figure, axis = plt.subplots(figsize=(11.5, 5.8))
    positions = np.arange(len(result))[::-1]

    for pos, row in zip(positions, result.itertuples()):
        significant = row.p_value < 0.05
        color = (C_MOSQUITO if row.effect_pct >= 0 else C_TEMP) if significant else "#AFB6BC"
        axis.plot([row.low_pct, row.high_pct], [pos, pos],
                  color=color, linewidth=2.6, solid_capstyle="round")
        axis.plot(row.effect_pct, pos, "o", markersize=13, color=color,
                  markerfacecolor="white", markeredgewidth=3)

        label = (f"{row.effect_pct:+.0f}%   p={row.p_value:.3f}" if significant
                 else f"불명확   p={row.p_value:.3f}")
        axis.text(row.high_pct + 2.2, pos, label, va="center", ha="left",
                  fontsize=12, color=C_TEXT if significant else "#8A8A8A",
                  fontweight="bold" if significant else "normal")

    axis.axvline(0, color=C_ZERO, linewidth=1.2)
    style_axis(axis, grid=None)
    axis.set_yticks(positions, result["term"])
    axis.set_ylim(-0.7, len(result) - 0.3)
    axis.set_xlim(min(result["low_pct"]) - 8, max(result["high_pct"]) + 26)
    axis.set(title="평년보다 한 단계 높아질 때 모기 관측량은 몇 % 달라지는가",
             xlabel="모기 관측량 변화 (%) — 가로선은 95% 신뢰구간, 0을 지나면 불명확")
    figure.suptitle(f"날씨가 설명하는 몫은 전체의 {model.rsquared * 100:.1f}%뿐이다"
                    f"  (n={int(model.nobs)}주)", fontsize=13, color="#6B7683", y=0.985)
    figure.tight_layout()
    save(figure, "06_regression_effects.png")


def warming_vs_actual(model, data, months, label):
    """온난화가 실제 감소를 얼마나 설명하는지 계산한다.

    앞의 회귀는 '어떤 주가 평년보다 따뜻하면 그 주 모기가 어떻게 되는가'를 잰다.
    그것만으로는 "16년 동안 더워져서 모기가 줄었다"에 답할 수 없다. 둘은 다른
    질문이다. 답하려면 한 단계가 더 필요하다.

        실제로 오른 기온  ×  회귀에서 얻은 한 단계당 효과  =  온난화의 몫

    이 몫을 실제 일어난 변화와 나란히 놓으면, 온난화로 설명되는 부분과
    설명되지 않는 부분이 갈린다.

    주의: 계수가 통계적으로 확정되지 않았더라도(p가 커도) 일단 그 값을 그대로
    믿어주고 계산한다. 관대하게 계산해도 설명이 안 된다면, 결론이 더 단단해진다.
    """
    window = data[data["month"].isin(months)]
    early = window[window["year"] <= EARLY[1]]
    late = window[window["year"] >= LATE[0]]

    sd_warm = data["avg_temp_dev"].std(ddof=0)   # 회귀에서 말하는 '한 단계'의 크기
    sd_heat = data["hot_day_ratio_dev"].std(ddof=0)

    d_warm = late["avg_temp"].mean() - early["avg_temp"].mean()
    d_heat = late["hot_day_ratio"].mean() - early["hot_day_ratio"].mean()

    warm_log = model.params["평년보다 따뜻함"] * d_warm / sd_warm
    heat_log = model.params["폭염일 많음"] * d_heat / sd_heat
    to_pct = lambda x: (np.exp(x) - 1) * 100

    return {
        "label": label, "d_warm": d_warm, "d_heat": d_heat,
        "sd_warm": sd_warm, "sd_heat": sd_heat,
        "warm_pct": to_pct(warm_log), "heat_pct": to_pct(heat_log),
        "weather_pct": to_pct(warm_log + heat_log),
        "actual_pct": (late["culex"].mean() / early["culex"].mean() - 1) * 100,
    }


def draw_warming(summary):
    """온난화의 몫과 실제 변화를 한 줄씩 쌓아 비교한다."""
    figure, axis = plt.subplots(figsize=(12.5, 6.2))
    rows = [
        (f"평균기온 {summary['d_warm']:+.2f}℃ 오른 효과", summary["warm_pct"], "part"),
        (f"폭염일 {summary['d_heat'] * 100:+.1f}%p 늘어난 효과", summary["heat_pct"], "part"),
        ("두 효과를 합친 온난화의 몫", summary["weather_pct"], "sum"),
        ("실제 일어난 변화", summary["actual_pct"], "actual"),
    ]
    positions = np.arange(len(rows))[::-1]

    for pos, (name, value, kind) in zip(positions, rows):
        color = {"part": C_MOSQUITO if value >= 0 else C_TEMP,
                 "sum": "#8A93A0", "actual": "#2F3B45"}[kind]
        axis.barh(pos, value, height=0.42 if kind == "part" else 0.52, color=color)
        axis.text(value + (0.7 if value >= 0 else -0.7), pos, f"{value:+.1f}%",
                  va="center", ha="left" if value >= 0 else "right",
                  fontsize=14, fontweight="bold", color=C_TEXT)

    # 온난화의 몫과 실제 사이의 간격이 이 그림의 요점이다
    gap = summary["actual_pct"] - summary["weather_pct"]
    axis.annotate("", xy=(summary["weather_pct"], 0.5), xytext=(summary["actual_pct"], 0.5),
                  arrowprops=dict(arrowstyle="<->", color="#B0413E", linewidth=2))
    axis.text((summary["weather_pct"] + summary["actual_pct"]) / 2, 0.66,
              f"{gap:.1f}%p — 더위로 설명되지 않는 몫", ha="center", va="bottom",
              fontsize=13.5, fontweight="bold", color="#B0413E")

    axis.axvline(0, color=C_ZERO, linewidth=1.2)
    style_axis(axis, grid=None)
    axis.set_yticks(positions, [r[0] for r in rows])
    axis.set_xlim(summary["actual_pct"] - 12, max(summary["warm_pct"], 0) + 12)
    axis.set_ylim(-0.55, len(rows) - 0.35)
    axis.set(title=f"온난화는 {summary['label']} 감소를 얼마나 설명하는가",
             xlabel="주간 평균 관측량 변화 (%) — 전반 8년 대비 후반 8년")
    axis.text(0, -0.185,
              "폭염 효과를 통계적으로 확정하지 못했지만, 그 값을 그대로 믿어줘도 이만큼이다.",
              transform=axis.transAxes, ha="left", fontsize=12.5, color="#6B7683")
    figure.tight_layout()
    save(figure, "07_warming_vs_actual.png")


def main():
    setup_matplotlib()
    merged, design = build_design(load_with_anomaly())
    model, result = fit(merged["log_index"], design)
    result.round(4).to_csv(PROCESSED / "regression_results.csv", index=False,
                           encoding="utf-8-sig")
    draw(model, result)

    print(f"표본 {int(model.nobs)}주, 설명력 R² = {model.rsquared:.3f}")
    print(f"→ 주 단위 오르내림의 {model.rsquared * 100:.1f}%만 날씨로 설명된다."
          f" 나머지 {100 - model.rsquared * 100:.1f}%는 이 자료 밖에 있다.\n")

    print("평년보다 1표준편차 높아질 때 모기 관측량 변화")
    for row in result.itertuples():
        mark = "유의함" if row.p_value < 0.05 else "불명확"
        print(f"  {row.term:<16} {row.effect_pct:+6.1f}%  "
              f"[{row.low_pct:+6.1f}% ~ {row.high_pct:+6.1f}%]  p={row.p_value:.3f}  {mark}")
        print(f"      └ {TERMS[row.term]}")

    summary = warming_vs_actual(model, merged, [6, 7, 8], "여름(6~8월)")
    draw_warming(summary)
    print("\n온난화는 여름 감소를 얼마나 설명하는가")
    print(f"  한 단계(1SD): 기온 {summary['sd_warm']:.2f}℃, "
          f"폭염일 비율 {summary['sd_heat']:.3f}")
    print(f"  평균기온 {summary['d_warm']:+.2f}℃ 오른 효과     {summary['warm_pct']:+6.1f}%")
    print(f"  폭염일 {summary['d_heat'] * 100:+.1f}%p 늘어난 효과  {summary['heat_pct']:+6.1f}%")
    print(f"  온난화의 몫 합계               {summary['weather_pct']:+6.1f}%")
    print(f"  실제 일어난 변화               {summary['actual_pct']:+6.1f}%")
    print(f"  → 더위로 설명되지 않는 몫      "
          f"{summary['actual_pct'] - summary['weather_pct']:+6.1f}%p")

    warm = result[result["term"] == "평년보다 따뜻함"].iloc[0]
    heat = result[result["term"] == "폭염일 많음"].iloc[0]
    print("\n핵심: 따뜻한 것과 너무 더운 것은 방향이 반대다.")
    print(f"  평년보다 따뜻하면  {warm.effect_pct:+.0f}%  (p={warm.p_value:.3f})")
    print(f"  폭염일이 많으면    {heat.effect_pct:+.0f}%  (p={heat.p_value:.3f})")
    print("  두 힘이 같은 주에 함께 작용하므로, '기온' 하나로 뭉뚱그리면")
    print("  서로 상쇄돼 아무 관계도 없는 것처럼 보인다.")
    if heat.p_value >= 0.05:
        print(f"  다만 폭염 효과는 p={heat.p_value:.3f}로 확정하지 못했다.")
        print("  방향만 참고하고, 크기는 다음 계산에서 관대하게 잡아 확인한다.")


if __name__ == "__main__":
    main()
