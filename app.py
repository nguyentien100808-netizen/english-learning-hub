import streamlit as st
import google.generativeai as genai
import json

# Cấu hình trang Streamlit
st.set_page_config(page_title="AI Writing Mentor", page_icon="📝", layout="wide")

st.title("📝 AI Writing Mentor - Trợ lý Luyện Viết Smart")
st.caption("Công cụ phân tích, sửa lỗi và tối ưu hóa bài viết ngoại ngữ của bạn bằng AI.")

# Sidebar: Nhập API Key và tùy chọn
with st.sidebar:
    st.header("⚙️ Cấu hình")
    api_key = st.text_input("Nhập Gemini API Key:", type="password")
    
    style_target = st.selectbox(
        "Mục tiêu văn phong:",
        ["IELTS Writing Task 2", "Business Email", "Academic Essay", "Casual Conversation"]
    )
    
    target_level = st.select_slider(
        "Trình độ mục tiêu:",
        options=["B1 (Intermediate)", "B2 (Upper-Intermediate)", "C1 (Advanced)"]
    )

# Khung nhập liệu chính
user_text = st.text_area("Nhập đoạn văn bản bạn muốn kiểm tra:", height=200, placeholder="Dán đoạn văn tiếng Anh vào đây...")

if st.button("🚀 Phân tích & Sửa bài", type="primary"):
    if not api_key:
        st.error("Vui lòng nhập Gemini API Key ở thanh bên trái!")
    elif not user_text.strip():
        st.warning("Vui lòng nhập đoạn văn cần kiểm tra.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.5-flash-lite')

            # Prompt tối ưu hóa dữ liệu đầu ra dưới dạng JSON
            prompt = f"""
            You are an expert English Writing Mentor. Analyze the following user text.
            Target Style: {style_target}
            Target Level: {target_level}

            User Text: "{user_text}"

            Provide your output in strictly valid JSON format with the following structure:
            {{
                "corrected_text": "The fully corrected and improved version of the text",
                "overall_feedback": "Short summary of strengths and weaknesses",
                "corrections": [
                    {{
                        "original": "incorrect or weak phrase",
                        "correction": "improved phrase",
                        "type": "Grammar / Vocabulary / Style / Collocation",
                        "explanation": "Clear explanation in Vietnamese why this change was made"
                    }}
                ],
                "advanced_rephrasing": [
                    "Option 1 for a more natural/advanced tone",
                    "Option 2 for a more natural/advanced tone"
                ],
                "vocabulary_bank": [
                    {{
                        "word": "advanced word/phrase used",
                        "ipa": "/phonetics/",
                        "meaning_vi": "Nghĩa tiếng Việt",
                        "example": "Example sentence"
                    }}
                ]
            }}
            Return ONLY the JSON object, without markdown formatting like ```json.
            """

            with st.spinner("AI đang phân tích bài viết của bạn..."):
                response = model.generate_content(prompt)
                clean_json_str = response.text.strip().removeprefix("```json").removesuffix("```").strip()
                data = json.loads(clean_json_str)

            st.success("Phân tích hoàn tất!")

            # Hiển thị kết quả
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📌 Văn bản gốc")
                st.info(user_text)

            with col2:
                st.subheader("✨ Văn bản đã sửa & tối ưu")
                st.success(data.get("corrected_text", ""))

            st.markdown("---")
            st.subheader("💡 Nhận xét tổng quan")
            st.write(data.get("overall_feedback", ""))

            # Bảng chi tiết lỗi sai
            st.subheader("🔍 Chi tiết lỗi & Gợi ý chỉnh sửa")
            for item in data.get("corrections", []):
                with st.expander(f"❌ {item['original']}  ➡️  ✅ {item['correction']} ({item['type']})"):
                    st.write(f"**Giải thích:** {item['explanation']}")

            # Gợi ý cách viết nâng cao
            st.subheader("🚀 Gợi ý viết lại nâng cao (Advanced Rephrasing)")
            for i, opt in enumerate(data.get("advanced_rephrasing", []), 1):
                st.markdown(f"**Cách {i}:** {opt}")

            # Từ vựng cần học
            st.subheader("📚 Từ vựng & Cấu trúc hay")
            vocab_list = data.get("vocabulary_bank", [])
            if vocab_list:
                st.table(vocab_list)

        except Exception as e:
            st.error(f"Có lỗi xảy ra: {str(e)}")