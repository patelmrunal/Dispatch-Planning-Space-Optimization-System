"""
sample_data_generator.py
Generates sample product data for training the AI model with various warehouse storage scenarios.
"""

import pandas as pd
import random
import json
from datetime import datetime, timedelta

def generate_product_variations(base_product, variations=100):
    """
    Generate multiple variations of a base product for better training data.
    """
    products = []
    
    for i in range(variations):
        # Create variations in weight, dimensions, and other properties
        weight_variation = random.uniform(0.7, 1.3)
        length_variation = random.uniform(0.8, 1.2)
        width_variation = random.uniform(0.8, 1.2)
        height_variation = random.uniform(0.8, 1.2)
        
        # Vary the fragility and priority
        fragile = random.choice([True, False]) if base_product.get('Fragile') else False
        priority = random.choice(['High', 'Medium', 'Low'])
        
        # Vary warehouse zones
        warehouse_zones = ["ZoneA", "ZoneB", "ZoneC", "ZoneD", "ZoneE", "ZoneF", "ZoneG", "ZoneH", "ZoneI", "ZoneJ",
                          "Rack1", "Rack2", "Rack3", "Rack4", "Rack5", "Rack6", "Rack7", "Rack8", "Rack9", "Rack10",
                          "Aisle1", "Aisle2", "Aisle3", "Aisle4", "Aisle5", "Aisle6", "Aisle7", "Aisle8", "Aisle9", "Aisle10",
                          "SectionA", "SectionB", "SectionC", "SectionD", "SectionE", "SectionF", "SectionG", "SectionH",
                          "Floor1", "Floor2", "Floor3", "Floor4", "Floor5",
                          "ColdStorage", "DryStorage", "HazardousStorage", "BulkStorage", "SmallItemStorage",
                          "PalletArea1", "PalletArea2", "PalletArea3", "PalletArea4", "PalletArea5",
                          "ShelfArea1", "ShelfArea2", "ShelfArea3", "ShelfArea4", "ShelfArea5",
                          "LoadingDock1", "LoadingDock2", "LoadingDock3", "LoadingDock4", "LoadingDock5",
                          "ReceivingArea", "ShippingArea", "QualityControl", "ReturnsArea", "OverflowStorage",
                          "Mezzanine1", "Mezzanine2", "Mezzanine3", "Mezzanine4", "Mezzanine5",
                          "Basement1", "Basement2", "Basement3", "Basement4", "Basement5",
                          "HighBay1", "HighBay2", "HighBay3", "HighBay4", "HighBay5",
                          "AutomatedStorage1", "AutomatedStorage2", "AutomatedStorage3", "AutomatedStorage4", "AutomatedStorage5",
                          "ManualStorage1", "ManualStorage2", "ManualStorage3", "ManualStorage4", "ManualStorage5",
                          "FastMoving", "SlowMoving", "Seasonal", "BulkItems", "FragileItems",
                          "HeavyItems", "LightItems", "LargeItems", "SmallItems", "MediumItems",
                          "Priority1", "Priority2", "Priority3", "Priority4", "Priority5",
                          "ExpressLane", "StandardLane", "EconomyLane", "PremiumLane", "OverflowLane"]
        
        destination = random.choice(warehouse_zones)
        
        # Vary dispatch dates
        base_date = datetime.strptime(base_product['DispatchDate'], '%Y-%m-%d')
        days_offset = random.randint(-30, 30)
        new_date = base_date + timedelta(days=days_offset)
        
        product_variation = {
            "Product": f"{base_product['Product']} - Variant {i+1:03d}",
            "Weight": round(base_product['Weight'] * weight_variation, 1),
            "Length": round(base_product['Length'] * length_variation, 1),
            "Width": round(base_product['Width'] * width_variation, 1),
            "Height": round(base_product['Height'] * height_variation, 1),
            "Fragile": fragile,
            "Destination": destination,
            "Priority": priority,
            "DispatchDate": new_date.strftime('%Y-%m-%d')
        }
        
        products.append(product_variation)
    
    return products

