import numpy as np
import pandas as pd
from scipy import integrate

class EnergyCalculator:
    """
    Physics-based energy consumption calculator for electric vehicles
    Based on the research methodology from the BMW i3 case study
    """
    
    def __init__(self):
        # Default vehicle parameters (BMW i3-like)
        self.default_params = {
            'vehicle_mass': 1195,  # kg (curb weight)
            'frontal_area': 2.38,  # m²
            'drag_coefficient': 0.29,
            'rolling_resistance_coef': 0.01,
            'motor_efficiency': 0.90,
            'regenerative_efficiency': 0.70,
            'auxiliary_power': 1.0,  # kW (average)
            'battery_efficiency': 0.95,
            'transmission_efficiency': 0.95
        }
        
        # Physical constants
        self.g = 9.81  # m/s² (gravity)
        self.air_density = 1.225  # kg/m³ (at sea level, 15°C)
    
    def calculate_energy_consumption(self, speed, acceleration=0.0, road_slope=0.0, 
                                   temperature=20.0, vehicle_mass=None, frontal_area=None,
                                   drag_coefficient=None, rolling_resistance=None,
                                   motor_efficiency=None, auxiliary_power=None,
                                   air_density=None):
        """
        Calculate instantaneous energy consumption based on driving conditions
        
        Args:
            speed: Vehicle speed (km/h)
            acceleration: Vehicle acceleration (m/s²)
            road_slope: Road slope (degrees)
            temperature: Ambient temperature (°C)
            vehicle_mass: Vehicle mass (kg)
            frontal_area: Frontal area (m²)
            drag_coefficient: Drag coefficient
            rolling_resistance: Rolling resistance coefficient
            motor_efficiency: Motor efficiency (0-1)
            auxiliary_power: Auxiliary power consumption (kW)
            air_density: Air density (kg/m³)
            
        Returns:
            Energy consumption (kWh/100km)
        """
        
        # Use default values if not provided
        vehicle_mass = vehicle_mass or self.default_params['vehicle_mass']
        frontal_area = frontal_area or self.default_params['frontal_area']
        drag_coefficient = drag_coefficient or self.default_params['drag_coefficient']
        rolling_resistance = rolling_resistance or self.default_params['rolling_resistance_coef']
        motor_efficiency = motor_efficiency or self.default_params['motor_efficiency']
        auxiliary_power = auxiliary_power or self.default_params['auxiliary_power']
        air_density = air_density or self.air_density
        
        # Convert speed from km/h to m/s
        speed_ms = speed / 3.6
        
        # Convert road slope from degrees to radians
        slope_rad = np.radians(road_slope)
        
        # Calculate forces acting on the vehicle
        forces = self._calculate_forces(
            speed_ms, acceleration, slope_rad, vehicle_mass,
            frontal_area, drag_coefficient, rolling_resistance, air_density
        )
        
        # Calculate total tractive force at wheels
        total_force = forces['aerodynamic'] + forces['rolling'] + forces['gravitational'] + forces['inertial']
        
        # Calculate mechanical power at wheels (kW)
        if speed_ms > 0:
            mechanical_power = (total_force * speed_ms) / 1000  # kW
        else:
            mechanical_power = 0
        
        # Handle regenerative braking
        if mechanical_power < 0:  # Braking
            mechanical_power *= self.default_params['regenerative_efficiency']
        
        # Calculate electrical power from battery
        electrical_power = mechanical_power / motor_efficiency / self.default_params['transmission_efficiency']
        
        # Add auxiliary power consumption
        total_power = electrical_power + auxiliary_power
        
        # Add temperature effect on auxiliary systems
        temp_effect = self._calculate_temperature_effect(temperature)
        total_power += temp_effect
        
        # Convert to energy consumption (kWh/100km)
        if speed > 0:
            energy_consumption = (total_power * 100) / speed  # kWh/100km
        else:
            energy_consumption = 0
        
        # Apply battery efficiency
        energy_consumption /= self.default_params['battery_efficiency']
        
        return max(0, energy_consumption)  # Ensure non-negative consumption
    
    def _calculate_forces(self, speed_ms, acceleration, slope_rad, vehicle_mass,
                         frontal_area, drag_coefficient, rolling_resistance, air_density):
        """
        Calculate individual forces acting on the vehicle
        
        Returns:
            Dictionary with force components (N)
        """
        
        forces = {}
        
        # Aerodynamic drag force
        forces['aerodynamic'] = 0.5 * air_density * frontal_area * drag_coefficient * speed_ms**2
        
        # Rolling resistance force
        forces['rolling'] = rolling_resistance * vehicle_mass * self.g * np.cos(slope_rad)
        
        # Gravitational force (road slope)
        forces['gravitational'] = vehicle_mass * self.g * np.sin(slope_rad)
        
        # Inertial force (acceleration/deceleration)
        forces['inertial'] = vehicle_mass * acceleration
        
        return forces
    
    def _calculate_temperature_effect(self, temperature):
        """
        Calculate additional power consumption due to temperature
        
        Args:
            temperature: Ambient temperature (°C)
            
        Returns:
            Additional power consumption (kW)
        """
        
        # Optimal temperature range (minimal HVAC usage)
        optimal_temp = 22  # °C
        
        # Calculate temperature difference
        temp_diff = abs(temperature - optimal_temp)
        
        # HVAC power consumption increases with temperature difference
        if temperature < optimal_temp:
            # Heating (typically more energy intensive)
            hvac_power = temp_diff * 0.15  # kW per degree
        else:
            # Cooling
            hvac_power = temp_diff * 0.12  # kW per degree
        
        return min(hvac_power, 5.0)  # Cap at 5 kW maximum
    
    def calculate_range(self, energy_consumption, battery_capacity, current_soc):
        """
        Calculate estimated driving range
        
        Args:
            energy_consumption: Energy consumption (kWh/100km)
            battery_capacity: Battery capacity (kWh)
            current_soc: Current state of charge (%)
            
        Returns:
            Estimated range (km)
        """
        
        # Available energy
        available_energy = battery_capacity * (current_soc / 100)
        
        # Calculate range
        if energy_consumption > 0:
            estimated_range = (available_energy / energy_consumption) * 100
        else:
            estimated_range = 0
        
        return estimated_range
    
    def get_energy_breakdown(self, speed, acceleration=0.0, road_slope=0.0,
                           vehicle_mass=None, frontal_area=None, drag_coefficient=None,
                           rolling_resistance=None, auxiliary_power=None, air_density=None):
        """
        Get detailed breakdown of energy consumption components
        
        Returns:
            Dictionary with energy breakdown
        """
        
        # Use default values if not provided
        vehicle_mass = vehicle_mass or self.default_params['vehicle_mass']
        frontal_area = frontal_area or self.default_params['frontal_area']
        drag_coefficient = drag_coefficient or self.default_params['drag_coefficient']
        rolling_resistance = rolling_resistance or self.default_params['rolling_resistance_coef']
        auxiliary_power = auxiliary_power or self.default_params['auxiliary_power']
        air_density = air_density or self.air_density
        
        # Convert speed
        speed_ms = speed / 3.6
        slope_rad = np.radians(road_slope)
        
        # Calculate forces
        forces = self._calculate_forces(
            speed_ms, acceleration, slope_rad, vehicle_mass,
            frontal_area, drag_coefficient, rolling_resistance, air_density
        )
        
        # Calculate power for each component
        if speed_ms > 0:
            aero_power = (forces['aerodynamic'] * speed_ms) / 1000  # kW
            rolling_power = (forces['rolling'] * speed_ms) / 1000  # kW
            grav_power = (forces['gravitational'] * speed_ms) / 1000  # kW
            inertial_power = (forces['inertial'] * speed_ms) / 1000  # kW
        else:
            aero_power = rolling_power = grav_power = inertial_power = 0
        
        # Convert to percentages
        total_mechanical = abs(aero_power) + abs(rolling_power) + abs(grav_power) + abs(inertial_power)
        total_power = total_mechanical + auxiliary_power
        
        if total_power > 0:
            breakdown = {
                'Aerodynamic Drag': (abs(aero_power) / total_power) * 100,
                'Rolling Resistance': (abs(rolling_power) / total_power) * 100,
                'Gravitational': (abs(grav_power) / total_power) * 100,
                'Acceleration': (abs(inertial_power) / total_power) * 100,
                'Auxiliary Systems': (auxiliary_power / total_power) * 100
            }
        else:
            breakdown = {
                'Aerodynamic Drag': 0,
                'Rolling Resistance': 0,
                'Gravitational': 0,
                'Acceleration': 0,
                'Auxiliary Systems': 100
            }
        
        return breakdown
    
    def calculate_trip_energy(self, speed_profile, acceleration_profile=None,
                            slope_profile=None, temperature_profile=None, time_step=1):
        """
        Calculate total energy consumption for a trip
        
        Args:
            speed_profile: Array of speeds (km/h)
            acceleration_profile: Array of accelerations (m/s²)
            slope_profile: Array of road slopes (degrees)
            temperature_profile: Array of temperatures (°C)
            time_step: Time step in seconds
            
        Returns:
            Dictionary with trip energy analysis
        """
        
        n_points = len(speed_profile)
        
        # Use default profiles if not provided
        if acceleration_profile is None:
            acceleration_profile = np.zeros(n_points)
        if slope_profile is None:
            slope_profile = np.zeros(n_points)
        if temperature_profile is None:
            temperature_profile = np.full(n_points, 20)
        
        # Calculate energy consumption at each point
        energy_consumptions = []
        for i in range(n_points):
            consumption = self.calculate_energy_consumption(
                speed_profile[i],
                acceleration_profile[i],
                slope_profile[i],
                temperature_profile[i]
            )
            energy_consumptions.append(consumption)
        
        energy_consumptions = np.array(energy_consumptions)
        
        # Calculate distance traveled
        distances = (np.array(speed_profile) / 3.6) * time_step / 1000  # km
        total_distance = np.sum(distances)
        
        # Calculate total energy
        instantaneous_power = energy_consumptions * np.array(speed_profile) / 100  # kW
        total_energy = np.sum(instantaneous_power) * time_step / 3600  # kWh
        
        # Average consumption
        if total_distance > 0:
            avg_consumption = (total_energy / total_distance) * 100  # kWh/100km
        else:
            avg_consumption = 0
        
        # Trip statistics
        trip_stats = {
            'total_distance': total_distance,
            'total_energy': total_energy,
            'average_consumption': avg_consumption,
            'max_consumption': np.max(energy_consumptions),
            'min_consumption': np.min(energy_consumptions),
            'average_speed': np.mean(speed_profile),
            'max_speed': np.max(speed_profile),
            'consumption_profile': energy_consumptions.tolist()
        }
        
        return trip_stats
    
    def optimize_speed_for_range(self, target_distance, battery_capacity, current_soc,
                               speed_range=(30, 120), road_slope=0, temperature=20):
        """
        Find optimal speed for maximum range
        
        Args:
            target_distance: Target distance (km)
            battery_capacity: Battery capacity (kWh)
            current_soc: Current state of charge (%)
            speed_range: Tuple of (min_speed, max_speed) in km/h
            road_slope: Road slope (degrees)
            temperature: Temperature (°C)
            
        Returns:
            Dictionary with optimization results
        """
        
        speeds = np.arange(speed_range[0], speed_range[1] + 1, 1)
        consumptions = []
        ranges = []
        
        for speed in speeds:
            consumption = self.calculate_energy_consumption(
                speed, 0, road_slope, temperature
            )
            range_km = self.calculate_range(consumption, battery_capacity, current_soc)
            
            consumptions.append(consumption)
            ranges.append(range_km)
        
        # Find optimal speed
        ranges = np.array(ranges)
        optimal_idx = np.argmax(ranges)
        optimal_speed = speeds[optimal_idx]
        max_range = ranges[optimal_idx]
        optimal_consumption = consumptions[optimal_idx]
        
        # Check if target distance is achievable
        can_reach_target = max_range >= target_distance
        
        if can_reach_target:
            # Find minimum speed to reach target
            feasible_speeds = speeds[ranges >= target_distance]
            if len(feasible_speeds) > 0:
                recommended_speed = feasible_speeds[0]  # Lowest feasible speed
            else:
                recommended_speed = optimal_speed
        else:
            recommended_speed = optimal_speed
        
        results = {
            'optimal_speed': optimal_speed,
            'max_range': max_range,
            'optimal_consumption': optimal_consumption,
            'recommended_speed': recommended_speed,
            'can_reach_target': can_reach_target,
            'target_distance': target_distance,
            'speed_range_analysis': {
                'speeds': speeds.tolist(),
                'consumptions': consumptions,
                'ranges': ranges.tolist()
            }
        }
        
        return results
    
    def estimate_charging_time(self, current_soc, target_soc, battery_capacity, 
                             charging_power, charging_curve=None):
        """
        Estimate charging time based on charging power and curve
        
        Args:
            current_soc: Current state of charge (%)
            target_soc: Target state of charge (%)
            battery_capacity: Battery capacity (kWh)
            charging_power: Charging power (kW)
            charging_curve: Optional charging curve (list of (soc, power_factor) tuples)
            
        Returns:
            Estimated charging time (hours)
        """
        
        if charging_curve is None:
            # Simple constant power charging
            energy_needed = battery_capacity * (target_soc - current_soc) / 100
            charging_time = energy_needed / charging_power
        else:
            # Use charging curve
            soc_range = np.linspace(current_soc, target_soc, 100)
            charging_time = 0
            
            for i in range(len(soc_range) - 1):
                soc = soc_range[i]
                soc_step = soc_range[i + 1] - soc
                
                # Interpolate power factor from charging curve
                power_factor = self._interpolate_charging_curve(soc, charging_curve)
                effective_power = charging_power * power_factor
                
                energy_step = battery_capacity * soc_step / 100
                time_step = energy_step / effective_power
                charging_time += time_step
        
        return charging_time
    
    def _interpolate_charging_curve(self, soc, charging_curve):
        """
        Interpolate power factor from charging curve
        
        Args:
            soc: State of charge (%)
            charging_curve: List of (soc, power_factor) tuples
            
        Returns:
            Power factor (0-1)
        """
        
        soc_points = [point[0] for point in charging_curve]
        power_factors = [point[1] for point in charging_curve]
        
        return np.interp(soc, soc_points, power_factors)
