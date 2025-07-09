"""
route_visualizer.py
Visualizes dispatch routes, vehicle assignments, and delivery sequences.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

def plot_route_map(routes: List[Dict], title: str = "Dispatch Routes") -> go.Figure:
    """
    Visualize dispatch routes on a map.
    Args:
        routes (list of dict): List of optimized routes
        title (str): Chart title
    Returns:
        plotly.graph_objs.Figure: Route map figure
    """
    if not routes:
        return go.Figure()
    
    fig = go.Figure()
    
    # Add warehouse location
    fig.add_trace(go.Scatter(
        x=[0], y=[0],
        mode='markers',
        marker=dict(size=20, color='red', symbol='star'),
        name='Warehouse',
        showlegend=True
    ))
    
    # Add routes
    for i, route in enumerate(routes):
        if not route or 'route' not in route:
            continue
            
        # Extract route coordinates
        route_coords: List[Tuple[float, float]] = [(0.0, 0.0)]  # Start at warehouse
        
        for route_item in route['route']:
            location = route_item.get('location', (0, 0))
            # Ensure location is a tuple of numbers
            if isinstance(location, (list, tuple)) and len(location) >= 2:
                try:
                    x = float(location[0])
                    y = float(location[1])
                    route_coords.append((x, y))
                except (ValueError, TypeError):
                    # Skip invalid coordinates
                    continue
            else:
                # Skip invalid location format
                continue
        
        # Add return to warehouse
        route_coords.append((0, 0))
        
        if len(route_coords) > 2:  # At least warehouse -> delivery -> warehouse
            x_coords = [coord[0] for coord in route_coords]
            y_coords = [coord[1] for coord in route_coords]
            
            fig.add_trace(go.Scatter(
                x=x_coords,
                y=y_coords,
                mode='lines+markers',
                name=f"Route {i+1}: {route.get('vehicle_id', 'Unknown')}",
                line=dict(width=2),
                marker=dict(size=8),
                hovertemplate=f"<b>Route {i+1}</b><br>" +
                             f"Vehicle: {route.get('vehicle_id', 'Unknown')}<br>" +
                             f"Driver: {route.get('driver_name', 'Unknown')}<br>" +
                             f"Distance: {route.get('total_distance', 0) * 1.60934:.1f} km<br>" +
                             f"Cost: ₹{route.get('total_cost', 0):.2f}<br>" +
                             f"Products: {route.get('products_delivered', 0)}<br>" +
                             "<extra></extra>"
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title="X Coordinate (km)",
        yaxis_title="Y Coordinate (km)",
        height=600,
        showlegend=True
    )
    
    return fig

def plot_route_timeline(routes: List[Dict]) -> go.Figure:
    """
    Visualize delivery timeline for all routes.
    Args:
        routes (list of dict): List of optimized routes
    Returns:
        plotly.graph_objs.Figure: Timeline figure
    """
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    for i, route in enumerate(routes):
        if not route or 'route' not in route:
            continue
            
        color = colors[i % len(colors)]
        vehicle_id = route.get('vehicle_id', f'Vehicle {i+1}')
        
        # Create timeline data
        current_time = datetime.now()
        timeline_data = []
        
        # Add warehouse departure
        timeline_data.append({
            'time': current_time,
            'location': 'Warehouse',
            'action': 'Departure',
            'product': 'Start Route'
        })
        
        # Add delivery stops
        for j, route_item in enumerate(route['route']):
            product = route_item.get('product', {})
            estimated_arrival = route_item.get('estimated_arrival', current_time + timedelta(hours=j+1))
            
            timeline_data.append({
                'time': estimated_arrival,
                'location': f"Delivery {j+1}",
                'action': 'Delivery',
                'product': product.get('Product', f'Product {j+1}')
            })
        
        # Add warehouse return
        total_duration = route.get('estimated_duration', 0)
        return_time = current_time + timedelta(hours=total_duration)
        timeline_data.append({
            'time': return_time,
            'location': 'Warehouse',
            'action': 'Return',
            'product': 'End Route'
        })
        
        # Plot timeline
        times = [item['time'] for item in timeline_data]
        locations = [item['location'] for item in timeline_data]
        
        fig.add_trace(go.Scatter(
            x=times,
            y=[vehicle_id] * len(times),
            mode='lines+markers',
            name=vehicle_id,
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            hovertemplate='<b>%{y}</b><br>Time: %{x}<br>Location: %{text}<extra></extra>',
            text=locations
        ))
    
    fig.update_layout(
        title="Delivery Timeline",
        xaxis_title="Time",
        yaxis_title="Vehicle",
        showlegend=True,
        height=400,
        hovermode='closest'
    )
    
    return fig

def plot_vehicle_utilization(routes: List[Dict]) -> go.Figure:
    """
    Visualize vehicle utilization metrics.
    Args:
        routes (list of dict): List of optimized routes
    Returns:
        plotly.graph_objs.Figure: Utilization figure
    """
    if not routes:
        return go.Figure()
    
    # Extract vehicle data
    vehicle_data = []
    for route in routes:
        if not route:
            continue
            
        vehicle_data.append({
            'vehicle_id': route.get('vehicle_id', 'Unknown'),
            'driver_name': route.get('driver_name', 'Unknown'),
            'total_distance': route.get('total_distance', 0),
            'total_cost': route.get('total_cost', 0),
            'products_delivered': route.get('products_delivered', 0),
            'total_weight': route.get('total_weight', 0),
            'total_volume': route.get('total_volume', 0),
            'estimated_duration': route.get('estimated_duration', 0)
        })
    
    if not vehicle_data:
        return go.Figure()
    
    df = pd.DataFrame(vehicle_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distance per Vehicle', 'Cost per Vehicle', 'Products per Vehicle', 'Weight per Vehicle'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Distance per vehicle
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['total_distance'] * 1.60934, name='Distance (km)'),
        row=1, col=1
    )
    
    # Cost per vehicle
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['total_cost'], name='Cost (₹)'),
        row=1, col=2
    )
    
    # Products per vehicle
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['products_delivered'], name='Products'),
        row=2, col=1
    )
    
    # Weight per vehicle
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['total_weight'], name='Weight (lbs)'),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Vehicle Utilization Metrics",
        height=600,
        showlegend=False
    )
    
    return fig

def plot_cost_breakdown(routes: List[Dict]) -> go.Figure:
    """
    Visualize cost breakdown for all routes.
    Args:
        routes (list of dict): List of optimized routes
    Returns:
        plotly.graph_objs.Figure: Cost breakdown figure
    """
    if not routes:
        return go.Figure()
    
    # Calculate total costs
    total_fuel_cost = sum(route.get('fuel_cost', 0) for route in routes)
    total_operating_cost = sum(route.get('operating_cost', 0) for route in routes)
    total_driver_cost = sum(route.get('driver_cost', 0) for route in routes)
    total_cost = sum(route.get('total_cost', 0) for route in routes)
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=['Fuel Cost', 'Operating Cost', 'Driver Cost'],
        values=[total_fuel_cost, total_operating_cost, total_driver_cost],
        hole=0.3
    )])
    
    fig.update_layout(
        title=f"Cost Breakdown - Total: ₹{total_cost:.2f}",
        height=400
    )
    
    return fig

def plot_delivery_heatmap(routes: List[Dict]) -> go.Figure:
    """
    Create a heatmap showing delivery density by location.
    Args:
        routes (list of dict): List of optimized routes
    Returns:
        plotly.graph_objs.Figure: Heatmap figure
    """
    if not routes:
        return go.Figure()
    
    # Collect all delivery locations
    all_locations = []
    for route in routes:
        if not route or 'route' not in route:
            continue
            
        for route_item in route['route']:
            location = route_item.get('location', (0, 0))
            # Ensure location is a tuple of numbers
            if isinstance(location, (list, tuple)) and len(location) >= 2:
                try:
                    x = float(location[0])
                    y = float(location[1])
                    all_locations.append((x, y))
                except (ValueError, TypeError):
                    # Skip invalid coordinates
                    continue
            else:
                # Skip invalid location format
                continue
    
    if not all_locations:
        return go.Figure()
    
    # Create grid for heatmap
    x_coords = [loc[0] for loc in all_locations]
    y_coords = [loc[1] for loc in all_locations]
    
    # Ensure we have valid numeric data
    if not x_coords or not y_coords:
        return go.Figure()
    
    try:
        # Create 2D histogram
        x_bins = np.linspace(min(x_coords), max(x_coords), 20)
        y_bins = np.linspace(min(y_coords), max(y_coords), 20)
        
        heatmap, x_edges, y_edges = np.histogram2d(x_coords, y_coords, bins=[x_bins, y_bins])
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap.T,
            x=x_edges[:-1],
            y=y_edges[:-1],
            colorscale='Viridis',
            colorbar=dict(title="Delivery Count")
        ))
        
        # Add warehouse location
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Warehouse',
            showlegend=True
        ))
        
        fig.update_layout(
            title="Delivery Density Heatmap",
            xaxis_title="X Coordinate (km)",
            yaxis_title="Y Coordinate (km)",
            height=500
        )
        
        return fig
        
    except (ValueError, TypeError) as e:
        # Return empty figure if there's an error with the data
        print(f"Warning: Could not create delivery heatmap due to data issues: {e}")
        return go.Figure()

def plot_route_efficiency(routes: List[Dict]) -> go.Figure:
    """
    Visualize route efficiency metrics.
    Args:
        routes (list of dict): List of optimized routes
    Returns:
        plotly.graph_objs.Figure: Efficiency figure
    """
    if not routes:
        return go.Figure()
    
    # Calculate efficiency metrics
    efficiency_data = []
    for route in routes:
        if not route:
            continue
            
        distance = route.get('total_distance', 0)
        cost = route.get('total_cost', 0)
        products = route.get('products_delivered', 0)
        weight = route.get('total_weight', 0)
        
        efficiency_data.append({
            'vehicle_id': route.get('vehicle_id', 'Unknown'),
            'cost_per_km': cost / (distance * 1.60934) if distance > 0 else 0,
            'products_per_km': products / (distance * 1.60934) if distance > 0 else 0,
            'weight_per_km': weight / (distance * 1.60934) if distance > 0 else 0,
            'cost_per_product': cost / products if products > 0 else 0
        })
    
    if not efficiency_data:
        return go.Figure()
    
    df = pd.DataFrame(efficiency_data)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Cost per Km', 'Products per Km', 'Weight per Km', 'Cost per Product'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Cost per km
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['cost_per_km'], name='Cost/Km (₹)'),
        row=1, col=1
    )
    
    # Products per km
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['products_per_km'], name='Products/Km'),
        row=1, col=2
    )
    
    # Weight per km
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['weight_per_km'], name='Weight/Km (kg)'),
        row=2, col=1
    )
    
    # Cost per product
    fig.add_trace(
        go.Bar(x=df['vehicle_id'], y=df['cost_per_product'], name='Cost/Product (₹)'),
        row=2, col=2
    )
    
    fig.update_layout(
        title="Route Efficiency Metrics",
        height=600,
        showlegend=False
    )
    
    return fig 