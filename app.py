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

if mode == "🎥 拋物線動畫":
    speed_ms = st.slider("動畫速度（毫秒/frame）", 10, 300, 30, step=10)
    theta_rad = np.radians(theta_deg)
    traj_x, traj_y, _, = simulate_once(theta_rad, v)
    frames = []
    for i in range(3, len(traj_x), 3):
        frames.append(go.Frame(data=[go.Scatter(x=traj_x[:i], y=traj_y[:i],
                                                mode='lines+markers', line=dict(color='green'))]))
    layout = go.Layout(
        title="🏀 拋物線動畫",
        xaxis=dict(range=[0, max(traj_x)*1.1], title='水平距離 (m)'),
        yaxis=dict(range=[0, max(traj_y)*1.2], title='垂直高度 (m)'),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="播放", method="animate",
                          args=[None, {"frame": {"duration": speed_ms, "redraw": True}, "fromcurrent": True}])]
        )]
    )
    fig = go.Figure(data=[go.Scatter(x=[], y=[], mode='lines+markers')], layout=layout, frames=frames)
    fig.add_trace(go.Scatter(x=[4.5], y=[3.05], mode='markers+text',
                             marker=dict(color='blue', size=12),
                             text=["籃框"], textposition="top center"))
    st.plotly_chart(fig)

elif mode == "📊 命中率統計模擬":
    n_runs = st.slider("模擬輪數", 1, 20, 10)
    n_per_run = st.slider("每輪投籃次數", 10, 300, 100)
    progress = st.progress(0)
    hit_rates = []
    for run in range(n_runs):
        hits = 0
        for _ in range(n_per_run):
            theta_rand = np.radians(theta_deg + np.random.normal(0, 2))
            v_rand = v + np.random.normal(0, 0.5)
            _, _, _, is_hit = simulate_once(theta_rand, v_rand)
            if is_hit:
                hits += 1
        hit_rates.append(hits / n_per_run)
        progress.progress((run + 1) / n_runs)
    st.subheader("📊 命中率變化圖")
    fig2, ax = plt.subplots()
    ax.plot(range(1, len(hit_rates)+1), [r*100 for r in hit_rates], marker='o')
    ax.set_xlabel("測試輪次")
    ax.set_ylabel("命中率 (%)")
    ax.set_title("命中率是否進步？")
    ax.grid(True)
    st.pyplot(fig2)
    st.write(f"🎯 平均命中率：{np.mean(hit_rates)*100:.2f}%")
    st.write(f"📈 最佳命中率：{max(hit_rates)*100:.1f}%")
    st.write(f"📉 最差命中率：{min(hit_rates)*100:.1f}%")

elif mode == "🎬 3D 拋物線模擬":
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
                              args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}])])]
        )
        fig = go.Figure(data=first_frame_data, layout=layout, frames=frames)
        fig.add_trace(go.Scatter3d(
            x=[4.5], y=[0], z=[3.05],
            mode='markers+text',
            marker=dict(size=6, color='blue'),
            text=["籃框"], textposition='top center'))
        st.plotly_chart(fig)
