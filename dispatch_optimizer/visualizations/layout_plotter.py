"""
layout_plotter.py
Visualizes 2D and 3D warehouse storage layout using realistic packing algorithms.
"""

import plotly.graph_objects as go
import numpy as np

def simple_pack_2d(products, storage_length, storage_width):
    """
    Simple 2D packing algorithm - places boxes in rows for warehouse storage.
    """
    positions = []
    current_x = 0
    current_y = 0
    row_height = 0
    
    for product in products:
        # Check if box fits in current row
        if current_x + product['Length'] > storage_length:
            # Move to next row
            current_x = 0
            current_y += row_height
            row_height = 0
        
        # Check if box fits in storage width
        if current_y + product['Width'] > storage_width:
            # Start new storage area (for demo purposes, we'll just continue)
            current_x = 0
            current_y = 0
            row_height = 0
        
        positions.append({
            'x': current_x,
            'y': current_y,
            'product': product
        })
        
        current_x += product['Length']
        row_height = max(row_height, product['Width'])
    
    return positions

def simple_pack_3d(products, storage_length, storage_width, storage_height):
    """
    Simple 3D packing algorithm - places boxes in layers for warehouse storage.
    """
    positions = []
    current_x = 0
    current_y = 0
    current_z = 0
    layer_height = 0
    layer_width = 0
    
    for product in products:
        # Check if box fits in current layer
        if current_x + product['Length'] > storage_length:
            # Move to next position in same layer
            current_x = 0
            current_y += layer_width
            layer_width = 0
        
        # Check if we need a new layer
        if current_y + product['Width'] > storage_width:
            # Start new layer
            current_x = 0
            current_y = 0
            current_z += layer_height
            layer_height = 0
            layer_width = 0
        
        # Check if box fits in storage height
        if current_z + product['Height'] > storage_height:
            # For demo, we'll just continue (in real app, this would start new storage area)
            current_x = 0
            current_y = 0
            current_z = 0
            layer_height = 0
            layer_width = 0
        
        positions.append({
            'x': current_x,
            'y': current_y,
            'z': current_z,
            'product': product
        })
        
        current_x += product['Length']
        layer_width = max(layer_width, product['Width'])
        layer_height = max(layer_height, product['Height'])
    
    return positions

def plot_layout(dispatch_plan, constraints):
    """
    Visualize the storage layout in 2D with realistic warehouse dimensions.
    Args:
        dispatch_plan (list of dict): Optimized storage plan with positions.
        constraints (dict): Storage dimensions and constraints.
    Returns:
        plotly.graph_objs.Figure: 2D layout figure.
    """
    storage_length = constraints.get('storage_length', 40)
    storage_width = constraints.get('storage_width', 20)
    
    # Pack products in 2D
    positions = simple_pack_2d(dispatch_plan, storage_length, storage_width)
    
    fig = go.Figure()
    
    # Draw storage area outline
    fig.add_shape(
        type="rect",
        x0=0, y0=0,
        x1=storage_length, y1=storage_width,
        line=dict(color="black", width=3),
        fillcolor="rgba(200,200,200,0.1)"
    )
    
    # Draw each product
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, pos in enumerate(positions):
        product = pos['product']
        color = colors[i % len(colors)]
        
        # Convert hex to rgba for fillcolor
        hex_color = color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        rgba_color = f'rgba({r},{g},{b},0.3)'
        
        # Draw product box
        fig.add_shape(
            type="rect",
            x0=pos['x'], y0=pos['y'],
            x1=pos['x'] + product['Length'], y1=pos['y'] + product['Width'],
            line=dict(color=color, width=2),
            fillcolor=rgba_color
        )
        
        # Add product label
        fig.add_annotation(
            x=pos['x'] + product['Length']/2,
            y=pos['y'] + product['Width']/2,
            text=f"{product['Product']}<br>({product['Length']}x{product['Width']}x{product['Height']} ft, {product['Weight']} lbs)",
            showarrow=False,
            font=dict(size=8)
        )
    
    fig.update_layout(
        title="2D Warehouse Storage Layout (Top View)",
        xaxis_title="Length (ft)",
        yaxis_title="Width (ft)",
        showlegend=False,
        height=500,
        xaxis=dict(range=[-1, storage_length + 1]),
        yaxis=dict(range=[-1, storage_width + 1])
    )
    
    return fig

