import streamlit as st
import requests
from datetime import timedelta
import threading
import time

# URL ของ ESP32
st.title("ควบคุมไฟด้วย ESP32")

# ฟังก์ชันเพื่อให้แน่ใจว่า URL มี "http://" อยู่แล้ว
def format_url(ip):
    return f"http://{ip}" if not ip.startswith("http://") else ip

# ฟังก์ชันส่งคำสั่งเปิดไฟ
def turn_on_light():
    try:
        requests.get(f"{esp_url}/on")
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาดในการเปิดไฟ: {e}")

# ฟังก์ชันส่งคำสั่งปิดไฟ
def turn_off_light():
    try:
        requests.get(f"{esp_url}/off")
    except requests.exceptions.RequestException as e:
        st.error(f"เกิดข้อผิดพลาดในการปิดไฟ: {e}")

# ฟังก์ชันสำหรับการตั้งเวลาและเริ่มการนับถอยหลัง
def schedule_lights(on_duration, off_duration):
    while True:
        turn_on_light()
        time.sleep(on_duration.total_seconds())
        turn_off_light()
        time.sleep(off_duration.total_seconds())

raw_ip = st.text_input("กรอก IP ของ ESP32", "192.168.176.25")
esp_url = format_url(raw_ip)
st.markdown('<h2 style="font-size:40px;">LED Light</h2>', unsafe_allow_html=True)

mode = st.radio("เลือกโหมด", ("โหมดปกติ", "โหมดออโต้"))

if mode == "โหมดปกติ":
    col1, col2 = st.columns([0.1, 1])

    with col1:
        if st.button("ON"):
            turn_on_light()

    with col2:
        if st.button("OFF"):
            turn_off_light()

elif mode == "โหมดออโต้":
    st.subheader("ตั้งเวลาเปิด/ปิดไฟ")

    on_hours = st.number_input("ระยะเวลาเปิดไฟ (ชั่วโมง)", min_value=0, value=0, step=1)
    on_minutes = st.number_input("ระยะเวลาเปิดไฟ (นาที)", min_value=0, value=0, step=1)
    off_hours = st.number_input("ระยะเวลาปิดไฟ (ชั่วโมง)", min_value=0, value=0, step=1)
    off_minutes = st.number_input("ระยะเวลาปิดไฟ (นาที)", min_value=0, value=0, step=1)

    on_duration = timedelta(hours=on_hours, minutes=on_minutes)
    off_duration = timedelta(hours=off_hours, minutes=off_minutes)

    if on_duration.total_seconds() > 0 and off_duration.total_seconds() > 0:
        if st.button("เริ่มโหมดออโต้"):
            if "auto_thread" in st.session_state and st.session_state.auto_thread.is_alive():
                st.error("เธรดโหมดออโต้กำลังทำงานอยู่แล้ว")
            else:
                st.session_state.auto_thread = threading.Thread(target=schedule_lights, args=(on_duration, off_duration), daemon=True)
                st.session_state.auto_thread.start()
    else:
        st.warning("กรุณากรอกระยะเวลาเปิดและปิดไฟให้ครบถ้วน")
