const pptxgen = require("pptxgenjs");
const IMG = "/mnt/user-data/uploads/Desktop/cody3-1(new)/images/";

// ── 색: 그래프와 같은 두 가지만 (색맹 시뮬레이션 통과 조합) ──────────────
const INK = "16262C";      // 짙은 밤빛
const INK2 = "24404A";
const PAPER = "FFFFFF";
const TINT = "F1F4F6";
const MOS = "C0560F";      // 모기 / 강조
const TMP = "1B6795";      // 기온 / 보조
const MUTED = "6B7683";
const LIGHTTX = "C9D6DC";
const HEAD = "Cambria";
const BODY = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.33 x 7.5
pres.author = "모기 데이터 분석 강연";
pres.title = "요즘 모기가 줄어든 걸까?";

const W = 13.33, M = 0.75, CW = W - M * 2;

const dark = () => { const s = pres.addSlide(); s.background = { color: INK }; return s; };
const light = () => { const s = pres.addSlide(); s.background = { color: PAPER }; return s; };

function title(s, text, sub) {
  s.addText(text, { x: M, y: 0.46, w: CW, h: 0.78, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 33, bold: true, color: INK, valign: "middle" });
  if (sub) s.addText(sub, { x: M, y: 1.22, w: CW, h: 0.4, isTextBox: true, margin: 0,
    valign: "top", fontFace: BODY, fontSize: 14, color: MUTED });
}

/** 갈림길 표시 — 이 강연의 척추. 장식이 아니라 순서를 나타내는 정보다. */
function forkTitle(s, n, text, sub) {
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 0.5, w: 1.62, h: 0.44,
    fill: { color: MOS }, rectRadius: 0.06 });
  s.addText(`갈림길 ${n}`, { x: M, y: 0.5, w: 1.62, h: 0.44, isTextBox: true, margin: 0,
    align: "center", valign: "middle", fontFace: BODY, fontSize: 13, bold: true,
    color: "FFFFFF", charSpacing: 1 });
  s.addText(text, { x: M + 1.86, y: 0.42, w: CW - 1.86, h: 0.62, isTextBox: true,
    margin: 0, fontFace: HEAD, fontSize: 30, bold: true, color: INK, valign: "middle" });
  if (sub) s.addText(sub, { x: M, y: 1.12, w: CW, h: 0.42, isTextBox: true, margin: 0,
    valign: "top", fontFace: BODY, fontSize: 14, color: MUTED });
}

function question(eyebrow, text, note) {
  const s = dark();
  s.addText(eyebrow, { x: M, y: 2.3, w: CW, h: 0.35, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: MOS, charSpacing: 3 });
  s.addText(text, { x: M, y: 2.75, w: CW - 0.5, h: 1.8, isTextBox: true, margin: 0,
    fontFace: HEAD, fontSize: 40, bold: true, color: "FFFFFF", lineSpacing: 50 });
  if (note) s.addText(note, { x: M, y: 4.7, w: CW - 1.2, h: 0.9, isTextBox: true,
    margin: 0, valign: "top", fontFace: BODY, fontSize: 15, color: LIGHTTX, lineSpacing: 24 });
  return s;
}

function bullets(s, lines, x, y, w, size = 15, h = 2.2) {
  s.addText(lines.map((t, i) => ({ text: t,
      options: { bullet: true, breakLine: i !== lines.length - 1 } })),
    { x, y, w, h, isTextBox: true, margin: 0, valign: "top",
      fontFace: BODY, fontSize: size, color: INK2,
      lineSpacing: size * 1.55, paraSpaceAfter: 9 });
}

/** 코드 조각. 학생이 "저 정도면 되는구나" 하고 겁을 덜게 하는 장치. */
function code(s, text, x, y, w, h, size = 14) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: INK }, rectRadius: 0.05 });
  s.addText(text, { x: x + 0.24, y: y + 0.14, w: w - 0.48, h: h - 0.28, isTextBox: true,
    margin: 0, valign: "middle", fontFace: "Consolas", fontSize: size,
    color: "E8EEF2", lineSpacing: size * 1.6 });
}

function statRow(s, items, y, h = 1.45, size = 30) {
  const gap = 0.3, w = (CW - gap * (items.length - 1)) / items.length;
  items.forEach((it, i) => {
    const x = M + i * (w + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: TINT }, rectRadius: 0.07 });
    s.addText(it.v, { x: x + 0.2, y: y + 0.14, w: w - 0.4, h: 0.62, isTextBox: true,
      margin: 0, valign: "middle", fontFace: HEAD, fontSize: it.size || size,
      bold: true, color: it.c || INK });
    s.addText(it.l, { x: x + 0.2, y: y + 0.78, w: w - 0.4, h: h - 0.88, isTextBox: true,
      margin: 0, valign: "top", fontFace: BODY, fontSize: 12.5, color: MUTED, lineSpacing: 17 });
  });
}

