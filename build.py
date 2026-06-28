from pathlib import Path
import html
import re
import pandas as pd
import shutil

TSV = Path("questions.tsv")
OUT = Path("docs/index.html")
IMG_DIR = "pdf_images"

IMG_PAT = re.compile(r"IMAGEIMAGEIMAGE([A-Za-z0-9_]+)__DOT__([A-Za-z0-9]+)")


def render_cell(value: str) -> str:
    s = html.escape(str(value or ""))

    def repl(m: re.Match) -> str:
        name = m.group(1)
        ext = m.group(2)
        src = f"{IMG_DIR}/{name}.{ext}"
        alt = f"{name}.{ext}"
        return f'<img src="{src}" class="qimg" alt="{html.escape(alt)}">'

    s = IMG_PAT.sub(repl, s)
    return s.replace("\n", "<br>")


def main() -> None:
    df = pd.read_csv(TSV, sep="\t", dtype=str, keep_default_na=False)

    required = ["qid", "answer", "tigan", "p1", "p2", "p3"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if "tail" not in df.columns:
        df["tail"] = ""

    rows = []
    for _, r in df.iterrows():
        qid = html.escape(str(r["qid"]))
        answer = html.escape(str(r["answer"]).strip())
        tigan = render_cell(r["tigan"])
        p1 = render_cell(r["p1"])
        p2 = render_cell(r["p2"])
        p3 = render_cell(r["p3"])
        tail = render_cell(r.get("tail", ""))

        tail_html = f'<div class="tail">{tail}</div>' if tail.strip() else ""

        rows.append(f"""
<section class="question" data-qid="{qid}" data-answer="{answer}">
  <div class="qid">#{qid}</div>
  <div class="tigan">{tigan}</div>
  <div class="choices">
    <button class="choice" data-choice="1"><span class="label">(1)</span><span class="choice-text">{p1}</span></button>
    <button class="choice" data-choice="2"><span class="label">(2)</span><span class="choice-text">{p2}</span></button>
    <button class="choice" data-choice="3"><span class="label">(3)</span><span class="choice-text">{p3}</span></button>
  </div>
  {tail_html}
  <div class="feedback"></div>
</section>
""")

    docs = Path("docs")
    docs.mkdir(exist_ok=True)
    dst = docs / "pdf_images"
    if dst.exists():
        shutil.rmtree(dst)
    if Path("pdf_images").exists():
        shutil.copytree("pdf_images", dst)

    html_text = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>汽車筆試練習</title>
<style>
:root {{
  --bg: #f7f7f7;
  --card: #ffffff;
  --line: #d8d8d8;
  --text: #222;
  --muted: #666;
  --hover: #eef3ff;
  --correct: #dff3df;
  --wrong: #ffdede;
  --picked: #444;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Noto Sans TC", "Microsoft JhengHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.55;
}}
.toolbar {{
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 10px 14px;
  background: rgba(255,255,255,0.96);
  border-bottom: 1px solid var(--line);
}}
.toolbar button, .toolbar input {{ font-size: 14px; }}
.status {{ color: var(--muted); margin-left: auto; }}
main {{
  max-width: 1100px;
  margin: 18px auto 60px;
  padding: 0 12px;
}}
.question {{
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 14px;
  margin: 14px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}}
.qid {{
  font-weight: 700;
  color: var(--muted);
  margin-bottom: 6px;
}}
.tigan {{
  font-size: 18px;
  margin: 8px 0 12px;
}}
.choices {{
  display: grid;
  gap: 8px;
}}
.choice {{
  display: grid;
  grid-template-columns: 54px 1fr;
  align-items: start;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: white;
  color: inherit;
  text-align: left;
  font: inherit;
  cursor: pointer;
}}
.choice:hover {{ background: var(--hover); }}
.choice .label {{ font-weight: 700; color: var(--muted); }}
.choice.correct {{ background: var(--correct); border-color: #8bb98b; font-weight: 700; }}
.choice.wrong {{ background: var(--wrong); border-color: #d48d8d; font-weight: 700; }}
.choice.picked {{ outline: 2px solid var(--picked); }}
.tail {{
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  color: #333;
}}
.feedback {{
  margin-top: 8px;
  font-weight: 700;
}}
.qimg {{
  max-width: 140px;
  max-height: 140px;
  display: inline-block;
  vertical-align: middle;
  margin: 4px 6px 4px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}}
.hidden-answer .choice.correct {{
  background: white;
  border-color: var(--line);
  font-weight: inherit;
}}
.hidden-answer .choice.wrong {{
  background: white;
  border-color: var(--line);
  font-weight: inherit;
}}
@media (max-width: 720px) {{
  .choice {{ grid-template-columns: 44px 1fr; }}
  .tigan {{ font-size: 16px; }}
  .status {{ width: 100%; margin-left: 0; }}
}}
</style>
</head>
<body>
<div class="toolbar">
  <button onclick="exportRecords()">匯出作答紀錄</button>
  <label>匯入紀錄 <input type="file" accept=".json" onchange="importRecords(this.files[0])"></label>
  <button onclick="clearRecords()">清空紀錄</button>
  <button onclick="toggleAnswers()" id="toggleBtn">隱藏已作答答案</button>
  <span class="status" id="status"></span>
</div>
<main>
<h1>汽車筆試練習</h1>
{''.join(rows)}
</main>
<script>
const STORE_KEY = "drv_question_answers_v1";
let records = JSON.parse(localStorage.getItem(STORE_KEY) || "{{}}");
let showAnsweredAnswers = true;

function saveRecords() {{
  localStorage.setItem(STORE_KEY, JSON.stringify(records));
  updateStatus();
}}

function updateStatus() {{
  const total = document.querySelectorAll(".question").length;
  const answered = Object.keys(records).length;
  const correct = Object.values(records).filter(r => r.correct).length;
  document.getElementById("status").textContent = `已作答 ${{answered}}/${{total}}，正確 ${{correct}}`;
}}

function resetRow(tr) {{
  tr.querySelectorAll(".choice").forEach(td => {{
    td.classList.remove("picked", "correct", "wrong");
  }});
  tr.querySelector(".feedback").textContent = "";
}}

function markRow(tr, choice, persist = true) {{
  const qid = tr.dataset.qid;
  const answer = tr.dataset.answer;
  const isCorrect = choice === answer;

  resetRow(tr);

  tr.querySelectorAll(".choice").forEach(td => {{
    const c = td.dataset.choice;
    if (c === answer) td.classList.add("correct");
    if (c === choice && c !== answer) td.classList.add("wrong");
    if (c === choice) td.classList.add("picked");
  }});

  tr.querySelector(".feedback").textContent = isCorrect ? "✅ 正確" : `❌ 錯誤，答案是 (${{answer}})`;

  if (persist) {{
    records[qid] = {{
      choice,
      answer,
      correct: isCorrect,
      ts: new Date().toISOString()
    }};
    saveRecords();
  }}
}}

function applyVisibility() {{
  document.querySelectorAll(".question").forEach(tr => {{
    tr.classList.toggle("hidden-answer", !showAnsweredAnswers);
  }});
  document.getElementById("toggleBtn").textContent = showAnsweredAnswers ? "隱藏已作答答案" : "顯示已作答答案";
}}

function exportRecords() {{
  const blob = new Blob([JSON.stringify(records, null, 2)], {{type: "application/json"}});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "answer_records.json";
  a.click();
  URL.revokeObjectURL(a.href);
}}

function importRecords(file) {{
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {{
    records = JSON.parse(reader.result);
    saveRecords();
    location.reload();
  }};
  reader.readAsText(file);
}}

function clearRecords() {{
  if (!confirm("確定清空目前瀏覽器內的作答紀錄？")) return;
  records = {{}};
  saveRecords();
  document.querySelectorAll(".question").forEach(resetRow);
}}

function toggleAnswers() {{
  showAnsweredAnswers = !showAnsweredAnswers;
  applyVisibility();
}}

document.querySelectorAll(".question").forEach(tr => {{
  const qid = tr.dataset.qid;
  tr.querySelectorAll(".choice").forEach(td => {{
    td.addEventListener("click", () => markRow(tr, td.dataset.choice));
  }});

  if (records[qid] && records[qid].choice) {{
    markRow(tr, records[qid].choice, false);
  }}
}});

applyVisibility();
updateStatus();
</script>
</body>
</html>
"""

    OUT.write_text(html_text, encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
