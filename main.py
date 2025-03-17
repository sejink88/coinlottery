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

student_pw = st.text_input("학생 개인 비밀번호를 입력하세요:", type="password")

# -----------------------------
# 로또 게임 함수 (선택한 숫자와 추가 게임 여부 인자로 받음)
def play_lottery(chosen_numbers, is_free=False):
    global students_data, lottery_data
    coin_balance = int(students_data.at[student_index, "세진코인"])
    if not is_free:
        if coin_balance < 1:
            st.error("세진코인이 부족합니다. 게임에 참여할 수 없습니다.")
            return None
        # 1코인 차감
        students_data.at[student_index, "세진코인"] = coin_balance - 1
        cost = 1
    else:
        cost = 0

    st.write("**숫자 선택 후, 컴퓨터가 공을 뽑습니다...**")
    time.sleep(0.5)
    
    # 1부터 20까지 중, 컴퓨터가 중복 없이 3개의 메인공과 보너스공 1개 추첨
    pool = list(range(1, 21))
    main_balls = random.sample(pool, 3)
    remaining_pool = [num for num in pool if num not in main_balls]
    bonus_ball = random.choice(remaining_pool)
    
    st.write(f"**메인 공:** {sorted(main_balls)}")
    st.write(f"**보너스 공:** {bonus_ball}")
    st.write(f"**학생이 선택한 숫자:** {sorted(chosen_numbers)}")
    
    # 메인 공과 비교하여 일치하는 숫자 개수 계산
    matches = set(chosen_numbers) & set(main_balls)
    match_count = len(matches)
    
    outcome = ""
    reward_text = ""
    game_type = "일반"
    
    # 룰에 따른 판정
    if match_count == 3:
        outcome = "1등"
        reward_text = "치킨"
        # 1등은 상품 지급; 코인 보상 없음
    elif match_count == 2:
        # 불일치하는 숫자 (학생 선택 중 메인 공에 없는 수; 1개만 존재)
        non_match = list(set(chosen_numbers) - matches)[0]
        if non_match == bonus_ball:
            outcome = "2등"
            reward_text = "햄버거세트"
        else:
            outcome = "3등"
            reward = random.randint(2, 3)
            reward_text = f"{reward} 코인"
            students_data.at[student_index, "세진코인"] += reward
    elif match_count == 1:
        outcome = "추가게임"
        game_type = "추가"
    else:
        outcome = "다음 기회에"
    
    if outcome in ["1등", "2등"]:
        st.success(f"축하합니다! {outcome} 당첨! 상품: {reward_text}을(를) 획득하였습니다.")
    elif outcome == "3등":
        st.success(f"축하합니다! {outcome} 당첨! {reward_text}을(를) 획득하였습니다.")
    elif outcome == "추가게임":
        st.info("메인 공과 1개만 일치합니다. 추가 게임을 진행하여 홀/짝을 맞춰보세요!")
    else:
        st.error("아쉽게도 당첨되지 않았습니다. 다음 기회에!")
    
    # 기록 생성
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_record = {
        "반": selected_class,
        "학생": selected_student,
        "게임유형": game_type,
        "결과": outcome,
        "상품/코인획득": reward_text,
        "코인차감": cost,
        "시간": now,
    }
    # pd.concat로 데이터프레임에 새 기록 추가 (append 대신)
    lottery_data = pd.concat([lottery_data, pd.DataFrame([new_record])], ignore_index=True)
    # 전역 변수 업데이트
    globals()['lottery_data'] = lottery_data

    save_students_data(students_data)
    save_lottery_record(lottery_data)
    st.write(f"현재 잔액: **{students_data.at[student_index, '세진코인']} 코인**")
    
    return outcome

# -----------------------------
# 학생 로그인 후 로또 게임 진행
if student_pw:
    if selected_student in student_passwords and student_pw == student_passwords[selected_student]:
        st.success(f"{selected_student}님, 환영합니다!")
        coin_balance = int(students_data.at[student_index, "세진코인"])
        st.write(f"현재 세진코인 잔액: **{coin_balance} 코인**")
        
        st.write("1부터 20까지의 숫자 중 **정확히 3개**의 숫자를 선택하세요:")
        selected_numbers = st.multiselect("숫자 선택", list(range(1,21)))
        if len(selected_numbers) != 3:
            st.warning("정확히 3개의 숫자를 선택해야 합니다.")
        else:
            if st.button("로또 게임 시작 (1코인 차감)"):
                result = play_lottery(selected_numbers, is_free=False)
                # 추가 게임 진행: match_count == 1 일 때 result는 "추가게임"
                if result == "추가게임":
                    st.markdown("---")
                    st.write("**추가 게임: 홀수/짝수 맞추기**")
                    player_choice = st.radio("홀수 또는 짝수를 선택하세요:", ("홀수", "짝수"))
                    if st.button("추가 게임 진행"):
                        comp_choice = random.choice(["홀수", "짝수"])
                        st.write(f"컴퓨터의 선택: **{comp_choice}**")
                        if player_choice == comp_choice:
                            st.success("추가 게임 승리! 무료 로또 게임 기회를 드립니다.")
                            if st.button("무료 추가 로또 게임 시작"):
                                play_lottery(selected_numbers, is_free=True)
                        else:
                            st.error("추가 게임에서 실패하였습니다. 다음 기회에!")
    else:
        st.error("비밀번호가 올바르지 않습니다.")

# -----------------------------
# 나의 로또 게임 기록 보기 (학생용)
if student_pw and selected_student in student_passwords and student_pw == student_passwords[selected_student]:
    my_records = lottery_data[(lottery_data["반"] == selected_class) & (lottery_data["학생"] == selected_student)]
    st.subheader("나의 로또 게임 기록")
    st.dataframe(my_records)

# -----------------------------
# 관리자 모드: 전체 로또 기록 확인
st.markdown("---")
admin_pw = st.text_input("관리자 모드 비밀번호를 입력하세요 (로또 기록 확인):", type="password")
if admin_pw == ADMIN_PASSWORD:
    st.subheader("전체 로또 게임 기록")
    st.dataframe(lottery_data)
