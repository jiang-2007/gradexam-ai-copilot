"""Streamlit Web UI"""
import streamlit as st
import requests
import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="考研AIGC助手", page_icon="📚", layout="wide")

st.title("📚 考研AIGC助手")
st.caption("RAG问答 · 作文批改 · 复习规划 · 闪卡生成 · 全网情报")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 知识库问答", "✍️ 作文批改", "📅 复习规划", "🃏 闪卡生成", "🕵️ 全网情报"])

# ====== Tab1: RAG 问答 ======
with tab1:
    st.subheader("知识库问答")
    uploaded = st.file_uploader("上传考研资料（PDF/TXT）", type=["pdf", "txt", "md"])
    if uploaded and st.button("导入知识库"):
        with st.spinner("正在处理文档..."):
            files = {"file": (uploaded.name, uploaded.getvalue())}
            r = requests.post(f"{API_BASE}/api/upload", files=files)
            if r.status_code == 200:
                st.success(f"导入成功，新增 {r.json()['chunks_added']} 个知识片段")
            else:
                st.error("导入失败")

    question = st.text_input("输入你的问题：")
    if st.button("提问", key="qa_btn") and question:
        with st.spinner("思考中..."):
            r = requests.post(f"{API_BASE}/api/qa", json={"question": question})
            if r.status_code == 200:
                data = r.json()
                st.markdown(data["answer"])
                if data.get("sources"):
                    st.caption("参考来源：" + " | ".join(data["sources"]))

# ====== Tab2: 作文批改 ======
with tab2:
    st.subheader("作文批改")
    subj = st.radio("科目", ["英语作文", "政治论述题"])
    topic = st.text_input("题目：")
    essay = st.text_area("你的作答：", height=200)
    if st.button("开始批改", key="essay_btn") and topic and essay:
        with st.spinner("批改中..."):
            subject = "politics" if "政治" in subj else "english"
            r = requests.post(f"{API_BASE}/api/essay/grade",
                              json={"topic": topic, "essay": essay, "subject": subject})
            if r.status_code == 200:
                st.markdown(r.json()["result"])

# ====== Tab3: 复习规划 ======
with tab3:
    st.subheader("复习计划 & 择校")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 生成复习计划")
        school = st.text_input("目标院校：", "复旦大学")
        major = st.text_input("目标专业：", "应用心理（347）")
        found = st.selectbox("当前基础", ["零基础", "一般", "较好"])
        months = st.number_input("剩余月数", 1, 24, 12)
        hours = st.number_input("每日学习时长", 1.0, 16.0, 8.0)
        if st.button("生成计划"):
            with st.spinner("规划中..."):
                r = requests.post(f"{API_BASE}/api/planner/plan", json={
                    "target_school": school, "target_major": major,
                    "foundation": found, "months_left": months, "daily_hours": hours,
                })
                if r.status_code == 200:
                    st.markdown(r.json()["plan"])

    with col2:
        st.markdown("### 智能择校")
        bg = st.text_input("本科层次：", "双非一本")
        score = st.text_input("估分：", "360-380")
        loc = st.text_input("地域偏好：", "上海/江浙")
        deg = st.selectbox("学位类型", ["学硕", "专硕"])
        if st.button("推荐院校"):
            with st.spinner("分析中..."):
                r = requests.post(f"{API_BASE}/api/planner/schools", json={
                    "bg": bg, "major": major, "score": score,
                    "location": loc, "degree_type": deg,
                })
                if r.status_code == 200:
                    st.markdown(r.json()["recommendation"])

# ====== Tab4: 闪卡生成 ======
with tab4:
    st.subheader("AI 自动生成背诵闪卡")
    note = st.text_area("粘贴你的笔记内容：", height=200)
    if st.button("生成闪卡", key="fc_btn") and note:
        with st.spinner("拆解知识点..."):
            r = requests.post(f"{API_BASE}/api/flashcard", json={"content": note})
            if r.status_code == 200:
                cards = r.json()["cards"]
                for i, c in enumerate(cards, 1):
                    with st.expander(f"闪卡 {i}：{c.get('front', '')}"):
                        st.write(c.get("back", ""))

# ====== Tab5: 全网情报 ======
with tab5:
    st.subheader("🕵️ 全网考研情报检索")
    st.caption("学费 / 报录比 / 分数线 / 专硕学硕对比 / 一键深度报告（数据来自全网实时检索）")

    col_s, col_m = st.columns(2)
    school = col_s.text_input("院校名称", "复旦大学")
    major = col_m.text_input("专业名称", "应用心理")

    c1, c2, c3, c4 = st.columns(4)
    btn_tuition = c1.button("💰 学费情报")
    btn_ratio = c2.button("📊 报录比/分数线")
    btn_compare = c3.button("⚖️ 专硕vs学硕")
    btn_report = c4.button("📑 一键深度报告")

    if btn_tuition:
        with st.spinner("全网检索学费信息..."):
            r = requests.post(f"{API_BASE}/api/research/tuition", json={"school": school, "major": major})
            if r.status_code == 200:
                st.markdown(r.json()["result"])

    if btn_ratio:
        with st.spinner("全网检索招生数据..."):
            r = requests.post(f"{API_BASE}/api/research/admission", json={"school": school, "major": major})
            if r.status_code == 200:
                st.markdown(r.json()["result"])

    if btn_compare:
        with st.spinner("全网检索专硕学硕政策..."):
            r = requests.post(f"{API_BASE}/api/research/compare", json={"school": school, "major": major})
            if r.status_code == 200:
                st.markdown(r.json()["result"])

    if btn_report:
        with st.spinner("正在生成深度分析报告（约1-2分钟）..."):
            r = requests.post(f"{API_BASE}/api/research/report", json={"school": school, "major": major})
            if r.status_code == 200:
                st.markdown(r.json()["report"])
                st.download_button(
                    "⬇️ 下载报告 (Markdown)",
                    r.json()["report"],
                    file_name=f"{school}_{major}_考研分析报告.md",
                    mime="text/markdown",
                )
