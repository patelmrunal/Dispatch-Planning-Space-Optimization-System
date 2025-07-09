"""
dynamic_optimizer.py
Dynamic real-time optimization for live goods movement and continuous optimization.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Callable
import queue
import json
import sqlite3
from dispatch_optimizer.agents.optimizer import optimize_dispatch
from dispatch_optimizer.agents.dispatch_planner import DispatchPlanner

class DynamicOptimizer:
    def __init__(self, db_path="dynamic_optimization.db"):
        self.db_path = db_path
        self.event_queue = queue.Queue()
        self.optimization_thread = None
        self.is_running = False
        self.current_state = {}
        self.optimization_callbacks = []
        self.dispatch_planner = DispatchPlanner()
        self.last_optimization = None
        self.optimization_interval = 300  # 5 minutes default
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database for tracking dynamic changes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS goods_movement (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                movement_type TEXT,
                product_id TEXT,
                product_name TEXT,
                quantity INTEGER,
                location_from TEXT,
                location_to TEXT,
                weight REAL,
                volume REAL,
                priority TEXT,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                optimization_type TEXT,
                products_count INTEGER,
                routes_count INTEGER,
                total_cost REAL,
                total_distance REAL,
                optimization_duration REAL,
                status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS real_time_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_products INTEGER,
                total_weight REAL,
                total_volume REAL,
                active_routes INTEGER,
                available_vehicles INTEGER,
                utilization_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_dynamic_optimization(self):
        """Start the dynamic optimization thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop)
        self.optimization_thread.daemon = True
        self.optimization_thread.start()
        print("🔄 Dynamic optimization started")
    
    def stop_dynamic_optimization(self):
        """Stop the dynamic optimization thread."""
        self.is_running = False
        if self.optimization_thread:
            self.optimization_thread.join()
        print("⏹️ Dynamic optimization stopped")
    
    def _optimization_loop(self):
        """Main optimization loop that runs continuously."""
        while self.is_running:
            try:
                # Process any pending events
                self._process_events()
                
                # Check if optimization is needed
                if self._should_optimize():
                    self._perform_optimization()
                
                # Update real-time metrics
                self._update_metrics()
                
                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in optimization loop: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _process_events(self):
        """Process pending events in the queue."""
        while not self.event_queue.empty():
            try:
                event = self.event_queue.get_nowait()
                self._handle_event(event)
            except queue.Empty:
                break
    
    def _handle_event(self, event: Dict):
        """Handle a single event."""
        event_type = event.get('type')
        
        if event_type == 'goods_in':
            self._handle_goods_in(event)
        elif event_type == 'goods_out':
            self._handle_goods_out(event)
        elif event_type == 'location_change':
            self._handle_location_change(event)
        elif event_type == 'priority_change':
            self._handle_priority_change(event)
        elif event_type == 'vehicle_status':
            self._handle_vehicle_status(event)
        elif event_type == 'driver_status':
            self._handle_driver_status(event)
        
        # Log the event
        self._log_movement_event(event)
    
    def _handle_goods_in(self, event: Dict):
        """Handle goods coming into the system."""
        product = event.get('product', {})
        location = event.get('location', 'Receiving')
        
        # Add to current state
        product_id = product.get('Product', f"product_{len(self.current_state)}")
        self.current_state[product_id] = {
            'product': product,
            'location': location,
            'timestamp': datetime.now(),
            'status': 'available'
        }
        
        print(f"📦 Goods in: {product.get('Product', 'Unknown')} at {location}")
    
    def _handle_goods_out(self, event: Dict):
        """Handle goods leaving the system."""
        product_id = event.get('product_id')
        destination = event.get('destination', 'Unknown')
        
        if product_id in self.current_state:
            # Mark as dispatched
            self.current_state[product_id]['status'] = 'dispatched'
            self.current_state[product_id]['destination'] = destination
            self.current_state[product_id]['dispatch_time'] = datetime.now()
            
            print(f"🚚 Goods out: {product_id} to {destination}")
    
    def _handle_location_change(self, event: Dict):
        """Handle goods moving between locations."""
        product_id = event.get('product_id')
        new_location = event.get('new_location')
        
        if product_id in self.current_state:
            old_location = self.current_state[product_id]['location']
            self.current_state[product_id]['location'] = new_location
            self.current_state[product_id]['last_move'] = datetime.now()
            
            print(f"🔄 Location change: {product_id} from {old_location} to {new_location}")
    
    def _handle_priority_change(self, event: Dict):
        """Handle priority changes for goods."""
        product_id = event.get('product_id')
        new_priority = event.get('new_priority')
        
        if product_id in self.current_state:
            self.current_state[product_id]['product']['Priority'] = new_priority
            self.current_state[product_id]['priority_change_time'] = datetime.now()
            
            print(f"⚡ Priority change: {product_id} to {new_priority}")
    
    def _handle_vehicle_status(self, event: Dict):
        """Handle vehicle status changes."""
        vehicle_id = event.get('vehicle_id')
        status = event.get('status')
        
        # Update vehicle status in dispatch planner
        for vehicle in self.dispatch_planner.vehicles:
            if vehicle['id'] == vehicle_id:
                vehicle['available'] = (status == 'available')
                vehicle['last_status_update'] = datetime.now()
                break
        
        print(f"🚛 Vehicle status: {vehicle_id} is {status}")
    
    def _handle_driver_status(self, event: Dict):
        """Handle driver status changes."""
        driver_id = event.get('driver_id')
        status = event.get('status')
        hours_worked = event.get('hours_worked', 0)
        
        # Update driver status in dispatch planner
        for driver in self.dispatch_planner.drivers:
            if driver['id'] == driver_id:
                driver['available'] = (status == 'available')
                driver['current_hours'] = hours_worked
                driver['last_status_update'] = datetime.now()
                break
        
        print(f"👤 Driver status: {driver_id} is {status} ({hours_worked} hours)")
    
    def _should_optimize(self) -> bool:
        """Determine if optimization should be performed."""
        if not self.last_optimization:
            return True
        
        # Check if enough time has passed
        time_since_last = datetime.now() - self.last_optimization
        if time_since_last.total_seconds() < self.optimization_interval:
            return False
        
        # Check if there are significant changes
        available_products = [p for p in self.current_state.values() if p['status'] == 'available']
        if len(available_products) < 5:
            return False
        
        return True
    
    def _perform_optimization(self):
        """Perform the actual optimization."""
        start_time = datetime.now()
        
        try:
            # Get available products
            available_products = [p['product'] for p in self.current_state.values() 
                                if p['status'] == 'available']
            
            if not available_products:
                return
            
            # Create constraints
            constraints = {
                'max_storage_weight': 5000,
                'fragile_on_top': True,
                'priority_first': True,
                'storage_length': 40,
                'storage_width': 20,
                'storage_height': 15
            }
            
            # Perform storage optimization
            storage_plan = optimize_dispatch(available_products, constraints)
            
            # Perform dispatch planning
            products_with_locations = self.dispatch_planner.assign_delivery_locations(available_products)
            dispatch_routes = self.dispatch_planner.optimize_routes(products_with_locations, constraints)
            
            # Calculate metrics
            route_summary = self.dispatch_planner.get_route_summary(dispatch_routes)
            
            # Log optimization
            self._log_optimization({
                'type': 'full_optimization',
                'products_count': len(available_products),
                'routes_count': len(dispatch_routes),
                'total_cost': route_summary.get('total_cost', 0),
                'total_distance': route_summary.get('total_distance', 0),
                'duration': (datetime.now() - start_time).total_seconds(),
                'status': 'success'
            })
            
            # Update current state with optimization results
            self._update_state_with_optimization(storage_plan, dispatch_routes)
            
            # Notify callbacks
            self._notify_optimization_callbacks({
                'storage_plan': storage_plan,
                'dispatch_routes': dispatch_routes,
                'summary': route_summary,
                'timestamp': datetime.now()
            })
            
            self.last_optimization = datetime.now()
            print(f"✅ Optimization completed: {len(dispatch_routes)} routes, ${route_summary.get('total_cost', 0):.2f} total cost")
            
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            self._log_optimization({
                'type': 'full_optimization',
                'products_count': 0,
                'routes_count': 0,
                'total_cost': 0,
                'total_distance': 0,
                'duration': (datetime.now() - start_time).total_seconds(),
                'status': 'failed'
            })
    
    def _update_state_with_optimization(self, storage_plan: List[Dict], dispatch_routes: List[Dict]):
        """Update current state with optimization results."""
        # Update storage assignments
        for i, product_data in enumerate(storage_plan):
            product_id = product_data.get('Product', f"product_{i}")
            if product_id in self.current_state:
                self.current_state[product_id]['storage_area'] = product_data.get('Storage Area #', 1)
                self.current_state[product_id]['storage_order'] = product_data.get('StorageOrder', i + 1)
        
        # Update dispatch assignments
        for route in dispatch_routes:
            for route_item in route.get('route', []):
                product = route_item.get('product', {})
                product_id = product.get('Product', 'unknown')
                if product_id in self.current_state:
                    self.current_state[product_id]['assigned_vehicle'] = route.get('vehicle_id')
                    self.current_state[product_id]['assigned_driver'] = route.get('driver_name')
                    self.current_state[product_id]['estimated_arrival'] = route_item.get('estimated_arrival')
    
    def _update_metrics(self):
        """Update real-time metrics."""
        available_products = [p for p in self.current_state.values() if p['status'] == 'available']
        total_weight = sum(p['product'].get('Weight', 0) for p in available_products)
        total_volume = sum(p['product'].get('Length', 0) * p['product'].get('Width', 0) * p['product'].get('Height', 0) 
                          for p in available_products)
        
        available_vehicles = sum(1 for v in self.dispatch_planner.vehicles if v['available'])
        
        metrics = {
            'total_products': len(available_products),
            'total_weight': total_weight,
            'total_volume': total_volume,
            'active_routes': len([p for p in self.current_state.values() if p.get('assigned_vehicle')]),
            'available_vehicles': available_vehicles,
            'utilization_rate': len(available_products) / max(len(self.current_state), 1)
        }
        
        self._log_metrics(metrics)
    
    def add_optimization_callback(self, callback: Callable):
        """Add a callback function to be called when optimization completes."""
        self.optimization_callbacks.append(callback)
    
    def _notify_optimization_callbacks(self, optimization_result: Dict):
        """Notify all registered callbacks with optimization results."""
        for callback in self.optimization_callbacks:
            try:
                callback(optimization_result)
            except Exception as e:
                print(f"Error in optimization callback: {e}")
    
    def add_event(self, event: Dict):
        """Add an event to the processing queue."""
        self.event_queue.put(event)
    
    def get_current_state(self) -> Dict:
        """Get the current state of all goods."""
        return self.current_state.copy()
    
    def get_optimization_status(self) -> Dict:
        """Get the current optimization status."""
        return {
            'is_running': self.is_running,
            'last_optimization': self.last_optimization,
            'optimization_interval': self.optimization_interval,
            'pending_events': self.event_queue.qsize(),
            'total_products': len(self.current_state),
            'available_products': len([p for p in self.current_state.values() if p['status'] == 'available'])
        }
    
    def reset_state(self):
        """Reset the dynamic optimizer's state (clear all products and events)."""
        self.current_state.clear()
        while not self.event_queue.empty():
            try:
                self.event_queue.get_nowait()
            except Exception:
                break
    
    def _log_movement_event(self, event: Dict):
        """Log a movement event to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO goods_movement 
            (movement_type, product_id, product_name, quantity, location_from, location_to, weight, volume, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.get('type'),
            event.get('product_id', event.get('product', {}).get('Product', 'unknown')),
            event.get('product', {}).get('Product', 'unknown'),
            event.get('quantity', 1),
            event.get('location_from', ''),
            event.get('location_to', event.get('location', '')),
            event.get('product', {}).get('Weight', 0),
            event.get('product', {}).get('Length', 0) * event.get('product', {}).get('Width', 0) * event.get('product', {}).get('Height', 0),
            event.get('product', {}).get('Priority', 'Medium'),
            event.get('status', 'completed')
        ))
        
        conn.commit()
        conn.close()
    
    def _log_optimization(self, optimization_data: Dict):
        """Log optimization results to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO optimization_history 
            (optimization_type, products_count, routes_count, total_cost, total_distance, optimization_duration, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            optimization_data.get('type'),
            optimization_data.get('products_count'),
            optimization_data.get('routes_count'),
            optimization_data.get('total_cost'),
            optimization_data.get('total_distance'),
            optimization_data.get('duration'),
            optimization_data.get('status')
        ))
        
        conn.commit()
        conn.close()
    
    def _log_metrics(self, metrics: Dict):
        """Log real-time metrics to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO real_time_metrics 
            (total_products, total_weight, total_volume, active_routes, available_vehicles, utilization_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            metrics.get('total_products'),
            metrics.get('total_weight'),
            metrics.get('total_volume'),
            metrics.get('active_routes'),
            metrics.get('available_vehicles'),
            metrics.get('utilization_rate')
        ))
        
        conn.commit()
        conn.close() 