function table(s, rows, x, y, w, colW, opts = {}) {
  const rightCols = opts.rightCols || [];
  const rh = opts.rh || 0.44, size = opts.size || 13.5;
  rows.forEach((row, r) => {
    const yy = y + r * rh;
    if (r === 0) s.addShape(pres.ShapeType.rect, { x, y: yy, w, h: rh, fill: { color: TINT } });
    let cx = x;
    row.forEach((cell, c) => {
      const isHead = r === 0;
      s.addText(String(cell), { x: cx + 0.16, y: yy, w: colW[c] - 0.32, h: rh,
        isTextBox: true, margin: 0, valign: "middle",
        fontFace: BODY, fontSize: isHead ? size - 1 : size,
        bold: isHead || (opts.boldRows || []).includes(r),
        color: isHead ? MUTED : ((opts.rowColors || {})[r] || INK2),
        align: rightCols.includes(c) ? "right" : "left" });
      cx += colW[c];
    });
    if (r > 0) s.addShape(pres.ShapeType.line, { x, y: yy, w, h: 0,
      line: { color: "E4E9ED", width: 1 } });
  });
}

// ══════════════════════════════════════════════════════════ 1. 표지
{
  const s = dark();
  s.addText("AI 데이터 분석 · 데이터 기반 트렌드 분석", { x: M, y: 1.7, w: 10, h: 0.4,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 14, bold: true,
    color: MOS, charSpacing: 3 });
  s.addText("요즘 모기가\n줄어든 걸까?", { x: M, y: 2.2, w: 9.5, h: 2.3, isTextBox: true,
    margin: 0, fontFace: HEAD, fontSize: 58, bold: true, color: "FFFFFF", lineSpacing: 66 });
  s.addText("서울 빨간집모기 2008~2023년, 478주의 기록으로 확인하기", { x: M, y: 4.7,
    w: 10, h: 0.45, isTextBox: true, margin: 0, fontFace: BODY, fontSize: 18, color: LIGHTTX });
  s.addText("그래프를 그리는 건 어렵지 않습니다. 어려운 건 그게 무슨 의미인지 해석하는 일입니다.",
    { x: M, y: 5.55, w: 11, h: 0.45, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 13, italic: true, color: "9BAAB4" });
  s.addNotes("오늘은 결과 발표가 아니라 '어떻게 하는지'를 보여드립니다. 30분 동안 답이 두 번 뒤집힙니다.");
}

// ══════════════════════════════════════════════════════════ 2. 두 문장
{
  const s = light();
  title(s, "우리가 늘 듣는 두 문장");
  [["\"요즘 모기가 별로 없더라\"", INK], ["\"날이 너무 더워져서 못 산대\"", MOS]]
    .forEach(([t, c], i) => {
      const x = M + i * 6.18;
      s.addShape(pres.ShapeType.roundRect, { x, y: 1.95, w: 5.85, h: 1.6,
        fill: { color: TINT }, rectRadius: 0.07 });
      s.addText(t, { x: x + 0.3, y: 1.95, w: 5.25, h: 1.6, isTextBox: true, margin: 0,
        fontFace: HEAD, fontSize: 22, bold: true, color: c, valign: "middle" });
    });
  s.addText("둘 다 그럴듯합니다. 그런데 확인된 적은 없습니다.", { x: M, y: 4.0, w: CW,
    h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 24, bold: true, color: INK });
  bullets(s, [
    "체감이 뚜렷한 주제는 곧 검증할 것이 있는 주제입니다",
    "서울시는 2008년부터 매주 유문등으로 모기를 잡아 종별 개체수를 공개해 왔습니다",
    "같은 기간 기상 자료를 나란히 놓으면 두 문장을 직접 확인할 수 있습니다",
  ], M, 4.6, CW, 15, 2.3);
  s.addNotes("체감은 데이터가 아니다. 하지만 체감을 데이터로 검증할 수는 있다.");
}

// ══════════════════════════════════════════════════════════ 3. 오늘의 뼈대
{
  const s = light();
  title(s, "오늘의 뼈대 — 답이 갈리는 네 지점",
    "분석은 계산이 아니라 판단의 연속입니다. 오늘은 그 판단을 따라갑니다");
  const forks = [
    ["①", "어디까지 볼까", "4~11월 전체 vs 여름만"],
    ["②", "0을 어떻게 볼까", "진짜 0 vs 기록 오류"],
    ["③", "원자료를 믿을까", "이상한 값을 발견했을 때"],
    ["④", "무엇과 비교할까", "절대 기온 vs 평년 대비"],
  ];
  const gap = 0.3, w = (CW - gap * 3) / 4;
  forks.forEach(([n, t, d], i) => {
    const x = M + i * (w + gap);
    s.addShape(pres.ShapeType.roundRect, { x, y: 2.1, w, h: 2.5,
      fill: { color: TINT }, rectRadius: 0.07 });
    s.addShape(pres.ShapeType.ellipse, { x: x + 0.28, y: 2.36, w: 0.5, h: 0.5,
      fill: { color: MOS } });
    s.addText(n, { x: x + 0.28, y: 2.36, w: 0.5, h: 0.5, isTextBox: true, margin: 0,
      align: "center", valign: "middle", fontFace: BODY, fontSize: 16, bold: true,
      color: "FFFFFF" });
    s.addText(t, { x: x + 0.28, y: 3.02, w: w - 0.56, h: 0.5, isTextBox: true, margin: 0,
      valign: "top", fontFace: HEAD, fontSize: 18, bold: true, color: INK });
    s.addText(d, { x: x + 0.28, y: 3.56, w: w - 0.56, h: 0.8, isTextBox: true, margin: 0,
      valign: "top", fontFace: BODY, fontSize: 13, color: MUTED, lineSpacing: 18 });
  });
  s.addText("네 지점 모두, 반대로 골랐다면 결론이 달라집니다.", { x: M, y: 5.0, w: CW,
    h: 0.5, isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 22, bold: true, color: MOS });
  s.addText("각 지점에서 먼저 여러분께 여쭙겠습니다. \"여기서 어떻게 하시겠어요?\"",
    { x: M, y: 5.6, w: CW, h: 0.45, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, color: INK2 });
  s.addNotes("이 슬라이드가 오늘의 지도. 각 갈림길에서 3초 멈추고 학생에게 물어볼 것.");
}

