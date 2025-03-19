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
            "학생": ["김성호", "학생 B", "학생 C", "학생 D"],
            "세진코인": [5, 5, 5, 5],
            "기록": ["[]", "[]", "[]", "[]"]
        })
        data.to_csv(students_file, index=False)
        return data

# CSV 파일 저장 함수 (학생 데이터)
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

student_pw = st.text_input("학생 개인 비밀번호를 입력하세요:", type="password")

# 학생 비밀번호 인증 및 로또 게임 진행
if student_pw:
    if selected_student in student_passwords and student_pw == student_passwords[selected_student]:
        st.success("학생 인증 성공!")
        
        # 로또 게임: 학생이 1부터 20까지 숫자 중 3개 선택
        st.write("1부터 20까지의 숫자 중 **정확히 3개**를 선택하세요:")
        chosen_numbers = st.multiselect("숫자 선택", list(range(1, 21)))
        if len(chosen_numbers) != 3:
            st.warning("정확히 3개의 숫자를 선택해야 합니다.")
        else:
            if st.button("로또 게임 시작 (1코인 차감)"):
                current_coins = int(students_data.at[student_index, "세진코인"])
                if current_coins < 1:
                    st.error("세진코인이 부족합니다.")
                else:
                    # 1코인 차감
                    students_data.at[student_index, "세진코인"] = current_coins - 1
                    
                    # 컴퓨터가 1부터 20까지 중, 중복 없이 3개의 메인 볼과 1개의 보너스 볼 추첨
                    pool = list(range(1, 21))
                    main_balls = random.sample(pool, 3)
                    remaining = [n for n in pool if n not in main_balls]
                    bonus_ball = random.choice(remaining)
                    
                    st.write("**컴퓨터 추첨 결과:**")
                    st.write("메인 볼:", sorted(main_balls))
                    st.write("보너스 볼:", bonus_ball)
                    
                    # 학생이 선택한 숫자와 메인 볼 비교
                    matches = set(chosen_numbers) & set(main_balls)
                    match_count = len(matches)
                    
                    if match_count == 3:
                        st.success("축하합니다! 1등 당첨! 상품: 치킨")
                        result = "1등"
                        reward = "치킨"
                    elif match_count == 2:
                        non_match = list(set(chosen_numbers) - matches)[0]
                        if non_match == bonus_ball:
                            st.success("축하합니다! 2등 당첨! 상품: 햄버거세트")
                            result = "2등"
                            reward = "햄버거세트"
                        else:
                            st.success("축하합니다! 3등 당첨! 상품: 매점이용권")
                            result = "3등"
                            reward = "매점이용권"
                    elif match_count == 1:
                        st.success("축하합니다! 4등 당첨! 보상: 0.5코인")
                        result = "4등"
                        reward = "0.5코인"
                        # 0.5코인 보상
                        students_data.at[student_index, "세진코인"] += 0.5
                    else:
                        st.error("아쉽게도 당첨되지 않았습니다.")
                        result = "낙첨"
                        reward = ""
                    
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_record = {
                        "반": selected_class,
                        "학생": selected_student,
                        "게임유형": "로또",
                        "결과": result,
                        "상품/코인획득": reward,
                        "코인차감": 1,
                        "시간": now
                    }
                    # pd.concat를 사용해 새 레코드 추가 (pandas 2.0 이상 호환)
                    lottery_data = pd.concat([lottery_data, pd.DataFrame([new_record])], ignore_index=True)
                    save_students_data(students_data)
                    save_lottery_record(lottery_data)
                    
                    st.write("현재 잔액:", students_data.at[student_index, "세진코인"])
    else:
        st.error("학생 비밀번호가 올바르지 않습니다.")
else:
    st.info("학생 개인 비밀번호를 입력하세요.")

# 관리자 모드: 전체 로또 기록 확인
admin_pw = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
if admin_pw == ADMIN_PASSWORD:
    st.subheader("전체 로또 기록")
    st.dataframe(lottery_data)
