"""[2단계] 자료를 열어보고, 어디가 비었는지 확인한다.

분석의 첫 동작은 계산이 아니라 '보기'다. 두 가지를 본다.

  ① 자료가 어떻게 생겼나  — info()로 행·열·자료형·결측을 확인
  ② 어디가 비었나        — 연도별로 몇 월 몇 주를 실제로 채집했나

②가 중요하다. info()는 "결측 0"이라고 말하지만, 그건 '표에 적힌 값 중'
빈 칸이 없다는 뜻일 뿐이다. **아예 행이 없는 주는 결측으로 잡히지 않는다.**
채집을 안 한 달은 표에 아예 나타나지 않으므로, 따로 세어봐야 보인다.

실행:  python src/step2_explore.py
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (C_MOSQUITO, C_TEMP, C_TEXT, MONTHS, WEEKLY_CSV,
                    save, setup_matplotlib, style_axis)

MONTH_NAMES = {m: f"{m}월" for m in MONTHS}


def load():
    data = pd.read_csv(WEEKLY_CSV, parse_dates=["week_start", "week_end"])
    return data.sort_values(["year", "month", "week_of_month"]).reset_index(drop=True)


def draw_raw(data):
    """480주를 그대로 그린다. 이 그림의 역할은 '무엇이 안 보이는지' 보여주기다."""
    figure, axis = plt.subplots(figsize=(14, 5.4))

    # 연도별로 끊어 그린다. 겨울에는 채집을 하지 않으므로 12~3월을 선으로
    # 이으면 있지도 않은 자료를 있는 것처럼 보여주게 된다.
    for _, group in data.groupby("year"):
        axis.plot(group["week_start"], group["culex"],
                  color=C_MOSQUITO, linewidth=1.6, marker="o", markersize=3,
                  markerfacecolor="white", markeredgewidth=0.9)

    # 가장 높았던 주만 짚어준다. 봉우리 위쪽 빈 자리에 놓아 선을 가리지 않게 한다.
    peak = data.loc[data["culex"].idxmax()]
    axis.annotate(f"최고 {peak['culex']:,}마리 · {peak['year']}년 {peak['week_label']}",
                  xy=(peak["week_start"], peak["culex"]),
                  xytext=(0, 16), textcoords="offset points",
                  ha="center", fontsize=11, color=C_TEXT)

    style_axis(axis)
    axis.set(title=f"서울 빨간집모기 주간 관측량 — 2008~2023년 4~11월, {len(data)}주",
             xlabel="연도", ylabel="관측 개체수 (마리)")
    axis.set_ylim(0, data["culex"].max() * 1.13)   # 주석이 들어갈 자리
    figure.tight_layout()
    save(figure, "01_weekly_raw.png")


def coverage_grid(data):
    """연도 × 월로 실제 채집된 주 수를 센다."""
    grid = data.pivot_table(index="year", columns="month",
                            values="culex", aggfunc="size")
    return grid.reindex(columns=list(MONTHS)).fillna(0).astype(int)


def draw_coverage(grid):
    """관측 현황을 격자로 그린다.

    색은 한 가지 색의 진하기만 쓴다(주 수가 많을수록 진하게). 여러 색을
    쓰면 '많다/적다'가 아니라 '종류가 다르다'로 읽힌다.
    채집을 아예 안 한 칸은 색이 아니라 빗금으로 구분한다.
    """
    figure, axis = plt.subplots(figsize=(11.5, 7.2))
    values = grid.to_numpy(float)
    masked = np.ma.masked_where(values == 0, values)

    cmap = plt.get_cmap("Blues").copy()
    axis.imshow(masked, cmap=cmap, vmin=0, vmax=6, aspect="auto")

    for y in range(values.shape[0]):
        for x in range(values.shape[1]):
            n = int(values[y, x])
            if n == 0:
                axis.add_patch(plt.Rectangle((x - .5, y - .5), 1, 1,
                                             facecolor="#F2F2F2", edgecolor="white",
                                             hatch="///", linewidth=1))
                axis.text(x, y, "없음", ha="center", va="center",
                          fontsize=10, color="#B0413E", fontweight="bold")
            else:
                axis.text(x, y, str(n), ha="center", va="center", fontsize=11.5,
                          color="white" if n >= 4 else C_TEXT)

    axis.set_xticks(range(len(grid.columns)), [MONTH_NAMES[m] for m in grid.columns])
    axis.set_yticks(range(len(grid.index)), grid.index)
    axis.set_xticks(np.arange(-.5, len(grid.columns), 1), minor=True)
    axis.set_yticks(np.arange(-.5, len(grid.index), 1), minor=True)
    axis.grid(which="minor", color="white", linewidth=2)
    axis.tick_params(which="minor", length=0)
    for side in axis.spines.values():
        side.set_visible(False)

    empty = int((values == 0).sum())
    axis.set(title="채집한 주가 해마다 다르다 — 칸 안 숫자는 그달에 채집한 주 수")
    axis.text(0, -0.085, f"통째로 빠진 달 {empty}개. "
              "info()는 '결측 0'이라고 하지만, 아예 없는 행은 결측으로 세어지지 않는다.",
              transform=axis.transAxes, ha="left", fontsize=12.5, color="#6B7683")
    figure.tight_layout()
    save(figure, "02_coverage.png")


def main():
    setup_matplotlib()
    data = load()

    print("═══ 자료 기본 정보 ═══")
    data.info()

    print("\n═══ 관측 현황 (연도 × 월, 실제 채집한 주 수) ═══")
    grid = coverage_grid(data)
    print(grid.rename(columns=MONTH_NAMES).to_string())
    print(f"\n통째로 빠진 달: {(grid == 0).sum().sum()}개")
    print("  ", ", ".join(f"{y}년 {MONTH_NAMES[m]}"
                          for y in grid.index for m in grid.columns if grid.loc[y, m] == 0))

    print("\n═══ 관측량 요약 ═══")
    print(data["culex"].describe().round(1).to_string())

    draw_raw(data)
    draw_coverage(grid)
    print("\n해마다 같은 모양의 봉우리가 반복되고, 봉우리 높이는 들쭉날쭉하다.")
    print("정작 '16년 동안 늘었나 줄었나'는 이 그림으로 알 수 없다.")
    print("계절에 따른 오르내림이 너무 커서 장기 변화를 덮기 때문이다.")


if __name__ == "__main__":
    main()