// ══════════════════════════════════════════════════════════ 4. 어디서 구하나
{
  const s = light();
  title(s, "어디서 자료를 구하나", "같은 주제라도 어디서 받느냐에 따라 할 수 있는 분석이 달라집니다");
  table(s, [
    ["출처", "특징", "이번 주제에는"],
    ["공공데이터포털", "정부·공공기관 자료가 가장 많음. 형식이 제각각", "쓸 만한 게 있지만 흩어져 있음"],
    ["Kaggle", "정제된 자료가 많아 시작이 편함", "한국 자료가 적음"],
    ["서울 열린데이터광장", "서울시 행정 자료. 주 단위 16년치가 그대로 있음", "채택"],
  ], M, 2.05, CW, [3.2, 5.6, 3.0], { boldRows: [3], rowColors: { 3: MOS }, rh: 0.62 });
  s.addText("서울시 보건환경연구원이 2008년부터 매주 유문등으로 채집한 모기 개체수를 종별로 공개합니다.",
    { x: M, y: 5.0, w: CW, h: 0.45, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 19, bold: true, color: INK });
  bullets(s, [
    "16년치 주 단위 시계열은 흔하지 않습니다",
    "기상 자료는 Open-Meteo의 ERA5 재분석 자료를 API로 받아 붙였습니다",
    "두 자료 모두 출처 표시 조건으로 자유롭게 쓸 수 있습니다",
  ], M, 5.6, CW, 14.5, 1.6);
  s.addNotes("데이터 출처를 명시하는 건 과제 요구사항이기도 하다. 라이선스도 확인할 것.");
}

// ══════════════════════════════════════════════════════════ 5. 무엇을 받았나
{
  const s = light();
  title(s, "무엇을 받았나");
  statRow(s, [
    { v: "478주", l: "2008~2023년 4~11월\n모기·기상 결합 완료", c: INK },
    { v: "131,763", l: "빨간집모기 누적\n전체 모기의 85.9%", c: MOS, size: 27 },
    { v: "5,844일", l: "일 단위 기상 자료\n기온·강수·습도", c: TMP },
    { v: "16개", l: "연도별 엑셀 시트\n서식이 제각각", c: INK },
  ], 2.0);
  s.addText("왜 빨간집모기 한 종만 보나", { x: M, y: 3.85, w: CW, h: 0.45,
    isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 20, bold: true, color: INK });
  bullets(s, [
    "유문등은 빛으로 유인하는 장치라 집모기류가 압도적으로 많이 잡힙니다 (85.9%)",
    "나머지 종은 주의 55~98%가 0마리라 시계열로 다룰 수 없습니다",
    "주의 — 낮에 사람을 무는 흰줄숲모기는 16년 통틀어 477마리뿐입니다. 이 자료로는 \"물리는 횟수\"에 답할 수 없습니다",
  ], M, 4.4, CW, 14.5, 2.4);
  s.addNotes("데이터가 답할 수 있는 질문과 없는 질문을 먼저 구분하는 게 중요하다.");
}

// ══════════════════════════════════════════════════════════ 6. 분석 질문
{
  const s = light();
  title(s, "무엇을 알고 싶은지부터 적습니다", "데이터를 열기 전에 질문을 정합니다");
  const qs = [
    ["01", "모기는 정말 줄고 있는가?", false],
    ["02", "온도는 실제로 오르고 있는가?", false],
    ["03", "기온 말고 영향을 주는 것이 또 있는가?", false],
    ["04", "결국 \"너무 더워서 여름에 줄었다\"는 말은 맞는가?", true],
  ];
  qs.forEach(([n, q, hl], i) => {
    const y = 2.25 + i * 1.02;
    s.addShape(pres.ShapeType.ellipse, { x: M, y, w: 0.5, h: 0.5,
      fill: { color: hl ? MOS : INK } });
    s.addText(n, { x: M, y, w: 0.5, h: 0.5, isTextBox: true, margin: 0, align: "center",
      valign: "middle", fontFace: BODY, fontSize: 13, bold: true, color: "FFFFFF" });
    s.addText(q, { x: M + 0.74, y: y - 0.04, w: 11, h: 0.58, isTextBox: true, margin: 0,
      valign: "middle", fontFace: BODY, fontSize: 19.5, bold: hl, color: hl ? MOS : INK2 });
  });
  s.addText("2번이 중요합니다. \"더워서 줄었다\"를 따지려면 더워졌다는 전제부터 확인해야 합니다.",
    { x: M, y: 6.3, w: CW, h: 0.5, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 17, bold: true, color: INK });
  s.addNotes("전제를 확인하지 않고 결론부터 따지는 게 흔한 실수. 2번이 그걸 막는다.");
}

