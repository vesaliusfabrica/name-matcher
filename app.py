import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from name_matcher import NameMatcher

st.set_page_config(
    page_title="Name Matcher",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 English Name Matcher")
st.caption("Double Metaphone  ·  Monge-Elkan  ·  Jaro-Winkler")

# --- Session state ---
if "registry" not in st.session_state:
    st.session_state.registry = [
        "John Smith",
        "Jon Smyth",
        "Jane Smith",
        "Robert Johnson",
        "Roberto Johnson",
        "Michael Brown",
        "Elizabeth Davis",
        "Smith John",
    ]

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
            st.success(f"{len(names)} 件のデータをインポートしました")
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
        st.success(f"{len(updated)} 件を登録しました")

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

            rows = [{"氏名": r.name, "スコア": round(r.score, 4)} for r in results]
            df_result = pd.DataFrame(rows)

            st.dataframe(
                df_result,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "スコア": st.column_config.ProgressColumn(
                        "スコア",
                        min_value=0.0,
                        max_value=1.0,
                        format="%.4f",
                    )
                },
            )

            st.caption(
                f"フォネティックスクリーニング後の候補数: "
                f"{'≥ ' if len(results) == top_k else ''}{len(results)} 件"
            )
else:
    st.info("上のテキストボックスに照合したい氏名を入力してください。")
