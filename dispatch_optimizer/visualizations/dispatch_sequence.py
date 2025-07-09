"""
dispatch_sequence.py
Visualizes the dispatch order/sequence using plotly or matplotlib.
"""

import plotly.graph_objects as go

def plot_dispatch_sequence(dispatch_plan):
    """
    Visualize the dispatch sequence/order.
    Args:
        dispatch_plan (list of dict): Optimized dispatch plan with order info.
    Returns:
        plotly.graph_objs.Figure: Dispatch sequence figure.
    """
    products = [box['Product'] for box in dispatch_plan]
    order = [box.get('DispatchOrder', i+1) for i, box in enumerate(dispatch_plan)]
    fig = go.Figure(go.Bar(x=order, y=products, orientation='h', marker_color='lightsalmon'))
    fig.update_layout(title="Dispatch Sequence", xaxis_title="Dispatch Order", yaxis_title="Product")
    return fig 