// ══════════════════════════════════════════════════════════ 7. 전환
question("이제 자료를 엽니다", "그래서, 뭐가 보이나요?",
  "가장 단순한 것부터 합니다. 그냥 그려보기.")
  .addNotes("여기서부터 정제 구간. 지루해 보이지만 여기 판단이 뒤의 결론을 전부 바꾼다.");

// ══════════════════════════════════════════════════════════ 8. 열어보기
{
  const s = light();
  title(s, "일단 그려보고, 기본 정보를 확인합니다");
  s.addImage({ path: IMG + "01_weekly_raw.png", x: M, y: 1.8, w: 8.3, h: 3.2 });
  code(s, "df.info()\n\n478 entries\n15 columns\nNon-Null: 478\n결측 0건",
    9.35, 1.8, 3.23, 1.75, 12);
  bullets(s, [
    "0마리 ~ 1,401마리",
    "중앙값 225.5마리",
    "평균 275.7마리",
  ], 9.35, 3.75, 3.23, 13.5, 1.1);
  s.addText("해마다 같은 봉우리가 반복되고 높이는 들쭉날쭉합니다.\n정작 '16년간 늘었나 줄었나'는 안 보입니다.",
    { x: M, y: 5.35, w: CW, h: 0.85, isTextBox: true, margin: 0, valign: "top",
      fontFace: HEAD, fontSize: 19, bold: true, color: INK, lineSpacing: 27 });
  s.addText("계절에 따른 오르내림이 너무 커서 장기 변화를 덮고 있습니다.",
    { x: M, y: 6.3, w: CW, h: 0.4, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, color: MUTED });
  s.addNotes("info()가 '결측 0'이라고 말한다. 이 말을 믿어도 될까? — 다음 슬라이드로.");
}

// ══════════════════════════════════════════════════════════ 9. 갈림길 ①
{
  const s = light();
  forkTitle(s, "①", "\"결측 0\"을 믿어도 될까요?");
  s.addImage({ path: IMG + "02_coverage.png", x: M, y: 1.6, w: 7.35, h: 4.6 });
  s.addText("아예 없는 행은\n결측으로 세어지지 않습니다", { x: 8.75, y: 1.75, w: 3.83, h: 0.9,
    isTextBox: true, margin: 0, valign: "top", fontFace: HEAD, fontSize: 20, bold: true,
    color: MOS, lineSpacing: 28 });
  bullets(s, [
    "통째로 빠진 달이 6개",
    "2009년은 10·11월 없음",
    "2020~22년은 4월 없음",
    "2023년은 11월 없음",
    "월별 주 수도 1~5주로 제각각",
  ], 8.75, 2.85, 3.83, 14, 2.0);
  s.addShape(pres.ShapeType.roundRect, { x: 8.75, y: 4.95, w: 3.83, h: 1.4,
    fill: { color: TINT }, rectRadius: 0.07 });
  s.addText("그냥 연도별 평균을 비교하면\n자료가 없어서 생긴 차이를\n모기 수 변화로 읽게 됩니다",
    { x: 9.0, y: 5.12, w: 3.4, h: 1.1, isTextBox: true, margin: 0, valign: "top",
      fontFace: BODY, fontSize: 13.5, color: INK2, lineSpacing: 20 });
  s.addNotes("여기서 물어볼 것: '연도마다 채집 기간이 다른데 어떻게 비교하시겠어요?' 답은 12번 슬라이드.");
}