def generate_sample_scenarios():
    """
    Generate 100 different realistic warehouse storage scenarios for training.
    Returns:
        list: List of dictionaries with scenario name and data
    """
    scenarios = []
    
    # Original 20 scenarios (1-20) - now with 100 variations each
    # Scenario 1: Small Electronics (Fragile, Light)
    electronics_base = [
        {"Product": "Laptop", "Weight": 5.5, "Length": 1.1, "Width": 0.8, "Height": 0.1, "Fragile": True, "Destination": "ZoneA", "Priority": "High", "DispatchDate": "2025-01-15"},
        {"Product": "Smartphone", "Weight": 0.4, "Length": 0.5, "Width": 0.3, "Height": 0.03, "Fragile": True, "Destination": "ZoneB", "Priority": "High", "DispatchDate": "2025-01-16"},
        {"Product": "Tablet", "Weight": 1.1, "Length": 0.8, "Width": 0.6, "Height": 0.07, "Fragile": True, "Destination": "ZoneC", "Priority": "Medium", "DispatchDate": "2025-01-17"},
        {"Product": "Headphones", "Weight": 0.7, "Length": 0.7, "Width": 0.5, "Height": 0.2, "Fragile": True, "Destination": "ZoneD", "Priority": "Low", "DispatchDate": "2025-01-18"},
        {"Product": "Camera", "Weight": 2.6, "Length": 0.4, "Width": 0.3, "Height": 0.2, "Fragile": True, "Destination": "ZoneE", "Priority": "High", "DispatchDate": "2025-01-19"}
    ]
    
    electronics_data = []
    for base_product in electronics_base:
        electronics_data.extend(generate_product_variations(base_product, 20))  # 20 variations each = 100 total
    
    scenarios.append({"name": "Small Electronics", "data": electronics_data})
    
    # Scenario 2: Heavy Machinery Parts
    machinery_base = [
        {"Product": "Engine Block", "Weight": 330, "Length": 2.6, "Width": 2.0, "Height": 1.3, "Fragile": False, "Destination": "HeavyItems", "Priority": "High", "DispatchDate": "2025-01-20"},
        {"Product": "Gear Box", "Weight": 165, "Length": 1.6, "Width": 1.3, "Height": 1.0, "Fragile": False, "Destination": "BulkStorage", "Priority": "Medium", "DispatchDate": "2025-01-21"},
        {"Product": "Hydraulic Pump", "Weight": 99, "Length": 1.1, "Width": 0.8, "Height": 0.7, "Fragile": False, "Destination": "PalletArea1", "Priority": "Low", "DispatchDate": "2025-01-22"},
        {"Product": "Turbine", "Weight": 440, "Length": 3.3, "Width": 2.6, "Height": 2.0, "Fragile": True, "Destination": "HazardousStorage", "Priority": "High", "DispatchDate": "2025-01-23"},
        {"Product": "Compressor", "Weight": 264, "Length": 2.3, "Width": 1.6, "Height": 1.5, "Fragile": False, "Destination": "BulkItems", "Priority": "Medium", "DispatchDate": "2025-01-24"}
    ]
    
    machinery_data = []
    for base_product in machinery_base:
        machinery_data.extend(generate_product_variations(base_product, 20))
    
    scenarios.append({"name": "Heavy Machinery", "data": machinery_data})
    
    # Continue with more scenarios...
    # [Adding scenarios 3-100 with diverse industries and 100 variations each]
    
    # For the remaining scenarios (3-100), I'll create varied data
    industries = [
        "Textiles", "Food Processing", "Plastic Products", "Glass Items", 
        "Ceramic Products", "Leather Goods", "Wood Products", "Metal Fabrication",
        "Electronics Assembly", "Chemical Processing", "Biotechnology", "Nanotechnology",
        "Robotics", "Artificial Intelligence", "Blockchain", "Cloud Computing",
        "Internet of Things", "Virtual Reality", "Augmented Reality", "3D Printing",
        "Drones", "Electric Vehicles", "Hybrid Vehicles", "Fuel Cells",
        "Nuclear Energy", "Geothermal Energy", "Biomass Energy", "Hydroelectric",
        "Tidal Energy", "Wave Energy", "Space Technology", "Satellite Technology",
        "Missile Technology", "Aircraft Technology", "Shipbuilding", "Railway Technology",
        "Metro Technology", "Highway Technology", "Bridge Technology", "Tunnel Technology",
        "Building Technology", "Smart Cities", "Green Buildings", "Sustainable Technology",
        "Waste Management", "Water Treatment", "Air Purification", "Soil Remediation",
        "Climate Technology", "Weather Technology", "Ocean Technology", "Forest Technology",
        "Wildlife Technology", "Agriculture Technology", "Horticulture Technology", "Floriculture Technology",
        "Aquaculture Technology", "Poultry Technology", "Dairy Technology", "Meat Processing",
        "Bakery Technology", "Confectionery Technology", "Beverage Technology", "Tobacco Technology",
        "Pharmaceutical Technology", "Medical Technology", "Dental Technology", "Veterinary Technology",
        "Optical Technology", "Acoustic Technology", "Thermal Technology", "Cryogenic Technology",
        "Magnetic Technology", "Electrical Technology", "Electronic Technology", "Digital Technology",
        "Analog Technology", "Mixed Signal Technology", "RF Technology", "Microwave Technology",
        "Optical Fiber Technology", "Wireless Technology", "Mobile Technology", "Computer Technology",
        "Software Technology", "Hardware Technology", "Network Technology", "Security Technology",
        "Database Technology", "Web Technology", "Mobile App Technology", "Game Technology",
        "Animation Technology", "Graphics Technology", "Audio Technology", "Video Technology",
        "Streaming Technology", "Social Media Technology", "E-commerce Technology", "Fintech Technology",
        "Edtech Technology", "Healthtech Technology", "Agritech Technology", "Cleantech Technology"
    ]
    
    for i, industry in enumerate(industries, 3):
        # Generate 100 varied products for each industry
        industry_data = []
        
        for j in range(100):
            # Generate varied data for each product
            base_weight = random.uniform(1, 660)  # 1-660 lbs
            base_length = random.uniform(0.3, 13)  # 0.3-13 ft
            base_width = random.uniform(0.3, 6.5)  # 0.3-6.5 ft
            base_height = random.uniform(0.2, 5)  # 0.2-5 ft
            
            # Create product variations
            weight_variation = random.uniform(0.6, 1.4)
            length_variation = random.uniform(0.7, 1.3)
            width_variation = random.uniform(0.7, 1.3)
            height_variation = random.uniform(0.7, 1.3)
            
            product = {
                "Product": f"{industry} Product {j+1:03d}",
                "Weight": round(base_weight * weight_variation, 1),
                "Length": round(base_length * length_variation, 1),
                "Width": round(base_width * width_variation, 1),
                "Height": round(base_height * height_variation, 1),
                "Fragile": random.choice([True, False]),
                "Destination": random.choice(["ZoneA", "ZoneB", "ZoneC", "ZoneD", "ZoneE", "ZoneF", "ZoneG", "ZoneH", "ZoneI", "ZoneJ",
                                            "Rack1", "Rack2", "Rack3", "Rack4", "Rack5", "Rack6", "Rack7", "Rack8", "Rack9", "Rack10",
                                            "Aisle1", "Aisle2", "Aisle3", "Aisle4", "Aisle5", "Aisle6", "Aisle7", "Aisle8", "Aisle9", "Aisle10",
                                            "SectionA", "SectionB", "SectionC", "SectionD", "SectionE", "SectionF", "SectionG", "SectionH",
                                            "Floor1", "Floor2", "Floor3", "Floor4", "Floor5",
                                            "ColdStorage", "DryStorage", "HazardousStorage", "BulkStorage", "SmallItemStorage",
                                            "PalletArea1", "PalletArea2", "PalletArea3", "PalletArea4", "PalletArea5",
                                            "ShelfArea1", "ShelfArea2", "ShelfArea3", "ShelfArea4", "ShelfArea5",
                                            "LoadingDock1", "LoadingDock2", "LoadingDock3", "LoadingDock4", "LoadingDock5",
                                            "ReceivingArea", "ShippingArea", "QualityControl", "ReturnsArea", "OverflowStorage",
                                            "Mezzanine1", "Mezzanine2", "Mezzanine3", "Mezzanine4", "Mezzanine5",
                                            "Basement1", "Basement2", "Basement3", "Basement4", "Basement5",
                                            "HighBay1", "HighBay2", "HighBay3", "HighBay4", "HighBay5",
                                            "AutomatedStorage1", "AutomatedStorage2", "AutomatedStorage3", "AutomatedStorage4", "AutomatedStorage5",
                                            "ManualStorage1", "ManualStorage2", "ManualStorage3", "ManualStorage4", "ManualStorage5",
                                            "FastMoving", "SlowMoving", "Seasonal", "BulkItems", "FragileItems",
                                            "HeavyItems", "LightItems", "LargeItems", "SmallItems", "MediumItems",
                                            "Priority1", "Priority2", "Priority3", "Priority4", "Priority5",
                                            "ExpressLane", "StandardLane", "EconomyLane", "PremiumLane", "OverflowLane"]),
                "Priority": random.choice(["High", "Medium", "Low"]),
                "DispatchDate": f"2025-{5 + (i//30):02d}-{(j%30) + 1:02d}"
            }
            
            industry_data.append(product)
        
        scenarios.append({"name": industry, "data": industry_data})
    
    return scenarios

