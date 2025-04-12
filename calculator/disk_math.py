import numpy as np
import sympy as sp
from scipy.integrate import quad
import plotly.graph_objs as go

def volume_disk_method(func, a, b):
    volume, _ = quad(lambda x: np.pi * (func(x)**2), a, b)
    return volume

def get_plot_data(func, a, b):
    x_vals = np.linspace(a, b, 100)
    y_vals = func(x_vals)
    theta = np.linspace(0, 2 * np.pi, 100)
    X = np.linspace(a, b, 100)
    Y = np.outer(func(X), np.cos(theta))
    Z = np.outer(func(X), np.sin(theta))
    x_surface = np.repeat(X[:, np.newaxis], len(theta), axis=1)
    return x_vals, y_vals, x_surface, Y, Z

def generate_figures(func_str, a, b):
    x = sp.symbols('x')
    func = sp.sympify(func_str)
    func_numeric = sp.lambdify(x, func, 'numpy')

    volume = volume_disk_method(func_numeric, a, b)
    x_vals, y_vals, x_surface, Y, Z = get_plot_data(func_numeric, a, b)

    # ---------- Function f(x) Plot ----------
    function_fig = go.Figure()
    function_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='yellow')))
    function_fig.update_layout(
        title='Function f(x)', 
        xaxis_title='x', 
        yaxis_title='f(x)', 
        plot_bgcolor='#1c2e2e', 
        paper_bgcolor='#1c2e2e', 
        font_color='lightgreen'
    )

    # ---------- Rotating Solid with Side Bar ----------
    num_frames = 50
    frames = []

    x_col = [b + 1] * 8
    y_col = [0, 0, 0.1, 0.1, 0, 0, 0.1, 0.1]
    z_col_template = [0, 0, 0, 0.1, 0, 1, 1, 0.1]  # Will be scaled
    i_col = [0, 1, 2, 3, 4, 5, 6, 7, 0, 2, 4, 6]
    j_col = [1, 3, 0, 2, 5, 7, 4, 6, 4, 6, 5, 7]
    k_col = [2, 2, 4, 4, 6, 6, 0, 0, 5, 5, 7, 7]

    for i in range(num_frames):
        angle = i / (num_frames - 1) * 2 * np.pi
        current_theta = np.linspace(0, angle, 100)
        frame_y = np.outer(func_numeric(x_surface[:, 0]), np.cos(current_theta))
        frame_z = np.outer(func_numeric(x_surface[:, 0]), np.sin(current_theta))

        # Bar height
        bar_height = (i + 1) / num_frames
        z_col = [z * bar_height for z in z_col_template]

        frames.append(go.Frame(data=[
            go.Surface(x=x_surface, y=frame_y, z=frame_z, opacity=0.7, colorscale='Viridis'),
            go.Mesh3d(
                x=x_col, y=y_col, z=z_col,
                i=i_col, j=j_col, k=k_col,
                color='yellowgreen',
                opacity=0.8,
                name='ProgressBar'
            )
        ]))

    final_surface = go.Surface(x=x_surface, y=Y, z=Z, colorscale='Viridis', opacity=0.7)
    final_bar = go.Mesh3d(
        x=x_col, y=y_col, z=[0] * 8,
        i=i_col, j=j_col, k=k_col,
        color='darkgreen',
        opacity=0.8,
        name='ProgressBar'
    )

    solid_fig = go.Figure(data=[final_surface, final_bar])
    solid_fig.frames = frames
    solid_fig.update_layout(
        title='Rotating Solid of Revolution with Progress Bar',
        scene=dict(
            xaxis_title='X', 
            yaxis_title='Y', 
            zaxis_title='Z',
            xaxis=dict(backgroundcolor='#1c2e2e'),
            yaxis=dict(backgroundcolor='#1c2e2e'),
            zaxis=dict(backgroundcolor='#1c2e2e')
        ),
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate'}],
                    'label': '<b style="color:darkblue">▶ Play</b>',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': False}}],
                    'label': '<b style="color:darkblue">⏸ Pause</b>',
                    'method': 'animate'
                },
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': True,
            'x': 0.1,
            'y': 1.15,
            'type': 'buttons'
        }],
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(15,32,39,1)',
        font_color='lightgreen'
    )

    # ---------- 2D Area Plot ----------
    solid_2d_fig = go.Figure()
    solid_2d_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color='yellow'), name='f(x)'))
    solid_2d_fig.add_trace(go.Scatter(x=x_vals, y=np.zeros_like(x_vals), mode='lines', line=dict(color='white')))
    solid_2d_fig.add_trace(go.Scatter(
        x=np.concatenate([x_vals, x_vals[::-1]]),
        y=np.concatenate([y_vals, np.zeros_like(y_vals)]),
        fill='toself',
        fillcolor='rgba(0,255,100,0.5)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Area'
    ))

    solid_2d_frames = []
    for i in range(num_frames):
        angle = i / (num_frames - 1) * 2 * np.pi
        ry = y_vals * np.cos(angle)
        ry_neg = -y_vals * np.cos(angle)
        solid_2d_frames.append(go.Frame(data=[
            go.Scatter(x=x_vals, y=ry, mode='lines', line=dict(color='lightgreen')),
            go.Scatter(x=x_vals, y=ry_neg, mode='lines', line=dict(color='lightgreen')),
            go.Scatter(
                x=np.concatenate([x_vals, x_vals[::-1]]),
                y=np.concatenate([ry, ry_neg[::-1]]),
                fill='toself',
                fillcolor='rgba(0,255,100,0.5)',
                line=dict(color='rgba(255,255,255,0)')
            )
        ]))

    solid_2d_fig.frames = solid_2d_frames
    solid_2d_fig.update_layout(
        title='2D Area Rotating Around X-axis',
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate'}],
                    'label': '<b style="color:darkblue">▶ Play</b>',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'mode': 'immediate', 'frame': {'duration': 0, 'redraw': False}}],
                    'label': '<b style="color:darkblue">⏸ Pause</b>',
                    'method': 'animate'
                },
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 77},
            'showactive': True,
            'x': 0.1,
            'y': 1.17,
            'type': 'buttons'
        }],
        plot_bgcolor='#1c2e2e',
        paper_bgcolor='#1c2e2e',
        font_color='lightgreen'
    )

    return volume, function_fig.to_html(full_html=False), solid_fig.to_html(full_html=False), solid_2d_fig.to_html(full_html=False)