// ══════════════════════════════════════════════════════════ 10. 갈림길 ②
{
  const s = light();
  forkTitle(s, "②", "0마리인 주가 8개 있습니다. 다 같은 0일까요?",
    "옆 칸(전체 모기 수)을 보면 성격이 갈립니다");
  table(s, [
    ["주차", "빨간집모기", "전체 모기", "판정", "처리"],
    ["2010 4월 1·5주, 11월 4주", "0", "0", "진짜 0 (초봄·늦가을)", "유지"],
    ["2011 4월 3·4주", "0", "1", "진짜 0에 가까움", "유지"],
    ["2021 9월 3주", "0", "2", "채집이 거의 안 된 주", "유지"],
    ["2008 6월 1주", "0", "47", "의심", "제외"],
    ["2009 9월 3주", "0", "418", "기록 오류", "제외"],
  ], M, 1.85, CW, [4.2, 1.7, 1.5, 3.3, 1.13],
     { boldRows: [5], rowColors: { 5: MOS }, rh: 0.52, rightCols: [1, 2] });
  s.addText("9월 성수기에 다른 종은 418마리가 잡혔는데, 전체의 86%를 차지하는 종만 정확히 0.",
    { x: M, y: 5.1, w: CW, h: 0.45, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 19, bold: true, color: INK });
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 5.65, w: CW, h: 0.95,
    fill: { color: TINT }, rectRadius: 0.07 });
  s.addText("처리 기준 — 전체 모기가 30마리 이상인데 빨간집모기가 0인 주는 기록 오류로 보고 제외한다.\n임의의 값을 채워 넣지는 않는다. 모르는 것은 모르는 채로 둔다.   480주 → 478주",
    { x: M + 0.3, y: 5.65, w: CW - 0.6, h: 0.95, isTextBox: true, margin: 0,
      valign: "middle", fontFace: BODY, fontSize: 14, color: INK2, lineSpacing: 21 });
  s.addNotes("여기서 물어볼 것: '0마리인데 옆 칸이 418이면 어떻게 하시겠어요?' — 옆 칸이 있어서 판별이 된다는 게 핵심.");
}

// ══════════════════════════════════════════════════════════ 11. 갈림길 ③
{
  const s = light();
  forkTitle(s, "③", "원자료를 믿어도 될까요?",
    "서로 다른 연도의 같은 주차 값이 일치하는지 120개 연도쌍을 전수 검사했습니다");
  table(s, [
    ["주차", "2009", "2010"],
    ["5월 3주", "98", "98"],
    ["6월 1주", "210", "210"],
    ["6월 2주", "638", "638"],
    ["7월 1주", "768", "768"],
    ["7월 2주", "459", "459"],
    ["7월 3주", "822", "822"],
  ], M, 1.9, 5.1, [2.3, 1.4, 1.4], { rh: 0.44, rightCols: [1, 2] });
  s.addText("2009·2010은 공통 22주 중 6주가 값까지 같습니다.", { x: 6.8, y: 1.95, w: 5.78,
    h: 0.9, isTextBox: true, margin: 0, valign: "top", fontFace: HEAD, fontSize: 21,
    bold: true, color: MOS, lineSpacing: 29 });
  s.addText("나머지 119개 연도쌍은 최대 1주만 일치합니다.\n638·768·822 같은 세 자리 수가 우연히 겹칠 확률은 사실상 0입니다.",
    { x: 6.8, y: 2.95, w: 5.78, h: 1.1, isTextBox: true, margin: 0, valign: "top",
      fontFace: BODY, fontSize: 14.5, color: INK2, lineSpacing: 22 });
  s.addShape(pres.ShapeType.roundRect, { x: 6.8, y: 4.2, w: 5.78, h: 1.55,
    fill: { color: TINT }, rectRadius: 0.07 });
  s.addText("그래서 어떻게 했나\n\n지우지 않았습니다. 어느 쪽이 맞는지\n알 수 없으니까요. 검사 결과를 파일로\n남기고 리포트 한계점에 밝혔습니다.",
    { x: 7.1, y: 4.34, w: 5.25, h: 1.3, isTextBox: true, margin: 0, valign: "top",
      fontFace: BODY, fontSize: 13.5, color: INK2, lineSpacing: 19 });
  s.addText("AI는 이걸 못 찾았습니다. 값을 눈으로 훑다가 사람이 발견했습니다.",
    { x: M, y: 6.15, w: CW, h: 0.45, isTextBox: true, margin: 0,
      fontFace: HEAD, fontSize: 17, bold: true, color: INK });
  s.addNotes("여기서 물어볼 것: '이상한 값을 찾았는데 어느 쪽이 맞는지 모르면?' — 지우는 것도 자료를 만드는 것.");
}

// ══════════════════════════════════════════════════════════ 12. 계절 걷어내기
{
  const s = light();
  title(s, "계절을 걷어내는 법 — 코드는 한 줄입니다",
    "갈림길 ①의 답. 각 주를 '그 월·주차의 평년값'으로 나눕니다");
  code(s, 'd["index"] = d.culex / d.groupby(["month", "week_of_month"]).culex.transform("mean")',
    M, 2.0, CW, 0.95, 14);
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 3.2, w: CW, h: 1.15,
    fill: { color: TINT }, rectRadius: 0.07 });
  s.addText([
    { text: "7월 3주에 800마리", options: { bold: true, color: INK } },
    { text: "   ÷   ", options: { color: MUTED } },
    { text: "7월 3주 평년 534마리", options: { bold: true, color: INK } },
    { text: "   =   ", options: { color: MUTED } },
    { text: "1.50배", options: { bold: true, color: MOS, fontSize: 30 } },
  ], { x: M + 0.4, y: 3.2, w: CW - 0.8, h: 1.15, isTextBox: true, margin: 0,
      valign: "middle", fontFace: HEAD, fontSize: 22 });
  bullets(s, [
    "4월이든 7월이든 모두 '평년 = 1.0' 기준이 되어 서로 비교할 수 있습니다",
    "관측 기간이 다른 연도끼리도 공정하게 견줄 수 있습니다",
    "평년값을 만들 근거가 부족한 주차(5개 연도 미만)는 제외했습니다 — 478주 → 463주",
    "표본 2개로 만든 평균을 '기준선'이라고 부를 수는 없기 때문입니다",
  ], M, 4.65, CW, 15, 2.4);
  s.addNotes("이 한 줄이 이 분석의 절반. 학생이 겁먹지 않게 '이게 다입니다'라고 말할 것.");
}

