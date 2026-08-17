import os

import streamlit as st
from openai import OpenAI


st.set_page_config(page_title="AI 微信对话助手", page_icon="💬", layout="centered")

ROLE_OPTIONS = {
    "👨‍🏫 导师/长辈（礼貌、严谨）": "你是一名在校大学生。回复必须礼貌、谦虚、严谨，适度使用敬语，重点关注请教、汇报与学术沟通。",
    "💻 项目团队（专业、直接）": "你是技术团队的协调人。回复直接、高效，重点清晰说明任务、进度、风险和下一步。",
    "🍻 朋友/同学（轻松、随和）": "你正在和朋友聊天。回复轻松、自然、口语化，可带一点恰当的幽默感。",
}

POLISH_STYLES = {
    "专业得体": "表达专业、清晰、有分寸，适合工作或正式沟通。",
    "亲切自然": "表达亲切、自然、真诚，避免生硬和过度客套。",
    "简洁直接": "保留关键信息，尽量简洁，适合即时消息。",
    "礼貌委婉": "表达礼貌、委婉，适合请求、提醒或拒绝。",
}


def get_client() -> tuple[OpenAI | None, str | None, str]:
    """Read credentials from Streamlit Secrets first, then environment variables."""
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    base_url = st.secrets.get("OPENAI_BASE_URL", os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com"))
    model = st.secrets.get("OPENAI_MODEL", os.getenv("OPENAI_MODEL", "deepseek-chat"))
    if not api_key:
        return None, "尚未配置 API 密钥。请在 Streamlit Cloud 的 Secrets 中填写 OPENAI_API_KEY。", model
    return OpenAI(api_key=api_key, base_url=base_url), None, model


def generate(system_prompt: str, user_prompt: str) -> str:
    client, error, model = get_client()
    if error:
        raise RuntimeError(error)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content or "未生成内容，请重试。"


st.title("💬 微信 AI 智能回复助手")
reply_tab, polish_tab = st.tabs(["智能回复", "话术润色"])

with reply_tab:
    st.caption("根据对话对象生成 3 种可直接发送的回复。")
    role_name = st.selectbox("选择当前对话对象", list(ROLE_OPTIONS))
    received_message = st.text_area("粘贴对方发来的消息", height=130, placeholder="把对方发来的一段话粘贴到这里…")
    if st.button("✨ 生成 3 种回复", use_container_width=True, key="reply"):
        if not received_message.strip():
            st.warning("请先粘贴对方的消息内容。")
        else:
            try:
                with st.spinner("AI 正在组织回复…"):
                    answer = generate(
                        ROLE_OPTIONS[role_name],
                        f"对方发来的消息是：『{received_message}』\n"
                        "请生成 3 种不同切入角度的中文回复。每条单独一行，并以 1.、2.、3. 开头。",
                    )
                st.session_state["reply_result"] = answer
            except Exception as exc:
                st.error(f"生成失败：{exc}")
    if result := st.session_state.get("reply_result"):
        st.subheader("可选回复")
        st.code(result, language=None)

with polish_tab:
    st.caption("把你想说的话改得更自然、更清楚、更符合场景。")
    polish_style = st.selectbox("润色风格", list(POLISH_STYLES), key="polish_style")
    original_text = st.text_area("输入你想说的话", height=150, placeholder="例如：老师我论文还没写完，能不能晚两天交？", key="original_text")
    if st.button("✍️ 润色这段话", use_container_width=True, key="polish"):
        if not original_text.strip():
            st.warning("请先输入需要润色的话。")
        else:
            try:
                with st.spinner("AI 正在润色…"):
                    polished = generate(
                        "你是一名中文沟通编辑。" + POLISH_STYLES[polish_style],
                        f"请润色下面这段话。只输出润色后的文本，不要解释，不要添加引号：\n{original_text}",
                    )
                st.session_state["polish_result"] = polished
            except Exception as exc:
                st.error(f"润色失败：{exc}")
    if result := st.session_state.get("polish_result"):
        st.subheader("润色结果")
        st.code(result, language=None)

st.divider()
st.caption("提示：请勿把 API 密钥写入代码或提交到 GitHub；请使用 Streamlit Secrets。")
