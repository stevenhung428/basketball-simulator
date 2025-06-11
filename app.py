import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="投籃物理模擬器")
st.title("🏀 投籃物理模擬器")

v = st.slider("初速度（m/s）", 1.0, 20.0, 10.0)
theta_deg = st.slider("投擲角度（°）", 10.0, 80.0, 45.0)
y0 = st.slider("出手高度（m）", 1.2, 2.5, 1.8)
v_wind = st.slider("風速（m/s，正為順風）", -5.0, 5.0, 0.0)
spin_rate = st.slider("旋轉圈速（圈/秒）", 0.0, 100.0, 30.0)
k_drag = st.slider("空氣阻力係數", 0.0, 0.1, 0.02)
s_magnus = st.slider("馬格努斯係數", 0.0, 0.05, 0.01)
n_trials = st.number_input("模擬投籃次數", min_value=10, max_value=1000, value=100, step=10)

def simulate_once():
    theta = np.radians(theta_deg)
    vx = v * np.cos(theta) + v_wind
    vy = v * np.sin(theta)
    x, y = 0.0, y0
    dt = 0.01
    while y >= 0 and x < 10:
        ax = -k_drag * vx * abs(vx)
        ay = -9.8 - k_drag * vy * abs(vy) + s_magnus * vx * spin_rate
        vx += ax * dt; vy += ay * dt
        x += vx * dt; y += vy * dt
        if abs(x - 4.5) < 0.3 and abs(y - 3.05) < 0.3:
            return x, y, True
    return x, y, False

hits = 0
all_x, all_y, all_hit = [], [], []
for _ in range(n_trials):
    x_sim, y_sim, is_hit = simulate_once()
    all_x.append(x_sim); all_y.append(y_sim); all_hit.append(is_hit)
    if is_hit:
        hits += 1

st.subheader("🎯 模擬結果")
st.write(f"總共模擬：{n_trials} 次投籃")
st.write(f"✅ 投進：{hits} 次；命中率：{hits/n_trials*100:.1f}%")

fig, ax = plt.subplots()
for x_i, y_i, h in zip(all_x, all_y, all_hit):
    ax.scatter(x_i, y_i, c='g' if h else 'r', s=10)
ax.scatter(4.5, 3.05, marker='X', s=100, c='blue', label="籃框")
ax.set_xlabel("水平距離 (m)")
ax.set_ylabel("垂直高度 (m)")
ax.set_ylim(0)
ax.legend()
st.pyplot(fig)
