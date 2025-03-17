import streamlit as st
import pandas as pd
import os
import ast
import random
import time
from datetime import datetime

# -----------------------------
# 기본 데이터 파일 경로 설정
students_file = "students_points.csv"
lottery_file = "lottery_records.csv"

# -----------------------------
# 학생 개인 비밀번호 (예시)
student_passwords = {
    "김성호": "tjdgh",
    "학생 B": "passwordB",
    "학생 C": "passwordC",
    "학생 D": "passwordD",
}

# 관리자 비밀번호 (관리자 기록 확인용)
ADMIN_PASSWORD = "wjddusdlcjswo"

# -----------------------------
# CSV 파일 로드 함수 (학생 데이터)
def load_students_data():
    if os.path.exists(students_file):
        return pd.read_csv(students_file)
    else:
        data = pd.DataFrame({
            "반": ["1반", "1반", "2반", "2반"],
            "학생": ["학생 A", "학생 B", "학생 C", "학생 D"],
            "세진코인": [5, 5, 5, 5],  # 초기 코인 수치는 예시로 5코인씩 부여
            "기록": ["[]", "[]", "[]", "[]"]
        })
        data.to_csv(students_file, index=False)
        return data

# CSV 저장 함수 (학생 데이터)
def save_students_data(data):
    try:
        data.to_csv(students_file, index=False)
    except Exception as e:
        st.error(f"데이터 저장 오류: {e}")

# -----------------------------
# 로또 기록 파일 로드/생성 함수
def load_lottery_records():
    if os.path.exists(lottery_file):
        return pd.read_csv(lottery_file)
    else:
        cols = ["반", "학생", "게임유형", "결과", "상품/코인획득", "코인차감", "시간"]
        data = pd.DataFrame(columns=cols)
        data.to_csv(lottery_file, index=False)
        return data

def save_lottery_record(record_df):
    try:
        record_df.to_csv(lottery_file, index=False)
    except Exception as e:
        st.error(f"로또 기록 저장 오류: {e}")

# -----------------------------
# 데이터 로드
students_data = load_students_data()
lottery_data = load_lottery_records()

# -----------------------------
# 페이지 타이틀
st.markdown("<h1 style='text-align:center; color:#ffffff; font-weight:bold;'>세진코인 로또 게임</h1>", unsafe_allow_html=True)

# -----------------------------
# 학생 로그인 (반, 학생 선택 및 개인 비밀번호)
selected_class = st.selectbox("반을 선택하세요:", students_data["반"].unique())
filtered_students = students_data[students_data["반"] == selected_class]
selected_student = st.selectbox("학생을 선택하세요:", filtered_students["학생"].tolist())
student_index = students_data[(students_data["반"] == selected_class) & (students_data["학생"] == selected_student)].index[0]

student_pw = st.text_input("학생 개인 
