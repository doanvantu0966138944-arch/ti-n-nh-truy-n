import streamlit as st
from openai import OpenAI
import asyncio
import edge_tts
import time
import json
import os

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Tiên Hiệp Creator Pro", layout="wide")

if 'chapters_flow' not in st.session_state:
    st.session_state.chapters_flow = []

DB_FILE = "tang_kinh_cac_v6.json"

# --- 2. CÔNG CỤ HỖ TRỢ ---
def save_to_library(title, content, audio_path=""):
    storage = load_db()
    storage.append({
        "id": time.time(),
        "title": title,
        "date": time.strftime("%d/%m/%Y %H:%M"),
        "content": content,
        "audio": audio_path
    })
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=4)

def delete_from_library(item_id):
    storage = load_db()
    storage = [item for item in storage if item['id'] != item_id]
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(storage, f, ensure_ascii=False, indent=4)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

async def generate_voice(text, filename):
    try:
        communicate = edge_tts.Communicate(text, "vi-VN-NamMinhNeural")
        await communicate.save(filename)
        return filename
    except: return ""

# --- 3. SIDEBAR: TRẮC NGHIỆM BỐI CẢNH ---
with st.sidebar:
    st.header("🔑 Cài Đặt Linh Khí")
    api_key = st.text_input("OpenRouter API Key", type="password")
    
    st.divider()
    st.header("📜 Trắc Nghiệm Bối Cảnh")
    world = st.selectbox("Thế giới", ["Phàm Nhân Giới", "Linh Giới", "Tiên Giới", "Ma Giới", "Bí Cảnh Thượng Cổ", "Yêu Tộc Lĩnh Địa"])
    world_idea = st.text_input("Ý tưởng thế giới riêng")
    era = st.selectbox("Thời đại", ["Hỗn Độn Sơ Khai", "Thái Cổ Thần Chiến", "Viễn Cổ Tiên Pháp", "Mạt Pháp", "Hiện Đại"])
    era_idea = st.text_input("Ý tưởng thời đại riêng")
    linh_can = st.selectbox("Linh căn", ["Thiên Linh Căn", "Biến Dị Linh Căn", "Hỗn Độn Linh Căn", "Kiếm Linh Căn"])
    linh_can_idea = st.text_input("Dị tượng linh căn")
    origin = st.selectbox("Xuất thân", ["Tộc nhân sa sút", "Nô bộc tông môn", "Xuyên không giả", "Trùng sinh lão tổ"])
    origin_idea = st.text_input("Ý tưởng xuất thân riêng")
    job = st.selectbox("Nghề nghiệp", ["Kiếm Tu", "Luyện Đan Sư", "Luyện Khí Sư", "Trận Pháp Sư"])
    job_idea = st.text_input("Ý tưởng nghề nghiệp riêng")
    artifact = st.selectbox("Pháp bảo", ["Trường Kiếm Cổ", "Linh Lung Tháp", "Đan Đỉnh", "Hệ Thống", "Nhẫn"])
    artifact_idea = st.text_input("Ý tưởng pháp bảo riêng")

    st.divider()
    if st.button("🗑️ XÓA BÀN VIẾT (LÀM MỚI)"):
        st.session_state.chapters_flow = []
        st.rerun()

context_str = f"Bối cảnh: {world}({world_idea}), Thời đại: {era}({era_idea}), Linh căn: {linh_can}({linh_can_idea}), Xuất thân: {origin}({origin_idea}), Nghề: {job}({job_idea}), Pháp bảo: {artifact}({artifact_idea})"

# --- 4. GIAO DIỆN CHÍNH ---
st.title("⛩️ SIÊU MÁY CHỦ BIÊN SOẠN")
tab_create, tab_lib = st.tabs(["🚀 Biên Soạn & Nối Chương", "📚 Tàng Kinh Các"])