// ══════════════════════════════════════════════════════════ 13. 전환
question("정제가 끝났습니다", "이제 네 질문에 답합니다",
  "여기까지가 준비. 지금부터가 분석입니다.");

// ══════════════════════════════════════════════════════════ 14. Q1
{
  const s = light();
  title(s, "질문 1 — 모기는 정말 줄었는가");
  s.addImage({ path: IMG + "03_seasonal_shift.png", x: 1.9, y: 1.6, w: 9.5, h: 5.22 });
  s.addNotes("첫 번째 반전. 전체는 p=0.881로 평평한데, 나누면 여름 −35% / 봄가을 +149%. 상쇄됐던 것.");
}

// ══════════════════════════════════════════════════════════ 15. Q1 정리
{
  const s = dark();
  s.addText("질문 1의 답", { x: M, y: 1.45, w: CW, h: 0.4, isTextBox: true, margin: 0,
    fontFace: BODY, fontSize: 13, bold: true, color: MOS, charSpacing: 3 });
  s.addText("모기는 줄지 않았습니다.\n시기가 옮겨갔습니다.", { x: M, y: 1.95, w: CW, h: 1.9,
    isTextBox: true, margin: 0, fontFace: HEAD, fontSize: 44, bold: true,
    color: "FFFFFF", lineSpacing: 56 });
  const rows = [["전체 4~11월", "변화 없음", "p = 0.881"],
                ["여름 6~8월", "1.17배 → 0.84배", "p = 0.051"],
                ["봄·가을", "0.84배 → 1.16배", "p = 0.053"]];
  rows.forEach(([a, b, c], i) => {
    const y = 4.15 + i * 0.62;
    s.addText(a, { x: M, y, w: 3.2, h: 0.5, isTextBox: true, margin: 0, valign: "middle",
      fontFace: BODY, fontSize: 15, color: LIGHTTX });
    s.addText(b, { x: M + 3.2, y, w: 3.6, h: 0.5, isTextBox: true, margin: 0,
      valign: "middle", fontFace: HEAD, fontSize: 17, bold: true, color: "FFFFFF" });
    s.addText(c, { x: M + 6.8, y, w: 2.4, h: 0.5, isTextBox: true, margin: 0,
      valign: "middle", fontFace: BODY, fontSize: 14, color: LIGHTTX });
  });
  s.addText("만약 6~10월만 잘랐다면 \"줄었다\"는 정반대 결론이 나왔을 겁니다. — 갈림길 ①",
    { x: M, y: 6.25, w: CW, h: 0.5, isTextBox: true, margin: 0,
      fontFace: BODY, fontSize: 15, italic: true, color: MOS });
  s.addNotes("p가 0.051, 0.053이라는 것도 정직하게 말할 것. 16개 점으로는 확정이 어렵다.");
}

// ══════════════════════════════════════════════════════════ 16. Q2
{
  const s = light();
  title(s, "질문 2 — 온도는 실제로 올랐는가",
    "\"더워서 줄었다\"를 따지려면 더워졌다는 전제부터 확인해야 합니다");
  s.addImage({ path: IMG + "04_temperature_trend.png", x: M, y: 1.85, w: 11.83, h: 4.9 });
  s.addNotes("핵심: 평균기온은 완만, 폭염일은 4.75일 → 11.25일로 2.4배. 둘은 다른 이야기다.");
}

// ══════════════════════════════════════════════════════════ 17. 갈림길 ④
{
  const s = light();
  forkTitle(s, "④", "기온과 모기, 무엇과 비교할까요?");
  s.addImage({ path: IMG + "05_temperature_bins.png", x: M, y: 1.75, w: 11.83, h: 5.07 });
  s.addNotes("오늘 강의에서 제일 중요한 슬라이드. 왼쪽은 기온이 아니라 '여름'을 재고 있다. 3초 멈추고 물어볼 것.");
}

// ══════════════════════════════════════════════════════════ 18. Q3
{
  const s = light();
  title(s, "질문 3 — 무엇이, 얼마나 영향을 주는가",
    "종속변수에 로그를 씌우고 독립변수를 표준화하면, 계수가 그대로 '몇 %'가 됩니다");
  s.addImage({ path: IMG + "06_regression_effects.png", x: 1.72, y: 1.9, w: 9.9, h: 5.0 });
  s.addNotes("표준화 계수 0.195를 학생에게 설명할 수 없다. +19.5%는 바로 알아듣는다. 계산은 같고 읽는 법만 다르다.");
}