def plot_layout_3d(dispatch_plan, constraints):
    """
    Visualize the storage layout in 3D with realistic warehouse dimensions.
    Args:
        dispatch_plan (list of dict): Optimized storage plan with positions.
        constraints (dict): Storage dimensions and constraints.
    Returns:
        plotly.graph_objs.Figure: 3D layout figure.
    """
    storage_length = constraints.get('storage_length', 40)
    storage_width = constraints.get('storage_width', 20)
    storage_height = constraints.get('storage_height', 15)
    
    # Pack products in 3D
    positions = simple_pack_3d(dispatch_plan, storage_length, storage_width, storage_height)
    
    fig = go.Figure()
    
    # Draw storage area outline (wireframe)
    storage_vertices = [
        [0, 0, 0], [storage_length, 0, 0], [storage_length, storage_width, 0], [0, storage_width, 0],
        [0, 0, storage_height], [storage_length, 0, storage_height], [storage_length, storage_width, storage_height], [0, storage_width, storage_height]
    ]
    
    # Storage area edges
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom
        [4, 5], [5, 6], [6, 7], [7, 4],  # Top
        [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical
    ]
    
    for edge in edges:
        start = storage_vertices[edge[0]]
        end = storage_vertices[edge[1]]
        fig.add_trace(go.Scatter3d(
            x=[start[0], end[0]],
            y=[start[1], end[1]],
            z=[start[2], end[2]],
            mode='lines',
            line=dict(color='black', width=3),
            showlegend=False
        ))
    
    # Draw each product as 3D boxes
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, pos in enumerate(positions):
        product = pos['product']
        color = colors[i % len(colors)]
        
        # Create 3D box vertices
        x = pos['x']
        y = pos['y']
        z = pos['z']
        l = product['Length']
        w = product['Width']
        h = product['Height']
        
        # Box vertices
        vertices = [
            [x, y, z], [x+l, y, z], [x+l, y+w, z], [x, y+w, z],
            [x, y, z+h], [x+l, y, z+h], [x+l, y+w, z+h], [x, y+w, z+h]
        ]
        
        # Box faces (triangles for each face)
        faces = [
            [0, 1, 2, 3],  # Bottom
            [4, 5, 6, 7],  # Top
            [0, 1, 5, 4],  # Front
            [2, 3, 7, 6],  # Back
            [0, 3, 7, 4],  # Left
            [1, 2, 6, 5]   # Right
        ]
        
        # Add 3D mesh for the box
        fig.add_trace(go.Mesh3d(
            x=[v[0] for v in vertices],
            y=[v[1] for v in vertices],
            z=[v[2] for v in vertices],
            i=[face[0] for face in faces],
            j=[face[1] for face in faces],
            k=[face[2] for face in faces],
            color=color,
            opacity=0.7,
            name=product['Product'],
            showscale=False
        ))
        
        # Add product label
        fig.add_trace(go.Scatter3d(
            x=[x + l/2],
            y=[y + w/2],
            z=[z + h + 0.5],
            mode='text',
            text=[f"{product['Product']}<br>({l}x{w}x{h} ft, {product['Weight']} lbs)"],
            showlegend=False,
            textfont=dict(size=8)
        ))
    
    fig.update_layout(
        title="3D Warehouse Storage Layout",
        scene=dict(
            xaxis_title="Length (ft)",
            yaxis_title="Width (ft)",
            zaxis_title="Height (ft)",
            xaxis=dict(range=[-1, storage_length + 1]),
            yaxis=dict(range=[-1, storage_width + 1]),
            zaxis=dict(range=[-1, storage_height + 1])
        ),
        height=600
    )
    
    return fig 