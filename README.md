# 서울 빨간집모기 관측량과 기상요인 분석

서울시 유문등 채집자료와 기상자료를 이용해 모기 관측량의 계절 패턴과 장기 흐름을 확인하고, 기온·강수량·습도와의 관련성을 비교한 시계열 분석 프로젝트입니다.

자세한 내용은 [REPORT.md](REPORT.md)에서 확인할 수 있습니다.

## 분석 흐름

1. 2008~2023년 주간 관측자료와 누락 구간 확인
2. 비교 조건이 같은 2010~2023년 5~10월을 분석기간으로 결정
3. 연도별 모기 관측량과 3년 이동평균으로 장기 흐름 확인
4. 같은 기간의 연도별 평균기온과 3년 이동평균 확인
5. 기온·강수량·습도와 모기 관측량의 관련성 비교

## 실행 방법

```bash
pip install -r requirements.txt
python src/step1_preprocess.py
python src/step2_explore.py
python src/step3_trend.py
python src/step4_temperature.py
python src/step6_factors.py
```

Python 3.10 이상이 필요합니다.
