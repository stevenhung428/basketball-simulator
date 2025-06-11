import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="拋物線動畫投籃模擬器")
st.title("🏀 投籃動畫模擬器")

# 使用者參數
v = st.slider("初速度（m/s）", 1.0, 20.0, 10.0)
theta_deg = st.slider("投擲角度（°）", 10.0, 80.0, 45.0)
y0 = st.slider("出手高度（m）", 1.2, 2.5, 1.8)
v_wind = st.slider("風速（m/s）", -5.0, 5.0, 0.0)
spin_rate = st.slider("旋轉圈速（圈/秒）", 0.0, 100.0, 30.0)
k_drag = st.slider("空氣阻力係數", 0.0, 0.1, 0.02)
s_magnus = st.slider("馬格努斯係數", 0.0, 0.05, 0.01)

# 模擬單次投籃軌跡
theta = np.radians(theta_deg)
vx = v * np.cos(theta) + v_wind
vy = v * np.sin(theta)
x, y = 0.0, y0
dt = 0.01

x_list = []
y_list = []

while y >= 0 and x <= 10:
    x_list.append(x)
    y_list.append(y)
    ax = -k_drag * vx * abs(vx)
    ay = -9.8 - k_drag * vy * abs(vy) + s_magnus * vx * spin_rate
    vx += ax * dt
    vy += ay * dt
    x += vx * dt
    y += vy * dt

# 建立動畫 Frame
frames = []
for i in range(1, len(x_list)):
    frames.append(go.Frame(data=[go.Scatter(x=x_list[:i], y=y_list[:i],
                                            mode='lines+markers', line=dict(color='green'))]))

# 畫動畫圖
fig = go.Figure(
    data=[go.Scatter(x=[], y=[], mode='lines+markers')],
    layout=go.Layout(
        title="🏀 投籃拋物線動畫",
        xaxis=dict(range=[0, max(x_list)*1.1], title='水平距離 (m)'),
        yaxis=dict(range=[0, max(y_list)*1.2], title='垂直高度 (m)'),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="播放", method="animate", args=[None])])]
    ),
    frames=frames
)

# 顯示籃框位置
fig.add_trace(go.Scatter(x=[4.5], y=[3.05], mode='markers+text',
                         marker=dict(color='blue', size=12),
                         text=["籃框"], textposition="top center"))

st.plotly_chart(fig)
st.pyplot(fig)
