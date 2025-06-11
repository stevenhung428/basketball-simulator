import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="投籃物理模擬器")
st.title("🏀 投籃物理模擬器")

# 使用者參數
v = st.slider("初速度（m/s）", 1.0, 20.0, 10.0)
theta_deg = st.slider("投擲角度（°）", 10.0, 80.0, 45.0)
y0 = st.slider("出手高度（m）", 1.2, 2.5, 1.8)
v_wind = st.slider("風速（m/s）", -5.0, 5.0, 0.0)
spin_rate = st.slider("旋轉圈速（圈/秒）", 0.0, 100.0, 30.0)
k_drag = st.slider("空氣阻力係數", 0.0, 0.1, 0.02)
s_magnus = st.slider("馬格努斯係數", 0.0, 0.05, 0.01)
n_trials = st.number_input("模擬次數", 10, 1000, 100, step=10)

# 模擬一次投籃，回傳軌跡與是否命中
def simulate_once():
    theta = np.radians(theta_deg)
    vx = v * np.cos(theta) + v_wind
    vy = v * np.sin(theta)
    x, y = 0.0, y0
    dt = 0.01
    traj_x = []
    traj_y = []
    while y >= 0 and x < 10:
        traj_x.append(x)
        traj_y.append(y)
        ax = -k_drag * vx * abs(vx)
        ay = -9.8 - k_drag * vy * abs(vy) + s_magnus * vx * spin_rate
        vx += ax * dt
        vy += ay * dt
        x += vx * dt
        y += vy * dt
        if abs(x - 4.5) < 0.3 and abs(y - 3.05) < 0.3:
            return traj_x, traj_y, True
    return traj_x, traj_y, False

# 模擬多次
all_traj = []
hits = 0
for _ in range(n_trials):
    x_traj, y_traj, is_hit = simulate_once()
    all_traj.append((x_traj, y_traj, is_hit))
    if is_hit:
        hits += 1

# 顯示命中率
st.subheader("🎯 模擬結果")
st.write(f"總共模擬：{n_trials} 次")
st.write(f"✅ 命中：{hits} 次（命中率：{hits/n_trials*100:.1f}%）")

# 繪圖
fig, ax = plt.subplots()
for x_list, y_list, is_hit in all_traj:
    ax.plot(x_list, y_list, color='green' if is_hit else 'red', alpha=0.4)
ax.scatter(4.5, 3.05, marker='X', s=100, c='blue', label="籃框")
ax.set_xlabel("水平距離 (m)")
ax.set_ylabel("垂直高度 (m)")
ax.set_ylim(0)
ax.legend()
st.pyplot(fig)