// ══════════════════════════════════════════════════════════ 19. Q4
{
  const s = light();
  title(s, "질문 4 — 그래서 \"더워서 줄었다\"가 맞는가",
    "앞의 회귀는 '주 단위 날씨 변동'을 잽니다. 16년 온난화의 효과는 한 단계 더 계산해야 합니다");
  s.addImage({ path: IMG + "07_warming_vs_actual.png", x: 1.4, y: 1.9, w: 10.5, h: 5.2 });
  s.addNotes("두 번째 반전. 폭염 효과를 관대하게 믿어줘도 −1.9%. 실제는 −31.4%. 31% 중 2%를 설명한다.");
}

// ══════════════════════════════════════════════════════════ 20. 인사이트
{
  const s = light();
  title(s, "인사이트", "관찰(Fact) · 원인(Why) · 행동(Action) 세 단으로 씁니다");
  const cards = [
    ["모기는 줄지 않았다. 옮겨갔다",
     "여름 1.17 → 0.84배, 봄·가을 0.84 → 1.16배. 전체는 p=0.881로 변화 없음",
     "방역 일정을 여름에 몰아둔 관행을 재검토. 10~11월 강화, 4~5월 조기 개시 검토"],
    ["\"더워서 없다\"는 크기가 안 맞는다",
     "폭염일 2.4배 증가로 설명되는 여름 감소는 −1.9%. 실제는 −31.4%",
     "단일 원인 설명을 채택하기 전에 방역 예산·살충제 사용량 자료를 확보해 함께 넣어야 함"],
    ["비교 대상을 맞추지 않으면 답이 뒤집힌다",
     "절대 기온으로 2.0배 → 평년 대비로 26%p. 6~10월이면 \"감소\", 4~11월이면 \"이동\"",
     "어떤 시계열이든 '무엇과 비교하는가'를 먼저 정하고 시작할 것"],
  ];
  cards.forEach(([t, f, a], i) => {
    const y = 2.05 + i * 1.55;
    s.addShape(pres.ShapeType.ellipse, { x: M, y: y + 0.06, w: 0.44, h: 0.44,
      fill: { color: MOS } });
    s.addText(String(i + 1), { x: M, y: y + 0.06, w: 0.44, h: 0.44, isTextBox: true,
      margin: 0, align: "center", valign: "middle", fontFace: BODY, fontSize: 13,
      bold: true, color: "FFFFFF" });
    s.addText(t, { x: M + 0.66, y, w: 11.9, h: 0.45, isTextBox: true, margin: 0,
      valign: "top", fontFace: HEAD, fontSize: 19, bold: true, color: INK });
    s.addText([
      { text: "관찰  ", options: { bold: true, color: MOS, fontSize: 12 } },
      { text: f, options: { color: INK2 } },
    ], { x: M + 0.66, y: y + 0.48, w: 11.9, h: 0.42, isTextBox: true, margin: 0,
        valign: "top", fontFace: BODY, fontSize: 13.5 });
    s.addText([
      { text: "행동  ", options: { bold: true, color: TMP, fontSize: 12 } },
      { text: a, options: { color: INK2 } },
    ], { x: M + 0.66, y: y + 0.92, w: 11.9, h: 0.42, isTextBox: true, margin: 0,
        valign: "top", fontFace: BODY, fontSize: 13.5 });
  });
  s.addNotes("지침의 인사이트 템플릿이 Fact/Why/Action 3단. Action이 빠지기 쉬우니 강조.");
}

// ══════════════════════════════════════════════════════════ 21. 한계
{
  const s = light();
  title(s, "여기서 멈춰야 합니다", "좋은 분석은 자기가 모르는 것을 압니다");
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 2.0, w: 4.3, h: 2.1,
    fill: { color: INK }, rectRadius: 0.07 });
  s.addText("R² = 0.050", { x: M + 0.35, y: 2.25, w: 3.6, h: 0.7, isTextBox: true,
    margin: 0, valign: "middle", fontFace: HEAD, fontSize: 34, bold: true, color: "FFFFFF" });
  s.addText("날씨로 설명되는 건\n주 단위 변동의 5.0%뿐입니다", { x: M + 0.35, y: 3.0, w: 3.6,
    h: 0.9, isTextBox: true, margin: 0, valign: "top", fontFace: BODY, fontSize: 14,
    color: LIGHTTX, lineSpacing: 20 });
  s.addText("나머지 95%는 어디에?", { x: 5.45, y: 2.05, w: 7.1, h: 0.45, isTextBox: true,
    margin: 0, valign: "top", fontFace: HEAD, fontSize: 21, bold: true, color: INK });
  bullets(s, [
    "방역 활동의 강도와 시점 — 자료에 없음",
    "유문등의 개수·위치·장비 변경 — 원자료에 기록이 없음",
    "도시 개발에 따른 서식지 변화, 정화조·하수구 관리",
  ], 5.45, 2.6, 7.1, 14.5, 1.6);
  s.addText("그 밖의 한계", { x: M, y: 4.45, w: CW, h: 0.4, isTextBox: true, margin: 0,
    valign: "top", fontFace: HEAD, fontSize: 18, bold: true, color: INK });
  bullets(s, [
    "2009·2010년 복사 의심 6주를 그대로 두었습니다. 전반기 평균이 왜곡됐을 수 있습니다",
    "16년은 짧습니다. 계절별·기온 추세의 p가 모두 0.05~0.10 사이입니다",
    "회귀계수는 관련성이지 인과가 아닙니다 — 오늘 말한 '왜'는 전부 가설입니다",
  ], M, 4.95, CW, 14, 1.9);
  s.addNotes("한계를 '말하는 것'과 '측정하는 것'은 다르다. R²를 제시하는 게 후자.");
}