with tab_create:
    if not st.session_state.chapters_flow:
        user_idea = st.text_area("✍️ Ý tưởng khởi đầu truyện:", placeholder="Nhập ý tưởng để AI bắt đầu viết...")
        if st.button("🚀 KHAI THIÊN LẬP ĐỊA"):
            if not api_key: st.error("Thiếu API Key!")
            else:
                client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                with st.spinner("Đang múa bút chương đầu..."):
                    prompt = f"{context_str}. Viết chương mở đầu truyện tiên hiệp về: {user_idea}. Định dạng: Tên Chương | Nội dung"
                    res = client.chat.completions.create(model="google/gemini-2.0-flash-001", messages=[{"role": "user", "content": prompt}])
                    raw = res.choices[0].message.content.strip()
                    parts = raw.split("|")
                    st.session_state.chapters_flow.append({
                        "title": parts[0].strip() if len(parts) > 0 else "Chương 1",
                        "content": parts[1].strip() if len(parts) > 1 else raw,
                        "audio": ""
                    })
                    st.rerun()

    for idx, ch in enumerate(st.session_state.chapters_flow):
        with st.container(border=True):
            st.subheader(f"📖 {ch['title']}")
            col_tools, col_audio_display = st.columns([1, 2])
            with col_tools:
                t1, t2 = st.columns(2)
                if t1.button(f"🔊 Đọc", key=f"voice_btn_{idx}"):
                    with st.spinner("Đang tạo..."):
                        fname = f"audio_{int(time.time())}_{idx}.mp3"
                        audio_path = asyncio.run(generate_voice(ch['content'], fname))
                        st.session_state.chapters_flow[idx]['audio'] = audio_path
                        st.rerun()
                if t2.button(f"💾 Lưu", key=f"save_btn_{idx}"):
                    save_to_library(ch['title'], ch['content'], ch['audio'])
                    st.success(f"Đã cất {ch['title']} vào Tàng Kinh Các!")
            with col_audio_display:
                if ch['audio']: st.audio(ch['audio'])

            st.markdown(ch['content'])
            
            if idx == len(st.session_state.chapters_flow) - 1:
                st.divider()
                if st.button("✍️ VIẾT TIẾP DIỄN BIẾN CHƯƠNG KẾ", type="primary", use_container_width=True):
                    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                    with st.spinner("AI đang múa bút nối mạch..."):
                        next_prompt = f"{context_str}. Chương trước: '{ch['content']}'. Hãy viết tiếp 1 chương mới hoàn chỉnh. Định dạng: Tên Chương | Nội dung"
                        res = client.chat.completions.create(model="google/gemini-2.0-flash-001", messages=[{"role": "user", "content": next_prompt}])
                        raw_n = res.choices[0].message.content.strip()
                        parts_n = raw_n.split("|")
                        st.session_state.chapters_flow.append({
                            "title": parts_n[0].strip() if len(parts_n) > 0 else f"Chương Tiếp {idx+2}",
                            "content": parts_n[1].strip() if len(parts_n) > 1 else raw_n,
                            "audio": ""
                        })
                        st.rerun()

with tab_lib:
    st.header("📜 Tàng Kinh Các (Danh sách lưu trữ)")
    history = load_db()
    if not history:
        st.info("Chưa có chương nào được lưu.")
    else:
        for item in reversed(history):
            with st.expander(f"📍 {item['date']} - {item['title']}"):
                # Hiển thị Audio ở đầu nếu có
                if item['audio']: 
                    st.audio(item['audio'])
                
                # Nội dung văn bản
                st.markdown(item['content'])
                
                st.divider()
                # TẤT CẢ CÁC NÚT CHỨC NĂNG ĐƯỢC CHUYỂN XUỐNG DƯỚI CÙNG
                c1, c2, c3, c_spacer = st.columns([1, 1, 1, 2])
                
                with c1:
                    if st.button("🔄 Khôi phục", key=f"res_lib_{item['id']}"):
                        st.session_state.chapters_flow = [{"title": item['title'], "content": item['content'], "audio": item['audio']}]
                        st.rerun()
                
                with c2:
                    if st.button("✍️ Viết tiếp", key=f"cont_lib_{item['id']}", type="primary"):
                        if not api_key:
                            st.error("Cần API Key!")
                        else:
                            client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
                            with st.spinner("Đang linh ứng nội dung cũ..."):
                                st.session_state.chapters_flow = [{"title": item['title'], "content": item['content'], "audio": item['audio']}]
                                next_prompt = f"{context_str}. Chương trước: '{item['content']}'. Viết tiếp chương mới. Định dạng: Tên Chương | Nội dung"
                                try:
                                    res = client.chat.completions.create(model="google/gemini-2.0-flash-001", messages=[{"role": "user", "content": next_prompt}])
                                    raw_n = res.choices[0].message.content.strip()
                                    parts_n = raw_n.split("|")
                                    st.session_state.chapters_flow.append({
                                        "title": parts_n[0].strip() if len(parts_n) > 0 else "Chương Tiếp",
                                        "content": parts_n[1].strip() if len(parts_n) > 1 else raw_n,
                                        "audio": ""
                                    })
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Lỗi: {e}")
                
                with c3:
                    # NÚT XÓA: Loại bỏ chương khỏi file JSON
                    if st.button("🗑️ Xóa", key=f"del_lib_{item['id']}"):
                        delete_from_library(item['id'])
                        st.rerun()