import folium
import pandas as pd
import numpy as np
from folium import plugins
import streamlit as st

class MapVisualizer:
    """
    Map visualization utilities for EV dashboard
    """
    
    def __init__(self):
        self.default_location = [51.5074, -0.1278]  # London as default
        self.map_style = "OpenStreetMap"
    
    def create_base_map(self, center_lat=None, center_lon=None, zoom_start=10):
        """
        Create a base folium map
        
        Args:
            center_lat: Center latitude
            center_lon: Center longitude
            zoom_start: Initial zoom level
            
        Returns:
            Folium map object
        """
        
        if center_lat is None or center_lon is None:
            center_lat, center_lon = self.default_location
        
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom_start,
            tiles=self.map_style
        )
        
        return m
    
    def add_route_from_coordinates(self, map_obj, df, lat_col='latitude', lon_col='longitude', 
                                 energy_col='energy_consumption', time_col=None):
        """
        Add route visualization from GPS coordinates
        
        Args:
            map_obj: Folium map object
            df: DataFrame with GPS coordinates
            lat_col: Latitude column name
            lon_col: Longitude column name
            energy_col: Energy consumption column name
            time_col: Time column name (optional)
            
        Returns:
            Updated map object
        """
        
        if lat_col not in df.columns or lon_col not in df.columns:
            return map_obj
        
        # Filter valid coordinates
        valid_coords = df.dropna(subset=[lat_col, lon_col])
        
        if len(valid_coords) == 0:
            return map_obj
        
        # Create route line
        coordinates = valid_coords[[lat_col, lon_col]].values.tolist()
        
        # Color code by energy consumption if available
        if energy_col in df.columns:
            # Normalize energy consumption for color mapping
            energy_values = valid_coords[energy_col].values
            min_energy = energy_values.min()
            max_energy = energy_values.max()
            
            # Create segments with different colors
            for i in range(len(coordinates) - 1):
                start_point = coordinates[i]
                end_point = coordinates[i + 1]
                
                # Calculate color based on energy consumption
                energy_val = energy_values[i]
                normalized_energy = (energy_val - min_energy) / (max_energy - min_energy) if max_energy > min_energy else 0
                
                # Color from green (low consumption) to red (high consumption)
                color = self._get_color_for_energy(normalized_energy)
                
                folium.PolyLine(
                    locations=[start_point, end_point],
                    color=color,
                    weight=4,
                    opacity=0.8,
                    popup=f"Energy: {energy_val:.2f} kWh/100km"
                ).add_to(map_obj)
        else:
            # Simple blue route line
            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=4,
                opacity=0.8
            ).add_to(map_obj)
        
        # Add start and end markers
        if len(coordinates) > 0:
            # Start marker (green)
            folium.Marker(
                coordinates[0],
                popup="Start",
                icon=folium.Icon(color='green', icon='play')
            ).add_to(map_obj)
            
            # End marker (red)
            folium.Marker(
                coordinates[-1],
                popup="End",
                icon=folium.Icon(color='red', icon='stop')
            ).add_to(map_obj)
        
        return map_obj
    
    def create_energy_heatmap(self, map_obj, df, lat_col='latitude', lon_col='longitude', 
                            energy_col='energy_consumption'):
        """
        Create energy consumption heatmap
        
        Args:
            map_obj: Folium map object
            df: DataFrame with GPS and energy data
            lat_col: Latitude column name
            lon_col: Longitude column name
            energy_col: Energy consumption column name
            
        Returns:
            Updated map object
        """
        
        if lat_col not in df.columns or lon_col not in df.columns or energy_col not in df.columns:
            return map_obj
        
        # Filter valid data
        valid_data = df.dropna(subset=[lat_col, lon_col, energy_col])
        
        if len(valid_data) == 0:
            return map_obj
        
        # Prepare data for heatmap
        heat_data = []
        for _, row in valid_data.iterrows():
            # Use energy consumption as weight
            heat_data.append([row[lat_col], row[lon_col], row[energy_col]])
        
        # Add heatmap layer
        plugins.HeatMap(
            heat_data,
            min_opacity=0.4,
            radius=15,
            blur=10,
            gradient={0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(map_obj)
        
        return map_obj
    
    def add_charging_stations(self, map_obj, charging_stations_df=None):
        """
        Add charging station markers to map
        
        Args:
            map_obj: Folium map object
            charging_stations_df: DataFrame with charging station locations
            
        Returns:
            Updated map object
        """
        
        if charging_stations_df is None:
            # Add some sample charging stations (this would normally come from real data)
            sample_stations = [
                {"lat": 51.5074, "lon": -0.1278, "name": "Central London Station", "power": "50kW"},
                {"lat": 51.5155, "lon": -0.0922, "name": "City Station", "power": "150kW"},
                {"lat": 51.4994, "lon": -0.1244, "name": "Westminster Station", "power": "22kW"},
            ]
            
            for station in sample_stations:
                folium.Marker(
                    [station["lat"], station["lon"]],
                    popup=f"{station['name']}<br>Power: {station['power']}",
                    icon=folium.Icon(color='orange', icon='bolt')
                ).add_to(map_obj)
        else:
            # Use provided charging stations data
            for _, station in charging_stations_df.iterrows():
                folium.Marker(
                    [station['latitude'], station['longitude']],
                    popup=f"{station.get('name', 'Charging Station')}<br>Power: {station.get('power', 'Unknown')}",
                    icon=folium.Icon(color='orange', icon='bolt')
                ).add_to(map_obj)
        
        return map_obj
    
    def add_markers_with_data(self, map_obj, df, lat_col='latitude', lon_col='longitude', 
                            popup_cols=None):
        """
        Add markers with data popups
        
        Args:
            map_obj: Folium map object
            df: DataFrame with location data
            lat_col: Latitude column name
            lon_col: Longitude column name
            popup_cols: List of columns to include in popup
            
        Returns:
            Updated map object
        """
        
        if lat_col not in df.columns or lon_col not in df.columns:
            return map_obj
        
        if popup_cols is None:
            popup_cols = ['energy_consumption', 'speed', 'temperature']
        
        # Filter valid coordinates
        valid_data = df.dropna(subset=[lat_col, lon_col])
        
        # Sample data if too many points
        if len(valid_data) > 100:
            valid_data = valid_data.sample(n=100)
        
        for idx, row in valid_data.iterrows():
            # Create popup text
            popup_text = ""
            for col in popup_cols:
                if col in row and pd.notna(row[col]):
                    popup_text += f"{col}: {row[col]:.2f}<br>"
            
            if popup_text:
                folium.CircleMarker(
                    [row[lat_col], row[lon_col]],
                    radius=5,
                    popup=popup_text,
                    color='blue',
                    fill=True,
                    opacity=0.7
                ).add_to(map_obj)
        
        return map_obj
    
    def _get_color_for_energy(self, normalized_value):
        """
        Get color based on normalized energy value (0-1)
        
        Args:
            normalized_value: Value between 0 and 1
            
        Returns:
            Color string
        """
        
        if normalized_value < 0.2:
            return '#00ff00'  # Green
        elif normalized_value < 0.4:
            return '#80ff00'  # Yellow-green
        elif normalized_value < 0.6:
            return '#ffff00'  # Yellow
        elif normalized_value < 0.8:
            return '#ff8000'  # Orange
        else:
            return '#ff0000'  # Red
    
    def generate_sample_gps_data(self, n_points=100, center_lat=51.5074, center_lon=-0.1278, radius=0.1):
        """
        Generate sample GPS data for demonstration
        
        Args:
            n_points: Number of data points
            center_lat: Center latitude
            center_lon: Center longitude
            radius: Radius in degrees
            
        Returns:
            DataFrame with sample GPS and energy data
        """
        
        np.random.seed(42)
        
        # Generate random walk for GPS coordinates
        lat_points = []
        lon_points = []
        current_lat = center_lat
        current_lon = center_lon
        
        for i in range(n_points):
            # Random walk with some drift
            lat_step = np.random.normal(0, 0.001)
            lon_step = np.random.normal(0, 0.001)
            
            current_lat += lat_step
            current_lon += lon_step
            
            # Keep within bounds
            current_lat = np.clip(current_lat, center_lat - radius, center_lat + radius)
            current_lon = np.clip(current_lon, center_lon - radius, center_lon + radius)
            
            lat_points.append(current_lat)
            lon_points.append(current_lon)
        
        # Generate corresponding EV data
        speeds = np.random.normal(50, 15, n_points)
        speeds = np.clip(speeds, 0, 120)
        
        accelerations = np.random.normal(0, 1, n_points)
        temperatures = np.random.normal(20, 8, n_points)
        
        # Energy consumption based on speed and other factors
        energy_consumption = (
            0.15 * speeds + 
            0.0008 * speeds**2 + 
            np.abs(accelerations) * 2 + 
            np.abs(temperatures - 22) * 0.1 + 
            np.random.normal(0, 1, n_points)
        )
        energy_consumption = np.clip(energy_consumption, 5, 40)
        
        # Create DataFrame
        gps_data = pd.DataFrame({
            'latitude': lat_points,
            'longitude': lon_points,
            'speed': speeds,
            'acceleration': accelerations,
            'temperature': temperatures,
            'energy_consumption': energy_consumption,
            'timestamp': pd.date_range('2024-01-01 08:00:00', periods=n_points, freq='1min')
        })
        
        return gps_data
    
    def calculate_route_statistics(self, df, lat_col='latitude', lon_col='longitude', 
                                 energy_col='energy_consumption'):
        """
        Calculate route statistics
        
        Args:
            df: DataFrame with route data
            lat_col: Latitude column name
            lon_col: Longitude column name
            energy_col: Energy consumption column name
            
        Returns:
            Dictionary with route statistics
        """
        
        stats = {}
        
        if lat_col in df.columns and lon_col in df.columns:
            # Calculate distance using Haversine formula (approximate)
            def haversine_distance(lat1, lon1, lat2, lon2):
                R = 6371  # Earth's radius in km
                dlat = np.radians(lat2 - lat1)
                dlon = np.radians(lon2 - lon1)
                a = (np.sin(dlat/2)**2 + 
                     np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2)
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
                return R * c
            
            # Calculate total distance
            total_distance = 0
            for i in range(len(df) - 1):
                dist = haversine_distance(
                    df.iloc[i][lat_col], df.iloc[i][lon_col],
                    df.iloc[i+1][lat_col], df.iloc[i+1][lon_col]
                )
                total_distance += dist
            
            stats['total_distance_km'] = total_distance
            stats['num_points'] = len(df)
        
        if energy_col in df.columns:
            stats['avg_energy_consumption'] = df[energy_col].mean()
            stats['min_energy_consumption'] = df[energy_col].min()
            stats['max_energy_consumption'] = df[energy_col].max()
            
            if 'total_distance_km' in stats and stats['total_distance_km'] > 0:
                # Estimate total energy used
                avg_consumption_per_km = stats['avg_energy_consumption'] / 100  # Convert from per 100km
                stats['total_energy_used_kwh'] = stats['total_distance_km'] * avg_consumption_per_km
        
        if 'speed' in df.columns:
            stats['avg_speed_kmh'] = df['speed'].mean()
            stats['max_speed_kmh'] = df['speed'].max()
        
        return stats