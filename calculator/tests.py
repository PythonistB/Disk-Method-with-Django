import numpy as np
import sympy as sp
import plotly.graph_objs as go
from scipy.integrate import quad
import plotly.io as pio

def volume_disk_method(func, a, b):
    volume, _ = quad(lambda x: np.pi * (func(x) ** 2), a, b)
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

    # --- Function Figure ---
    function_fig = go.Figure()
    function_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='cyan')))
    function_fig.add_trace(go.Scatter(x=x_vals, y=np.zeros_like(x_vals), mode='lines', name='x-axis', line=dict(color='white')))
    function_fig.update_layout(title='Function f(x)', template='plotly_dark')

    # --- 3D Solid of Revolution ---
    num_frames = 50
    frames = []
    for i in range(num_frames):
        angle = i / (num_frames - 1) * 2 * np.pi
        frame_y = np.outer(func_numeric(x_surface[:, 0]), np.cos(angle))
        frame_z = np.outer(func_numeric(x_surface[:, 0]), np.sin(angle))
        frames.append(go.Frame(data=[
            go.Surface(x=x_surface, y=frame_y, z=frame_z, colorscale='Viridis', opacity=0.7)
        ]))

    solid_fig = go.Figure(data=[
        go.Surface(x=x_surface, y=Y, z=Z, colorscale='Viridis', opacity=0.7)
    ])
    solid_fig.frames = frames
    solid_fig.update_layout(
        title='Rotating Solid of Revolution',
        scene=dict(xaxis_title='x', yaxis_title='y', zaxis_title='z'),
        updatemenus=[{
            'buttons': [
                {'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'mode': 'immediate'}],
                 'label': 'Play', 'method': 'animate'},
                {'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate'}],
                 'label': 'Pause', 'method': 'animate'}
            ],
            'type': 'buttons',
            'showactive': True,
            'x': 0.1, 'y': 1.1, 'xanchor': 'left', 'yanchor': 'top'
        }],
        template='plotly_dark'
    )

    # --- 2D Rotated Area ---
    solid_2d_fig = go.Figure()
    solid_2d_fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='f(x)', line=dict(color='cyan')))
    solid_2d_fig.add_trace(go.Scatter(x=x_vals, y=np.zeros_like(x_vals), mode='lines', name='x-axis', line=dict(color='white')))
    solid_2d_fig.add_trace(go.Scatter(
        x=np.concatenate([x_vals, x_vals[::-1]]),
        y=np.concatenate([y_vals, np.zeros_like(y_vals)]),
        fill='toself', fillcolor='rgba(0,100,255,0.6)', line=dict(color='rgba(0,0,0,0)'), name='Area'
    ))

    frames2d = []
    for i in range(num_frames):
        angle = i / (num_frames - 1) * 2 * np.pi
        rot = func_numeric(x_vals) * np.cos(angle)
        neg_rot = -func_numeric(x_vals) * np.cos(angle)
        frames2d.append(go.Frame(data=[
            go.Scatter(x=x_vals, y=rot, mode='lines', line=dict(color='cyan')),
            go.Scatter(x=x_vals, y=neg_rot, mode='lines', line=dict(color='cyan')),
            go.Scatter(
                x=np.concatenate([x_vals, x_vals[::-1]]),
                y=np.concatenate([rot, neg_rot[::-1]]),
                fill='toself', fillcolor=f'rgba(0, {int(255 * i / num_frames)}, 255, 0.5)',
                line=dict(color='rgba(0,0,0,0)'), name='Rotated Area'
            )
        ]))

    solid_2d_fig.frames = frames2d
    solid_2d_fig.update_layout(
        title='Area Being Rotated Around X-axis',
        updatemenus=[{
            'buttons': [
                {'args': [None, {'frame': {'duration': 100, 'redraw': True}, 'mode': 'immediate'}],
                 'label': 'Play', 'method': 'animate'}
            ],
            'type': 'buttons',
            'showactive': True,
            'x': 0.1, 'y': 1.1, 'xanchor': 'left', 'yanchor': 'top'
        }],
        template='plotly_dark'
    )

    return volume, function_fig.to_html(full_html=False), solid_fig.to_html(full_html=False), solid_2d_fig.to_html(full_html=False)
