"""프로젝트 공통 설정.

모든 step 스크립트가 이 파일을 불러옵니다.
경로·색상·한글 폰트를 한 곳에 모아두면 나중에 한 번만 고치면 됩니다.
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

# ── 경로 ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
IMAGES = ROOT / "images"

MOSQUITO_XLSX = RAW / "mosquito_light_trap_2008_2023.xlsx"
WEATHER_CSV = RAW / "seoul_weather_era5_2008_2023.csv"
WEEKLY_CSV = PROCESSED / "weekly_mosquito_weather_2008_2023.csv"
COVERAGE_CSV = PROCESSED / "coverage_by_year.csv"

for folder in (PROCESSED, IMAGES):
    folder.mkdir(parents=True, exist_ok=True)

# ── 분석 범위 ───────────────────────────────────────────────────────────
FIRST_YEAR, LAST_YEAR = 2008, 2023
MONTHS = range(4, 12)     # 4~11월. 모기 채집 자료가 존재하는 전체 기간
EARLY = (2008, 2015)      # 전반 8년
LATE = (2016, 2023)       # 후반 8년

# ── 색상 ────────────────────────────────────────────────────────────────
# 두 색만 씁니다. 색맹 시뮬레이션에서 구분되는지 확인한 조합입니다
# (정상 시야 ΔE 30.3, 적록색맹 21.5 — 둘 다 안전 기준을 넘습니다).
C_MOSQUITO = "#D95F02"    # 모기 / 후반기 / 늘어남
C_TEMP = "#1F78B4"        # 기온 / 전반기 / 줄어듦
C_RAIN = "#4E9F50"        # 강수
C_LINE = "#444444"        # 추세선 등 보조선
C_ZERO = "#999999"        # 0선·기준선
C_TEXT = "#333333"


def setup_matplotlib():
    """한글 폰트를 잡고 그래프 기본 스타일을 정합니다.

    OS마다 설치된 한글 폰트가 달라 후보를 여러 개 적어둡니다.
    matplotlib은 앞에서부터 찾아 첫 번째로 존재하는 폰트를 씁니다.
    """
    candidates = [
        "Malgun Gothic",       # Windows
        "AppleGothic",         # macOS
        "NanumGothic",         # 나눔고딕이 깔린 리눅스
        "NanumBarunGothic",
        "Noto Sans KR",
        "Noto Sans CJK KR",    # 리눅스 기본
        "Noto Serif CJK KR",
        # CJK 폰트는 한중일 글자가 한 파일(.ttc)에 같이 들어 있습니다.
        # matplotlib이 그 묶음에서 대표 이름 하나만 등록해 'KR'은 없고
        # 'JP'만 보이는 경우가 있는데, 한글 글자는 들어 있으므로 후보에 넣습니다.
        "Noto Sans CJK JP",
        "Noto Serif CJK JP",
    ]
    installed = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
    chosen = next((name for name in candidates if name in installed), None)
    if chosen is None:
        chosen = "DejaVu Sans"
        print("[경고] 한글 폰트를 찾지 못했습니다. 그래프의 한글이 깨집니다.")
        print("       리눅스는 'sudo apt install fonts-nanum' 후 다시 실행하세요.")

    plt.rcParams.update({
        "font.family": chosen,
        "axes.unicode_minus": False,   # 마이너스 기호가 네모로 깨지는 것 방지
        "figure.dpi": 110,
        "savefig.dpi": 180,
        "savefig.bbox": "tight",
        "axes.titlesize": 15,
        "axes.titlepad": 14,
        "axes.labelsize": 12,
        "axes.labelcolor": C_TEXT,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "xtick.color": C_TEXT,
        "ytick.color": C_TEXT,
        "legend.frameon": False,
        "legend.fontsize": 12,
    })
    return chosen


def style_axis(axis, grid="y"):
    """축을 눈에 덜 띄게 만듭니다.

    격자와 축선은 데이터를 읽는 보조 장치일 뿐입니다. 진하면 데이터와
    경쟁하므로 흐리게 두고, 위·오른쪽 테두리는 아예 없앱니다.
    """
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    for side in ("left", "bottom"):
        axis.spines[side].set_color("#CCCCCC")
    if grid:
        axis.grid(axis=grid, color="#E4E4E4", linewidth=0.8)
        axis.set_axisbelow(True)


def save(figure, filename):
    """그림을 images/ 폴더에 저장하고 경로를 출력합니다."""
    path = IMAGES / filename
    figure.savefig(path)
    plt.close(figure)
    print(f"  저장: images/{filename}")
    return path