// ══════════════════════════════════════════════════════════ 22. AI 검증
{
  const s = light();
  title(s, "AI가 만든 걸 어떻게 검증했나",
    "지침의 요구 — \"생성된 코드·해석을 검증할 수 있다\". 실제로 걸러낸 것들입니다");
  table(s, [
    ["검증한 것", "잡아낸 것"],
    ["원자료를 눈으로 대조", "AI는 못 찾았다. 2009·2010년 6개 주차가 동일한 것을 사람이 발견"],
    ["0의 성격 확인", "AI의 첫 코드는 2009년 9월 3주(0/418)를 실제 0으로 처리하고 있었다"],
    ["결과가 질문에 답하는지", "AI 회귀 차트는 '주 단위 변동'을 재고 있었다. 우리 질문은 '16년 온난화'였다"],
    ["통계 가정 점검", "16개 점에 HAC를 쓰니 p가 0.056 → 0.008. 소표본에서 못 믿을 값이라 제거"],
    ["그래프를 전부 열어보기", "AI는 7장 중 4장을 안 열어보고 넘겼다. 축 왜곡·글자 겹침이 남아 있었다"],
  ], M, 2.0, CW, [3.5, 8.33], { rh: 0.66, size: 13 });
  s.addShape(pres.ShapeType.roundRect, { x: M, y: 5.55, w: CW, h: 1.0,
    fill: { color: TINT }, rectRadius: 0.07 });
  s.addText("AI는 빠르게 만들어 줍니다. 그런데 '이게 내 질문에 답하고 있나'는 사람만 물을 수 있습니다.",
    { x: M + 0.35, y: 5.55, w: CW - 0.7, h: 1.0, isTextBox: true, margin: 0,
      valign: "middle", fontFace: HEAD, fontSize: 19, bold: true, color: INK });
  s.addNotes("이 슬라이드가 오늘 제일 오래 남을 것. 실패 사례라서 그렇다.");
}

// ══════════════════════════════════════════════════════════ 23. 체크리스트
{
  const s = dark();
  s.addText("이제 여러분 차례입니다", { x: M, y: 1.3, w: CW, h: 0.9, isTextBox: true,
    margin: 0, fontFace: HEAD, fontSize: 38, bold: true, color: "FFFFFF" });
  s.addText("주제는 달라도 됩니다. 순서는 같습니다.", { x: M, y: 2.2, w: CW, h: 0.45,
    isTextBox: true, margin: 0, fontFace: BODY, fontSize: 16, color: LIGHTTX });
  const items = [
    ["시계열 자료 1개 선정", "출처·기간 명시, 데이터 포인트 100개 이상"],
    ["분석 질문 3개 이상", "데이터를 열기 전에 적을 것"],
    ["결측치·이상치 처리", "무엇을 어떤 기준으로 처리했는지 설명할 수 있을 것"],
    ["시계열 분석 기법 2가지 이상", "왜 그 기법을 골랐는지 한 줄씩"],
    ["시각화 2개 이상", "한 장에 한 메시지"],
    ["인사이트 3개 이상", "관찰 · 원인 · 행동 세 단으로"],
    ["AI 사용 로그", "무엇을 시켰고, 어떻게 검증했는지"],
  ];
  items.forEach(([t, d], i) => {
    const y = 2.9 + i * 0.55;
    s.addShape(pres.ShapeType.rect, { x: M, y: y + 0.09, w: 0.24, h: 0.24,
      fill: { color: INK }, line: { color: MOS, width: 1.6 } });
    s.addText(t, { x: M + 0.5, y, w: 4.5, h: 0.44, isTextBox: true, margin: 0,
      valign: "middle", fontFace: BODY, fontSize: 15, bold: true, color: "FFFFFF" });
    s.addText(d, { x: M + 5.1, y, w: 7.4, h: 0.44, isTextBox: true, margin: 0,
      valign: "middle", fontFace: BODY, fontSize: 14, color: LIGHTTX });
  });
  s.addNotes("마지막. 학생이 이 화면을 사진 찍게 둘 것.");
}

pres.writeFile({ fileName: "/tmp/build/slides/모기_데이터분석_강연.pptx" })
  .then(f => console.log("생성 완료:", f));
