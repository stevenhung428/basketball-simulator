import streamlit as st
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

st.set_page_config(page_title="投籃模擬器：動畫 + 統計 + 3D")
st.title("\U0001F3C0 投籃模擬器")

# 模式選擇
mode = st.radio("請選擇模式", ["\U0001F3A5 拋物線動畫", "\U0001F4CA 命中率統計模擬", "\U0001F3AC 3D 拋物線模擬"])

# 共用參數
v = st.slider("平均初速度（m/s）", 1.0, 20.0, 10.0)
theta_deg = st.slider("平均投擲角度（°）", 10.0, 80.0, 45.0)
y0 = st.slider("出手高度（m）", 1.2, 2.5, 1.8)
v_wind = st.slider("風速（m/s）", -5.0, 5.0, 0.0)
spin_rate = st.slider("旋轉圈速（圈/秒）", 0.0, 100.0, 30.0)
k_drag = st.slider("空氣阻力係數", 0.0, 0.1, 0.02)
s_magnus = st.slider("馬格努斯係數", 0.0, 0.05, 0.01)

# 單次模擬函數
def simulate_once(theta_rad, v_input):
    vx = v_input * np.cos(theta_rad) + v_wind
    vy = v_input * np.sin(theta_rad)
    x, y = 0.0, y0
    dt = 0.01
    traj_x = []
    traj_y = []
    while y >= 0 and x <= 10:
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

# 拋物線動畫模式
if mode == "\U0001F3A5 拋物線動畫":
    speed_ms = st.slider("動畫速度（毫秒/frame）", 10, 300, 30, step=10)
    theta_rad = np.radians(theta_deg)
    traj_x, traj_y, _ = simulate_once(theta_rad, v)

    frames = []
    for i in range(3, len(traj_x), 3):
        frames.append(go.Frame(data=[go.Scatter(x=traj_x[:i], y=traj_y[:i],
                                                mode='lines+markers', line=dict(color='green'))]))

    fig = go.Figure(
        data=[go.Scatter(x=[], y=[], mode='lines+markers')],
        layout=go.Layout(
            title="\U0001F3C0 投籃拋物線動畫",
            xaxis=dict(range=[0, max(traj_x)*1.1], title='水平距離 (m)'),
            yaxis=dict(range=[0, max(traj_y)*1.2], title='垂直高度 (m)'),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                buttons=[dict(label="播放", method="animate",
                              args=[None, {"frame": {"duration": speed_ms, "redraw": True}, "fromcurrent": True}])]
            )]
        ),
        frames=frames
    )
    fig.add_trace(go.Scatter(x=[4.5], y=[3.05], mode='markers+text',
                             marker=dict(color='blue', size=12),
                             text=["籃框"], textposition="top center"))
    st.plotly_chart(fig)

# 命中率統計模式
elif mode == "\U0001F4CA 命中率統計模擬":
    n_runs = st.slider("模擬輪數", 1, 20, 10)
    n_per_run = st.slider("每輪投籃次數", 1, 300, 100)
    progress = st.progress(0)
    hit_rates = []

    for run in range(n_runs):
        hits = 0
        for _ in range(n_per_run):
            theta_rand = np.radians(theta_deg + np.random.normal(0, 2))
            v_rand = v + np.random.normal(0, 0.5)
            _, _, is_hit = simulate_once(theta_rand, v_rand)
            if is_hit:
                hits += 1
        hit_rates.append(hits / n_per_run)
        progress.progress((run + 1) / n_runs)

    st.subheader("\U0001F4CA 命中率變化圖")
    fig2, ax = plt.subplots()
    ax.plot(range(1, len(hit_rates)+1), [r*100 for r in hit_rates], marker='o')
    ax.set_xlabel("測試輪次")
    ax.set_ylabel("命中率 (%)")
    ax.set_title("命中率是否進步？")
    ax.grid(True)
    st.pyplot(fig2)

    if hit_rates:
        st.write(f"\U0001F3AF 平均命中率：{np.mean(hit_rates)*100:.2f}%")
        st.write(f"\U0001F4C8 最佳命中率：{max(hit_rates)*100:.1f}%")
        st.write(f"\U0001F4C9 最差命中率：{min(hit_rates)*100:.1f}%")
    else:
        st.warning("⚠️ 尚未完成模擬，無法計算命中率統計")

# 3D 模擬模式
elif mode == "\U0001F3AC 3D 拋物線模擬":
    st.subheader("\U0001F9CA 3D 投籃模擬")
    num_balls = st.slider("模擬球數", 1, 30, 10)
    speed_ms = st.slider("動畫速度（毫秒/frame）", 10, 300, 50, step=10)

    all_trajectories = []
    max_x, max_y, max_z = 0, 0, 0

    for i in range(num_balls):
        theta_rand = np.radians(theta_deg + np.random.normal(0, 2))
        v_rand = v + np.random.normal(0, 0.5)
        vx = v_rand * np.cos(theta_rand) + v_wind
        vy = v_rand * np.sin(theta_rand)
        x, y, z = 0.0, y0, 0.0
        dt = 0.01
        x_list, y_list, z_list = [], [], []
        lateral_drift = np.random.uniform(-0.4, 0.4)

        while y >= 0 and x <= 10:
            x_list.append(x)
            y_list.append(z)
            z_list.append(y)
            ax = -k_drag * vx * abs(vx)
            ay = -9.8 - k_drag * vy * abs(vy) + s_magnus * vx * spin_rate
            vx += ax * dt
            vy += ay * dt
            x += vx * dt
            y += vy * dt
            z += lateral_drift * dt

        color = "green" if abs(x - 4.5) < 0.3 and abs(y - 3.05) < 0.3 and abs(z) < 0.3 else "red"
        all_trajectories.append((x_list, y_list, z_list, color))
        max_x = max(max_x, max(x_list))
        max_y = max(max_y, max(y_list))
        max_z = max(max_z, max(z_list))

    frames = []
    max_len = max(len(t[0]) for t in all_trajectories)
    for i in range(0, max_len, 2):
        data = []
        for x_list, y_list, z_list, color in all_trajectories:
            x_i = x_list[:i] if i < len(x_list) else x_list
            y_i = y_list[:i] if i < len(y_list) else y_list
            z_i = z_list[:i] if i < len(z_list) else z_list
            data.append(go.Scatter3d(
                x=x_i, y=y_i, z=z_i,
                mode='lines',
                line=dict(color=color, width=4)
            ))
        data.append(go.Scatter3d(
            x=[4.5], y=[0], z=[3.05],
            mode='markers+text',
            marker=dict(color='blue', size=6),
            text=["籃框"],
            textposition="top center"
        ))
        frames.append(go.Frame(data=data))

    layout = go.Layout(
        scene=dict(
            xaxis=dict(title='X (前後)'),
            yaxis=dict(title='Z (左右)'),
            zaxis=dict(title='Y (高度)')
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        title="\U0001F3C0 多球 3D 拋物線動畫",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="播放", method="animate",
                          args=[None, {"frame": {"duration": speed_ms, "redraw": True},
                                       "fromcurrent": True}])]
        )]
    )

    fig = go.Figure(data=[], layout=layout, frames=frames)
    st.plotly_chart(fig)