def save_sample_data():
    """
    Save all sample scenarios to CSV files for easy access.
    """
    scenarios = generate_sample_scenarios()
    
    for i, scenario in enumerate(scenarios, 1):
        df = pd.DataFrame(scenario['data'])
        filename = f"data/sample_scenario_{i:03d}_{scenario['name'].replace(' ', '_').replace('&', 'and').lower()}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved: {filename} with {len(scenario['data'])} products")
    
    # Create a master file with all scenarios
    all_data = []
    for scenario in scenarios:
        for item in scenario['data']:
            item['Scenario'] = scenario['name']
            all_data.append(item)
    
    master_df = pd.DataFrame(all_data)
    master_df.to_csv("data/all_sample_data.csv", index=False)
    print("Saved: data/all_sample_data.csv")
    print(f"Total products generated: {len(all_data)}")
    
    return scenarios

if __name__ == "__main__":
    print("Generating 100 sample scenarios with 100 products each for AI training...")
    scenarios = save_sample_data()
    print(f"✅ Generated {len(scenarios)} scenarios with 100 products each!")
    print("📁 Check the 'data/' folder for individual CSV files.")
    print("🎯 Each file contains 100 different product variations for optimal training!")
    print("📏 All dimensions are in feet (ft) and weights in pounds (lbs)")
    print("🏢 Destinations are warehouse zones instead of cities") 