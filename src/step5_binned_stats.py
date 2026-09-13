"""[5단계] 구간별 통계 — 비교 대상을 바꾸면 답이 뒤집힌다.

4단계까지는 '모기가 어떻게 변했나'를 봤다. 이제 '무엇 때문인가'로 넘어간다.
가장 단순한 방법은 자료를 몇 덩어리로 나눠 평균을 비교하는 것이다.

기온을 낮은 순으로 5등분해 모기 수를 비교하면 2배 차이가 난다.
그런데 이건 기온이 아니라 계절을 잰 것이다. 여름이 덥고, 여름에 모기가 많으니까.

같은 시기끼리 — '그 주가 평년보다 따뜻했는가'로 나누면 진짜 관계가 남는다.
이 강의에서 가장 중요한 대목이다. 자료도 질문도 그대로인데,
무엇과 비교했는지만 바꿔도 답이 달라진다.

실행:  python src/step5_binned_stats.py
"""

import matplotlib.pyplot as plt
import pandas as pd

from config import C_MOSQUITO, C_TEMP, C_TEXT, C_ZERO, save, setup_matplotlib, style_axis
from analysis import load_with_anomaly

BIN_NAMES = ["최저", "낮음", "중간", "높음", "최고"]


def binned(data, by, value):
    """`by`를 5등분해 각 구간의 `value` 평균을 구한다.

    qcut은 값의 크기가 아니라 순위로 자르므로 구간마다 주 수가 거의 같아진다.
    그래야 구간끼리 공정하게 비교할 수 있다.
    """
    frame = data.copy()
    frame["bin"] = pd.qcut(frame[by], len(BIN_NAMES), labels=BIN_NAMES)
    return frame.groupby("bin", observed=True).agg(
        x=(by, "mean"), y=(value, "mean"), n=(value, "size")
    ).reset_index()


def draw(raw, anomaly):
    figure, (left, right) = plt.subplots(1, 2, figsize=(14, 6.0))

    # ── 왼쪽: 절대 기온으로 나눈 결과 (계절이 섞여 있다) ────────────────
    left.bar(raw["bin"], raw["y"], color=C_MOSQUITO, width=0.62)
    for row in raw.itertuples():
        left.text(row.Index, row.y + 9, f"{row.y:.0f}",
                  ha="center", fontsize=12.5, color=C_TEXT)
    style_axis(left)
    left.set(title="① 그냥 기온으로 나누면\n최고 구간이 최저 구간의 2배",
             xlabel="주간 평균기온 구간", ylabel="주간 평균 관측량 (마리)")
    left.set_ylim(0, raw["y"].max() * 1.18)
    left.text(0.5, -0.235, "기온이 아니라 '여름'을 재고 있다",
              transform=left.transAxes, ha="center", fontsize=12.5,
              color=C_MOSQUITO, fontweight="bold")

    # ── 오른쪽: 같은 시기 평년과 견준 결과 (진짜 기온 효과) ─────────────
    # 배수를 그대로 그리면 0.84와 1.12가 비슷해 보인다. 평년을 0으로 놓고
    # 몇 % 차이인지로 바꾸면 실제 크기가 보인다.
    percent = (anomaly["y"] - 1) * 100
    right.bar(anomaly["bin"], percent, color=C_TEMP, width=0.62)
    right.axhline(0, color=C_ZERO, linewidth=1.2)
    for i, (row, value) in enumerate(zip(anomaly.itertuples(), percent)):
        offset = 1.6 if value >= 0 else -3.6
        right.text(i, value + offset, f"{value:+.0f}%",
                   ha="center", fontsize=12.5, color=C_TEXT)
    style_axis(right)
    right.set(title="② '같은 시기 평년보다 따뜻했나'로 나누면\n관계가 되살아난다",
              xlabel="같은 월·주차 평년 대비 기온 차이 구간",
              ylabel="평년 대비 관측량 차이 (%)")
    right.set_ylim(percent.min() - 6, percent.max() + 6)
    gap = percent.iloc[-1] - percent.iloc[0]
    right.text(0.5, -0.235, f"가장 따뜻한 구간이 가장 추운 구간보다 {gap:+.0f}%p",
               transform=right.transAxes, ha="center", fontsize=12.5,
               color=C_TEMP, fontweight="bold")

    figure.suptitle("같은 자료, 같은 질문 — 바뀐 건 '무엇과 비교했는가'뿐이다",
                    fontsize=16, y=1.02)
    figure.tight_layout()
    save(figure, "05_temperature_bins.png")


def main():
    setup_matplotlib()
    data = load_with_anomaly()
    raw = binned(data, "avg_temp", "culex")
    anomaly = binned(data, "avg_temp_dev", "index")
    draw(raw, anomaly)

    print("① 절대 기온 구간별 관측량")
    for row in raw.itertuples():
        print(f"  {row.bin:>4}  평균기온 {row.x:5.1f}℃  →  {row.y:6.1f}마리  ({row.n}주)")
    print(f"  최고 구간이 최저 구간의 {raw['y'].iloc[-1] / raw['y'].iloc[0]:.1f}배")
    print("  ↑ 더워서가 아니라 여름이라서일 수 있다\n")

    print("② 같은 시기 평년 대비 기온 차이 구간별")
    for row in anomaly.itertuples():
        print(f"  {row.bin:>4}  평년 대비 {row.x:+5.2f}℃  →  "
              f"{(row.y - 1) * 100:+5.1f}%  ({row.n}주)")
    gap = (anomaly["y"].iloc[-1] - anomaly["y"].iloc[0]) * 100
    print(f"  가장 따뜻한 구간이 가장 추운 구간보다 {gap:+.0f}%p")
    print("  ↑ 비교 대상을 맞추는 것이 분석의 절반이다")


if __name__ == "__main__":
    main()
