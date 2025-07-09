"""
dispatch_planner.py
True dispatch planning with route optimization, vehicle assignment, and delivery scheduling.
"""

import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Tuple
import pandas as pd

FUEL_PRICE_PER_LITER = 95  # INR per liter (Indian diesel price)

class DispatchPlanner:
    def __init__(self):
        self.vehicles = []
        self.drivers = []
        self.routes = []
        
    def add_vehicle(self, vehicle_id: str, capacity_weight: float, capacity_volume: float, 
                   fuel_efficiency: float, operating_cost_per_km: float):
        """Add a vehicle to the fleet."""
        self.vehicles.append({
            'id': vehicle_id,
            'capacity_weight': capacity_weight,
            'capacity_volume': capacity_volume,
            'fuel_efficiency': fuel_efficiency,
            'operating_cost_per_km': operating_cost_per_km,
            'current_location': (0, 0),  # Warehouse location
            'available': True
        })
    
    def add_driver(self, driver_id: str, name: str, max_hours: float, hourly_rate: float):
        """Add a driver to the team."""
        self.drivers.append({
            'id': driver_id,
            'name': name,
            'max_hours': max_hours,
            'hourly_rate': hourly_rate,
            'current_hours': 0,
            'available': True
        })
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points."""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def assign_delivery_locations(self, products: List[Dict]) -> List[Dict]:
        """Assign realistic delivery locations to products."""
        # Generate realistic delivery locations around the warehouse
        warehouse_location = (0, 0)
        delivery_locations = []
        
        for i, product in enumerate(products):
            # Generate random delivery location within reasonable range
            angle = random.uniform(0, 2 * np.pi)
            distance = random.uniform(5, 50)  # 5-50 miles from warehouse
            x = warehouse_location[0] + distance * np.cos(angle)
            y = warehouse_location[1] + distance * np.sin(angle)
            
            # Add delivery time window
            base_time = datetime.now() + timedelta(days=random.randint(1, 7))
            delivery_window_start = base_time.replace(hour=random.randint(8, 12), minute=0)
            delivery_window_end = delivery_window_start + timedelta(hours=2)
            
            product_with_location = product.copy()
            product_with_location.update({
                'delivery_location': (x, y),
                'delivery_window_start': delivery_window_start,
                'delivery_window_end': delivery_window_end,
                'service_time': random.uniform(0.25, 1.0),  # 15-60 minutes
                'priority_score': self._calculate_priority_score(product)
            })
            delivery_locations.append(product_with_location)
        
        return delivery_locations
    
    def _calculate_priority_score(self, product: Dict) -> float:
        """Calculate priority score based on product attributes."""
        score = 0
        
        # Priority level
        priority_map = {'High': 3, 'Medium': 2, 'Low': 1}
        score += priority_map.get(product.get('Priority', 'Medium'), 2)
        
        # Fragile items get higher priority
        if product.get('Fragile', False):
            score += 1
        
        # Weight-based priority (heavier items might need special handling)
        if product.get('Weight', 0) > 200:
            score += 0.5
        
        return score
    
    def set_vehicles(self, vehicles):
        self.vehicles = vehicles
    def set_drivers(self, drivers):
        self.drivers = drivers
    
    def optimize_routes(self, products_with_locations: List[Dict], constraints: Dict) -> List[Dict]:
        """
        Optimize delivery routes using a genetic algorithm approach.
        """
        if not self.vehicles:
            raise Exception("No vehicles available. Please add vehicles in the system settings.")
        if not self.drivers:
            raise Exception("No drivers available. Please add drivers in the system settings.")
        
        # Group products by delivery date
        products_by_date = self._group_by_delivery_date(products_with_locations)
        
        optimized_routes = []
        
        for delivery_date, products in products_by_date.items():
            # Sort products by priority and delivery window
            sorted_products = sorted(products, 
                                   key=lambda x: (x['priority_score'], x['delivery_window_start']),
                                   reverse=True)
            
            # Assign products to vehicles
            vehicle_assignments = self._assign_products_to_vehicles(sorted_products, constraints)
            
            # Optimize routes for each vehicle
            for vehicle_id, vehicle_products in vehicle_assignments.items():
                if vehicle_products:
                    route = self._optimize_single_route(vehicle_id, vehicle_products, constraints)
                    optimized_routes.append(route)
        
        return optimized_routes
    
    def _group_by_delivery_date(self, products: List[Dict]) -> Dict:
        """Group products by delivery date."""
        grouped = {}
        for product in products:
            date_key = product['delivery_window_start'].date()
            if date_key not in grouped:
                grouped[date_key] = []
            grouped[date_key].append(product)
        return grouped
    
    def _assign_products_to_vehicles(self, products: List[Dict], 
                                   constraints: Dict) -> Dict:
        """Assign products to vehicles based on capacity and constraints."""
        vehicle_assignments = {vehicle['id']: [] for vehicle in self.vehicles}
        vehicle_capacities = {vehicle['id']: {'weight': 0, 'volume': 0} for vehicle in self.vehicles}
        
        for product in products:
            assigned = False
            
            # Try to assign to available vehicle
            for vehicle in self.vehicles:
                if not vehicle['available']:
                    continue
                
                current_weight = vehicle_capacities[vehicle['id']]['weight']
                current_volume = vehicle_capacities[vehicle['id']]['volume']
                
                # Check if product fits
                if (current_weight + product['Weight'] <= vehicle['capacity_weight'] and
                    current_volume + product['Length'] * product['Width'] * product['Height'] <= vehicle['capacity_volume']):
                    
                    vehicle_assignments[vehicle['id']].append(product)
                    vehicle_capacities[vehicle['id']]['weight'] += product['Weight']
                    vehicle_capacities[vehicle['id']]['volume'] += product['Length'] * product['Width'] * product['Height']
                    assigned = True
                    break
            
            # If no vehicle available, create new route
            if not assigned:
                # Find vehicle with most capacity
                best_vehicle = max(self.vehicles, key=lambda v: v['capacity_weight'])
                vehicle_assignments[best_vehicle['id']].append(product)
        
        return vehicle_assignments
    
    def _optimize_single_route(self, vehicle_id: str, products: List[Dict], 
                             constraints: Dict) -> Dict:
        """Optimize route for a single vehicle using nearest neighbor algorithm."""
        if not products:
            return {}
        
        # Start from warehouse
        current_location = (0, 0)
        unvisited = products.copy()
        route = []
        total_distance = 0
        total_cost = 0
        
        # Find vehicle and driver
        vehicle = next(v for v in self.vehicles if v['id'] == vehicle_id)
        driver = random.choice([d for d in self.drivers if d['available']])
        
        # Build route using nearest neighbor
        while unvisited:
            # Find nearest unvisited location
            nearest = min(unvisited, 
                         key=lambda p: self.calculate_distance(current_location, p['delivery_location']))
            
            # Calculate distance to this location
            distance = self.calculate_distance(current_location, nearest['delivery_location'])
            total_distance += distance
            
            # Add to route
            route.append({
                'product': nearest,
                'location': nearest['delivery_location'],
                'distance_from_previous': distance,
                'estimated_arrival': self._calculate_arrival_time(nearest, total_distance),
                'service_time': nearest['service_time']
            })
            
            # Update current location
            current_location = nearest['delivery_location']
            unvisited.remove(nearest)
        
        # Calculate return trip to warehouse
        return_distance = self.calculate_distance(current_location, (0, 0))
        total_distance += return_distance
        
        # Calculate costs
        # Assume total_distance is in miles, convert to km
        total_distance_km = total_distance * 1.60934
        fuel_cost = (total_distance_km / vehicle['fuel_efficiency']) * FUEL_PRICE_PER_LITER
        operating_cost = total_distance_km * vehicle['operating_cost_per_km']
        driver_cost = (total_distance_km / 30) * driver['hourly_rate']  # Assume 30 mph average
        total_cost = fuel_cost + operating_cost + driver_cost
        
        return {
            'vehicle_id': vehicle_id,
            'driver_id': driver['id'],
            'driver_name': driver['name'],
            'route': route,
            'total_distance': round(total_distance, 2),
            'total_cost': round(total_cost, 2),
            'fuel_cost': round(fuel_cost, 2),
            'operating_cost': round(operating_cost, 2),
            'driver_cost': round(driver_cost, 2),
            'estimated_duration': round(total_distance / 30, 2),  # hours
            'products_delivered': len(products),
            'total_weight': sum(p['Weight'] for p in products),
            'total_volume': sum(p['Length'] * p['Width'] * p['Height'] for p in products),
            'total_distance_km': round(total_distance_km, 2),
            'average_cost_per_km': round(total_cost / total_distance_km, 2) if total_distance_km > 0 else 0,
            'average_cost_per_product': round(total_cost / len(products), 2) if len(products) > 0 else 0
        }
    
    def _calculate_arrival_time(self, product: Dict, total_distance: float) -> datetime:
        """Calculate estimated arrival time based on distance and current time."""
        # Assume average speed of 30 mph
        travel_time_hours = total_distance / 30
        travel_time = timedelta(hours=travel_time_hours)
        
        # Start from current time
        start_time = datetime.now()
        arrival_time = start_time + travel_time
        
        return arrival_time
    
    def get_route_summary(self, routes: List[Dict]) -> Dict:
        """Generate summary statistics for all routes."""
        if not routes:
            return {}
        
        total_distance_km = sum(route['total_distance'] for route in routes) * 1.60934
        total_cost = sum(route['total_cost'] for route in routes)
        total_products = sum(route['products_delivered'] for route in routes)
        total_weight = sum(route['total_weight'] for route in routes)
        total_volume = sum(route['total_volume'] for route in routes)
        
        return {
            'total_routes': len(routes),
            'total_distance': round(total_distance_km, 2),
            'total_cost': round(total_cost, 2),
            'total_products': total_products,
            'total_weight': round(total_weight, 2),
            'total_volume': round(total_volume, 2),
            'average_cost_per_km': round(total_cost / total_distance_km, 2) if total_distance_km > 0 else 0,
            'average_cost_per_product': round(total_cost / total_products, 2) if total_products > 0 else 0
        } 