import streamlit as st
from openai import OpenAI
import os

# --- CÁC HÀM TIỆN ÍCH ---

def rfile(name_file):
    """Hàm đọc nội dung từ file văn bản một cách an toàn."""
    try:
        with open(name_file, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        # st.error(f"Lỗi: Không tìm thấy tệp '{name_file}'.")
        # return None
        # Trong trường hợp đặc biệt này, trả về chuỗi rỗng để tránh lỗi khi strip()
        return ""


# --- CÀI ĐẶT GIAO DIỆN ---

# Cấu hình trang, đặt tiêu đề và layout
st.set_page_config(page_title="Trợ lý AI", layout="wide")

# CSS tùy chỉnh để giao diện to, rõ ràng và sắc nét hơn
st.markdown("""
    <style>
        /* Thay đổi font chữ và kích thước để dễ đọc hơn */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }

        /* Tăng kích thước của bong bóng chat */
        .st-emotion-cache-1c7y2kd {
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        /* Căn giữa logo và làm cho nó nhỏ hơn một chút */
        .st-emotion-cache-1v0mbdj.e115fcil1 {
            display: flex;
            justify-content: center;
        }
        img {
            max-width: 150px;
            border-radius: 8px; /* Bo tròn góc logo */
        }
        
        /* Tùy chỉnh tiêu đề chính */
        h1 {
            font-size: 2rem !important;
            font-weight: 600 !important;
        }
        
        /* Cải thiện ô nhập liệu */
        .st-emotion-cache-sno5eb.effi0qh3 {
            border-radius: 12px;
            padding: 10px 15px;
        }
    </style>
""", unsafe_allow_html=True)


# --- KHỞI TẠO ỨNG DỤNG ---

# Hiển thị logo (nếu có)
if os.path.exists("logo.png"):
    st.image("logo.png")

# Hiển thị tiêu đề
title_content = rfile("00.xinchao.txt")
if title_content:
    st.markdown(f"<h1 style='text-align: center;'>{title_content}</h1>", unsafe_allow_html=True)

# Lấy OpenAI API key từ st.secrets một cách an toàn
openai_api_key = st.secrets.get("OPENAI_API_KEY")

# Kiểm tra nếu API key không tồn tại
if not openai_api_key:
    st.error("Vui lòng cung cấp OpenAI API Key trong phần secrets của Streamlit.")
    st.stop() # Dừng ứng dụng nếu không có key

# Khởi tạo OpenAI client
client = OpenAI(api_key=openai_api_key)

# --- QUẢN LÝ TRẠNG THÁI CHAT ---

# Khởi tạo tin nhắn hệ thống và trợ lý ban đầu
# Điều này giúp định hướng cho mô hình AI
INITIAL_SYSTEM_MESSAGE = {"role": "system", "content": rfile("01.system_trainning.txt")}
INITIAL_ASSISTANT_MESSAGE = {"role": "assistant", "content": rfile("02.assistant.txt")}

# Khởi tạo session state để lưu trữ lịch sử cuộc trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = []
    if INITIAL_SYSTEM_MESSAGE["content"]: # Chỉ thêm nếu có nội dung
        st.session_state.messages.append(INITIAL_SYSTEM_MESSAGE)
    if INITIAL_ASSISTANT_MESSAGE["content"]: # Chỉ thêm nếu có nội dung
        st.session_state.messages.append(INITIAL_ASSISTANT_MESSAGE)

# --- HIỂN THỊ LỊCH SỬ CHAT ---

# Sử dụng st.chat_message để hiển thị lịch sử tin nhắn một cách chuyên nghiệp
# Vòng lặp này sẽ hiển thị tất cả các tin nhắn đã lưu
for message in st.session_state.messages:
    # Bỏ qua tin nhắn hệ thống, không hiển thị cho người dùng
    if message["role"] != "system":
        # 'with' statement giúp tự động định dạng tin nhắn của user và assistant
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- XỬ LÝ NHẬP LIỆU CỦA NGƯỜI DÙNG ---

# Lấy model name từ file
MODEL_NAME = rfile("module_chatgpt.txt").strip()
if not MODEL_NAME:
    st.warning("Chưa cấu hình model ChatGPT. Vui lòng kiểm tra tệp 'module_chatgpt.txt'.")
    st.stop()

# Tạo ô nhập liệu chat ở cuối trang
if prompt := st.chat_input("Bạn muốn hỏi gì?"):
    # Thêm tin nhắn của người dùng vào lịch sử và hiển thị ngay lập tức
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Hiển thị tin nhắn của trợ lý và tạo hiệu ứng streaming
    with st.chat_message("assistant"):
        try:
            # Tạo stream phản hồi từ API OpenAI
            stream = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            # st.write_stream tự động hiển thị từng phần của phản hồi
            # và trả về toàn bộ nội dung khi hoàn tất
            response = st.write_stream(stream)
            # Thêm phản hồi hoàn chỉnh của trợ lý vào lịch sử
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi kết nối tới OpenAI: {e}")

