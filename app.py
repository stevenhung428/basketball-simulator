import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(page_title="投籃模擬器：動畫 + 統計 + 3D")
st.title("🏀 投籃模擬器")

mode = st.radio("請選擇模式", ["🎥 拋物線動畫", "📊 命中率統計模擬", "🎬 3D 拋物線模擬"])

v = st.slider("平均初速度（m/s）", 1.0, 20.0, 10.0)
theta_deg = st.slider("平均投擲角度（°）", 10.0, 80.0, 45.0)
y0 = st.slider("出手高度（m）", 1.2, 2.5, 1.8)
v_wind = st.slider("風速（m/s）", -5.0, 5.0, 0.0)
spin_rate = st.slider("旋轉圈速（圈/秒）", 0.0, 100.0, 30.0)
k_drag = st.slider("空氣阻力係數", 0.0, 0.1, 0.02)
s_magnus = st.slider("馬格努斯係數", 0.0, 0.05, 0.01)

def simulate_once(theta_rad, v_input):
    vx = v_input * np.cos(theta_rad) + v_wind
    vy = v_input * np.sin(theta_rad)
    vz = np.random.normal(0, 0.5)
    x, y, z = 0.0, y0, 0.0
    dt = 0.01
    traj_x, traj_y, traj_z = [], [], []
    while y >= 0 and x <= 10:
        traj_x.append(x)
        traj_y.append(y)
        traj_z.append(z)
        ax = -k_drag * vx * abs(vx)
        ay = -9.8 - k_drag * vy * abs(vy) + s_magnus * vx * spin_rate
        az = -k_drag * vz * abs(vz)
        vx += ax * dt
        vy += ay * dt
        vz += az * dt
        x += vx * dt
        y += vy * dt
        z += vz * dt
        if abs(x - 4.5) < 0.3 and abs(y - 3.05) < 0.3 and abs(z) < 0.3:
            return traj_x, traj_y, traj_z, True
    return traj_x, traj_y, traj_z, False

# 3D 模式
if mode == "🎬 3D 拋物線模擬":
    num_balls = st.slider("投籃次數（顆）", 1, 30, 10)
    theta_rad = np.radians(theta_deg)
    all_trajectories = []

    for _ in range(num_balls):
        t = simulate_once(theta_rad + np.random.normal(0, 0.05), v + np.random.normal(0, 0.5))
        if len(t[0]) > 1:
            all_trajectories.append(t)

    if not all_trajectories:
        st.error("⚠️ 所有球的模擬都失敗，請調整初速度或角度試試看！")
    else:
        frames = []
        max_len = max(len(t[0]) for t in all_trajectories)
        for i in range(0, max_len, 2):
            frame_data = []
            for t in all_trajectories:
                if i < len(t[0]):
                    frame_data.append(go.Scatter3d(
                        x=t[0][:i], y=t[2][:i], z=t[1][:i],
                        mode='lines', line=dict(width=4)))
            frames.append(go.Frame(data=frame_data))

        first_frame_data = []
        for t in all_trajectories:
            first_frame_data.append(go.Scatter3d(
                x=[t[0][0]], y=[t[2][0]], z=[t[1][0]],
                mode='lines', line=dict(width=4)))

        layout = go.Layout(
            scene=dict(
                xaxis=dict(title='水平距離 (m)', range=[0, 10]),
                yaxis=dict(title='左右偏移 (m)', range=[-2, 2]),
                zaxis=dict(title='垂直高度 (m)', range=[0, 5])
            ),
            title="🏀 3D 投籃模擬動畫",
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(label="播放", method="animate",
                              args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}])]
            )]
        )

        fig = go.Figure(data=first_frame_data, layout=layout, frames=frames)
        fig.add_trace(go.Scatter3d(
            x=[4.5], y=[0], z=[3.05],
            mode='markers+text',
            marker=dict(size=6, color='blue'),
            text=["籃框"], textposition='top center'))
        st.plotly_chart(fig)
