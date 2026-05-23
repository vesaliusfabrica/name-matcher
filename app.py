import streamlit as st
import pandas as pd
import pathlib
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from name_matcher import NameMatcher

# ── Persistence ───────────────────────────────────────────────────────────────
_DATA_FILE = pathlib.Path(__file__).parent / "data" / "registry.txt"

_DEFAULT_REGISTRY = [
    "John Smith", "Jon Smyth", "Jane Smith",
    "Robert Johnson", "Roberto Johnson",
    "Michael Brown", "Elizabeth Davis", "Smith John",
]

def _load_registry() -> list[str]:
    if _DATA_FILE.exists():
        names = [l.strip() for l in _DATA_FILE.read_text(encoding="utf-8").splitlines() if l.strip()]
        if names:
            return names
    return _DEFAULT_REGISTRY

def _save_registry(names: list[str]) -> None:
    _DATA_FILE.parent.mkdir(exist_ok=True)
    _DATA_FILE.write_text("\n".join(names), encoding="utf-8")

def _score_color(score: float) -> tuple[str, str, str]:
    """Return (hex_color, bg_color, label) based on score."""
    if score >= 0.95:
        return "#1a7f4b", "#d4f5e2", "高"
    if score >= 0.85:
        return "#b06800", "#fff3cd", "中"
    return "#c0392b", "#fde8e8", "要確認"


def _render_results(results) -> None:
    cards = []
    for r in results:
        color, bg, label = _score_color(r.score)
        pct = r.score * 100
        cards.append(f"""
<div style="
    background:{bg};
    border-left:5px solid {color};
    border-radius:8px;
    padding:14px 18px;
    margin-bottom:10px;
">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="font-size:1.05rem; font-weight:600; color:#222;">{r.name}</span>
    <span style="
        font-size:2rem;
        font-weight:800;
        color:{color};
        letter-spacing:-0.5px;
        line-height:1;
    ">{r.score:.4f}</span>
  </div>
  <div style="display:flex; align-items:center; gap:10px; margin-top:10px;">
    <div style="flex:1; background:#ddd; border-radius:6px; height:14px; overflow:hidden;">
      <div style="
          width:{pct:.1f}%;
          background:{color};
          height:100%;
          border-radius:6px;
      "></div>
    </div>
    <span style="
        font-size:0.8rem;
        font-weight:700;
        color:{color};
        min-width:3em;
        text-align:right;
    ">{label}</span>
  </div>
</div>""")
    st.markdown("\n".join(cards), unsafe_allow_html=True)


st.set_page_config(
    page_title="Name Matcher",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 English Name Matcher")
st.caption("Double Metaphone  ·  Monge-Elkan  ·  Jaro-Winkler")

# --- Session state ---
if "registry" not in st.session_state:
    st.session_state.registry = _load_registry()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Name Registry")

    uploaded = st.file_uploader(
        "Import CSV",
        type=["csv"],
        help="1列目 or 'name' 列に氏名が入った CSV を読み込む",
    )
    if uploaded:
        try:
            df = pd.read_csv(uploaded)
            col = "name" if "name" in df.columns else df.columns[0]
            names = df[col].dropna().astype(str).tolist()
            st.session_state.registry = names
            _save_registry(names)
            st.success(f"{len(names)} 件のデータをインポートしました（保存済み）")
        except Exception as exc:
            st.error(f"CSV の読み込みに失敗しました: {exc}")

    st.divider()

    registry_text = st.text_area(
        "レジストリを編集（1行1名）",
        value="\n".join(st.session_state.registry),
        height=220,
    )
    if st.button("変更を適用", use_container_width=True):
        updated = [n.strip() for n in registry_text.splitlines() if n.strip()]
        st.session_state.registry = updated
        _save_registry(updated)
        st.success(f"{len(updated)} 件を登録しました（保存済み）")

    st.metric("登録件数", len(st.session_state.registry))

# ── Main ─────────────────────────────────────────────────────────────────────
left, right = st.columns([3, 1])
with left:
    query = st.text_input("照合する氏名", placeholder="例: Jon Smythe")
with right:
    top_k = st.number_input("表示件数 (Top K)", min_value=1, max_value=50, value=5)

min_score = st.slider(
    "スコア閾値 (min_score)",
    min_value=0.0,
    max_value=1.0,
    value=0.75,
    step=0.01,
    format="%.2f",
    help="このスコア未満の候補は表示しません（0.75: 広めスクリーニング / 0.85: 精度重視）",
)

st.divider()

if query:
    if not st.session_state.registry:
        st.warning("レジストリが空です。サイドバーから名前を追加してください。")
    else:
        matcher = NameMatcher(st.session_state.registry)
        results = matcher.find_matches(query, top_k=top_k, min_score=min_score)

        if not results:
            st.info("閾値以上の候補が見つかりませんでした。スコア閾値を下げてみてください。")
        else:
            st.subheader(f"「{query}」の照合結果")
            _render_results(results)
            st.caption(
                f"フォネティックスクリーニング後の候補数: "
                f"{'≥ ' if len(results) == top_k else ''}{len(results)} 件"
            )
else:
    st.info("上のテキストボックスに照合したい氏名を入力してください。")
