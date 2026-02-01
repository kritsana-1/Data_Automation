import streamlit as st
import pandas as pd
import plotly.express as px
import requests

def send_line_notify(message, token):
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    data = {
        'message': message
    }
    response = requests.post(url, headers=headers, data=data)
    return response

st.set_page_config(page_title="Data Insights Dashboard", layout="wide")

st.title("Automated Data Insights Dashboard")
st.subheader("อัปโหลดไฟล์ของคุณเพื่อสรุปข้อมูลอัตโนมัติ")

# ส่วนอัปโหลดไฟล์
uploaded_file = st.file_uploader("เลือกไฟล์ CSV หรือ Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    # อ่านข้อมูล
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
        
    st.success("โหลดข้อมูลสำเร็จ!")
    # แสดงข้อมูล 5 แถวแรก
    st.write("### ตัวอย่างข้อมูล:", df.head())
    # แสดงสถิติพื้นฐาน
    st.write("### สรุปสถิติเบื้องต้น:", df.describe())
    # การวิเคราะห์และกราฟสรุปผล
    st.divider()
    st.header("การวิเคราะห์และกราฟสรุปผล")
    
    line_token = st.text_input("กรุณาใส่ Line Notify Token ของคุณ (ถ้ามี)", type="password")
    
    # เลือกคอลัมน์ที่ต้องการทำกราฟ (คิวสามารถเลือกเองได้บนหน้าเว็บ)
    columns = df.columns.tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_axis = st.selectbox("เลือกข้อมูลแนวแกน X", columns)
    with col2:
        y_axis = st.selectbox("เลือกข้อมูลแนวแกน Y (ตัวเลข)", columns)

    if st.button("วิเคราะห์ข้อมูล"):
        total_val = df[y_axis].sum()
        summary_msg = f"\n รายงานด่วนจาก Dashboard\n"
        summary_msg += f"หัวข้อ: {y_axis}\n"
        summary_msg += f"ยอดรวม: {total_val:,.2f}\n"
        
        status = send_line_notify(summary_msg, line_token)
        
        if status == 200:
            st.success("ส่งข้อความไปยัง Line Notify สำเร็จ!")
        else:
            st.error("การส่งข้อความล้มเหลว กรุณาตรวจสอบ Token ของคุณ")
    else:
        st.warning("กรุณากรอก Token ก่อนส่งข้อความ")

    # สร้างกราฟแท่งแบบ Interactive (เอาเมาส์ชี้แล้วเห็นเลข)
    fig = px.bar(df, x=x_axis, y=y_axis, title=f"กราฟสรุประหว่าง {x_axis} และ {y_axis}",
                 color=y_axis, color_continuous_scale='Icefire') # ใช้สีโทนเย็นตามที่คิวชอบ
    st.plotly_chart(fig, use_container_width=True)

    #การแจ้งเตือน 
    st.divider()
    st.header("ระบบแจ้งเตือนอัตโนมัติ")
    
    numeric_values = pd.to_numeric(df[y_axis], errors='coerce') # แปลงเป็นตัวเลข
    total_val = numeric_values.sum()
    if pd.isna(total_val):
        st.error(f"คอลัมน์ {y_axis} ไม่ใช่ตัวเลข ไม่สามารถคำนวณยอดรวมได้ครับ")
    else:
        st.metric(label=f"ยอดรวมของ {y_axis} ทั้งหมด", value=f"{float(total_val):,.2f}")

    if st.button("ยืนยันการส่งรายงาน"):
        if line_token:
            # สร้างข้อความสรุป
            summary_msg = f"\n รายงานด่วนจาก Dashboard\n"
            summary_msg += f"หัวข้อ: {y_axis}\n"
            summary_msg += f"ยอดรวมสะสม: {total_val:,.2f}"
            
            status = send_line_notify(summary_msg, line_token)
            
            if status == 200:
                st.success("ส่งข้อความเข้า Line เรียบร้อยแล้ว!")
            else:
                st.error("เกิดข้อผิดพลาดในการส่ง กรุณาเช็ค Token อีกครั้ง")
        else:
            st.warning("กรุณากรอก Token ก่อนกดส่งครับ")