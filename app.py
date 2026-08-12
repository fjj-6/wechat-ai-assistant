import streamlit as st
from openai import OpenAI

# 1. 页面配置
st.set_page_config(page_title="AI 微信对话助手", page_icon="💬", layout="centered")

st.markdown("### 💬 微信 AI 智能回复助手")
st.markdown("---")

# 2. 对话人设映射
role_options = {
    "👨‍🏫 导师/长辈 (礼貌、严谨)": "你现在是一名在校大学生。你的回复必须礼貌、谦虚、严谨，多用敬语。重点关注学术、请教问题或汇报进度。",
    "💻 项目团队 (专业、直接)": "你是技术团队的协调人。回复要直接、高效，重点关注任务推进、YOLOv8 模型训练、数据集采集等技术细节。",
    "🍻 朋友/同学 (轻松、随和)": "你现在在和朋友聊天。回复要轻松、口语化、随和，带有幽默感，不要古板。"
}

selected_role_name = st.selectbox("1. 选择当前对话对象：", list(role_options.keys()))
current_system_prompt = role_options[selected_role_name]

# 3. 输入收到的消息
user_message = st.text_area("2. 粘贴对方发来的消息：", placeholder="把对方发的一段话复制粘贴到这里...", height=100)

# 4. API 配置 (可以替换为你自己的 API 密钥与 EndPoint)
API_KEY = "sk-adf01bce95284b18b731069e09ff7dd5"  # 替换为你的 API Key
BASE_URL = "https://api.deepseek.com"  # 替换为你使用的服务商 base_url

# 5. 生成回复逻辑
if st.button("✨ 生成 3 种风格回复", use_container_width=True):
    if not user_message.strip():
        st.warning("请先粘贴对方的消息内容！")
    else:
        with st.spinner("AI 正在思考中..."):
            try:
                # 初始化客户端
                client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

                # 拼接 Prompt 要求模型一次性输出 3 个选项
                full_prompt = f"对方发来的消息是：『{user_message}』\n请根据你的人设，生成 3 种不同切入角度的回复。每种回复占一行，格式为：\n1. [回复内容1]\n2. [回复内容2]\n3. [回复内容3]"

                response = client.chat.completions.create(
                    model="deepseek-chat",  # 或 glm-4 等模型名
                    messages=[
                        {"role": "system", "content": current_system_prompt},
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7
                )

                raw_text = response.choices[0].message.content
                # 简单清洗并按行拆分选项
                replies = [line.strip() for line in raw_text.split("\n") if line.strip()]
                st.session_state["replies"] = replies[:3]  # 取前3条

            except Exception as e:
                st.error(f"调用 API 失败: {e}")

# 6. 渲染生成的选项
if "replies" in st.session_state and st.session_state["replies"]:
    st.markdown("### 3. 选择满意的回复：")
    for i, reply in enumerate(st.session_state["replies"]):
        st.info(reply)
