import streamlit as st
import streamlit.components.v1 as components
import random
import json
import time

# [1. 파이썬 UI 영역] 웹 페이지 기본 설정 및 제목 표시
st.set_page_config(page_title="행운의 룰렛", page_icon="🎡", layout="centered")

st.title("🎡 파이썬 행운의 룰렛 게임")
st.write("항목을 입력하고 버튼을 누르면 파이썬이 당첨자를 추첨하고 룰렛을 돌립니다!")

# 사용자로부터 추첨 항목 입력받기 (기본값: 점심 메뉴 6가지)
default_items = "치킨\n피자\n삼겹살\n초밥\n떡볶이\n햄버거"
raw_input = st.text_area(
    "추첨할 항목을 입력하세요 (줄바꿈 또는 쉼표로 구분)", 
    value=default_items, 
    height=140
)

# 파이썬 문자열 처리로 빈칸을 제거하고 깔끔한 리스트(List)로 변환
items = [item.strip() for item in raw_input.replace(',', '\n').split('\n') if item.strip()]

# 항목이 2개 미만일 때 안내 문구 출력
if len(items) < 2:
    st.warning("최소 2개 이상의 항목을 입력해 주세요.")
else:
    # 웹 화면이 새로고침되어도 추첨 결과를 기억하도록 세션 상태(Session State) 초기화
    if "spin_data" not in st.session_state:
        st.session_state.spin_data = None
    if "trigger_balloons" not in st.session_state:
        st.session_state.trigger_balloons = False

    # [2. 파이썬 무작위 추첨 영역] 버튼을 누르면 random 모듈이 당첨자를 결정
    if st.button("🎯 룰렛 돌리기!", use_container_width=True, type="primary"):
        winner_idx = random.randint(0, len(items) - 1)
        st.session_state.spin_data = {
            "winner_idx": winner_idx,
            "winner_name": items[winner_idx],
            "extra_spins": random.randint(5, 8), # 5~8바퀴 무작위 회전
            "jitter": random.uniform(-0.35, 0.35), # 멈추는 위치 미세 조정
            "spin_id": random.randint(1, 1000000) # 매번 새로 돌게 하는 고유 번호
        }
        st.session_state.trigger_balloons = True

    # [3. 파이썬 데이터를 HTML 그래픽으로 넘겨주는 영역]
    # 파이썬 리스트와 추첨 결과를 HTML이 읽을 수 있는 JSON 텍스트로 변환
    items_json = json.dumps(items, ensure_ascii=False)
    spin_json = json.dumps(st.session_state.spin_data, ensure_ascii=False)

    # 파이썬 f-string을 이용해 HTML5 룰렛 그래픽 코드를 동적으로 조립
    roulette_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: sans-serif;">
        <div style="position: relative; width: 350px; height: 350px; margin-top: 15px;">
            <!-- 12시 방향 빨간색 당첨 화살표 -->
            <div style="position: absolute; top: -12px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid #FF2B2B; z-index: 10; filter: drop-shadow(0px 3px 4px rgba(0,0,0,0.3));"></div>
            <!-- 룰렛 원판 캔버스 -->
            <canvas id="wheel" width="350" height="350" style="transition: transform 4s cubic-bezier(0.15, 0.85, 0.15, 1); border-radius: 50%; box-shadow: 0 6px 20px rgba(0,0,0,0.18);"></canvas>
        </div>
        <div id="result-box" style="margin-top: 25px; font-size: 24px; font-weight: 800; color: #1E293B; min-height: 40px; text-align: center;"></div>
    </div>

    <script>
    // 파이썬이 넘겨준 데이터를 받아서 원판 그리기
    const items = {items_json};
    const spinData = {spin_json};
    const canvas = document.getElementById('wheel');
    const ctx = canvas.getContext('2d');
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9', '#F1948A', '#82E0AA'];
    
    const numItems = items.length;
    const arc = (2 * Math.PI) / numItems;
    const radius = canvas.width / 2;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < numItems; i++) {{
        const angle = i * arc - Math.PI / 2;
        ctx.beginPath();
        ctx.fillStyle = colors[i % colors.length];
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius, angle, angle + arc);
        ctx.lineTo(radius, radius);
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#ffffff';
        ctx.stroke();

        // 항목 글자 쓰기
        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(angle + arc / 2);
        ctx.textAlign = "right";
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 16px sans-serif";
        ctx.shadowColor = "rgba(0,0,0,0.4)";
        ctx.shadowBlur = 4;
        const text = items[i].length > 9 ? items[i].substring(0, 8) + '..' : items[i];
        ctx.fillText(text, radius - 25, 6);
        ctx.restore();
    }}

    // 가운데 원 장식
    ctx.beginPath();
    ctx.arc(radius, radius, 20, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.lineWidth = 4;
    ctx.strokeStyle = '#334155';
    ctx.stroke();

    // 파이썬에서 추첨 신호가 오면 4초간 회전 애니메이션 실행
    if (spinData !== null) {{
        const sliceDeg = 360 / numItems;
        const targetDeg = spinData.extra_spins * 360 + (360 - (spinData.winner_idx + 0.5 + spinData.jitter) * sliceDeg);
        
        requestAnimationFrame(() => {{
            setTimeout(() => {{
                canvas.style.transform = `rotate(${{targetDeg}}deg)`;
            }}, 50);
        }});

        setTimeout(() => {{
            document.getElementById('result-box').innerHTML = `🎉 당첨: <span style="color: #E11D48;">${{spinData.winner_name}}</span> 🎉`;
        }}, 4100);
    }}
    </script>
    """
    
    # 조립된 HTML을 웹 화면에 출력
    components.html(roulette_html, height=440)

    # 룰렛이 멈추는 시간(4초)에 맞춰 축하 풍선 날리기
    if st.session_state.trigger_balloons:
        time.sleep(4.0)
        st.balloons()
        st.session_state.trigger_balloons = False