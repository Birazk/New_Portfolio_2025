import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class CostCalculator:
    """
    Cost calculation utilities for EV vs Petrol comparison in Nepal
    """
    
    def __init__(self):
        # Current rates in Nepal (as of 2024)
        self.electricity_rate_npr = 9.5  # NPR per kWh (average residential rate)
        self.petrol_price_npr = 155.0    # NPR per liter (approximate)
        self.diesel_price_npr = 140.0    # NPR per liter (approximate)
        
        # Vehicle efficiency assumptions
        self.petrol_car_efficiency = 12.0  # km per liter (average)
        self.diesel_car_efficiency = 15.0  # km per liter (average)
        
        # Currency conversion (approximate)
        self.npr_to_usd = 0.0075  # 1 NPR = 0.0075 USD (approximate)
    
    def calculate_ev_cost_npr(self, energy_consumption_kwh_100km, distance_km):
        """
        Calculate EV operating cost in NPR
        
        Args:
            energy_consumption_kwh_100km: Energy consumption per 100km
            distance_km: Distance traveled in km
            
        Returns:
            dict: Cost breakdown in NPR
        """
        
        # Energy required for the distance
        energy_required_kwh = (energy_consumption_kwh_100km / 100) * distance_km
        
        # Cost calculation
        electricity_cost = energy_required_kwh * self.electricity_rate_npr
        
        # Add charging losses (approximately 10%)
        total_cost = electricity_cost * 1.1
        
        cost_breakdown = {
            'energy_required_kwh': energy_required_kwh,
            'electricity_cost_npr': electricity_cost,
            'charging_losses_npr': electricity_cost * 0.1,
            'total_cost_npr': total_cost,
            'cost_per_km_npr': total_cost / distance_km if distance_km > 0 else 0
        }
        
        return cost_breakdown
    
    def calculate_petrol_cost_npr(self, distance_km, fuel_type='petrol'):
        """
        Calculate petrol/diesel vehicle operating cost in NPR
        
        Args:
            distance_km: Distance traveled in km
            fuel_type: 'petrol' or 'diesel'
            
        Returns:
            dict: Cost breakdown in NPR
        """
        
        if fuel_type == 'petrol':
            fuel_price = self.petrol_price_npr
            efficiency = self.petrol_car_efficiency
        else:  # diesel
            fuel_price = self.diesel_price_npr
            efficiency = self.diesel_car_efficiency
        
        # Fuel required
        fuel_required_liters = distance_km / efficiency
        
        # Cost calculation
        fuel_cost = fuel_required_liters * fuel_price
        
        cost_breakdown = {
            'fuel_required_liters': fuel_required_liters,
            'fuel_price_per_liter': fuel_price,
            'fuel_cost_npr': fuel_cost,
            'cost_per_km_npr': fuel_cost / distance_km if distance_km > 0 else 0,
            'fuel_type': fuel_type
        }
        
        return cost_breakdown
    
    def compare_costs(self, energy_consumption_kwh_100km, distance_km):
        """
        Compare EV vs Petrol vs Diesel costs
        
        Args:
            energy_consumption_kwh_100km: EV energy consumption per 100km
            distance_km: Distance for comparison
            
        Returns:
            dict: Comparison results
        """
        
        ev_cost = self.calculate_ev_cost_npr(energy_consumption_kwh_100km, distance_km)
        petrol_cost = self.calculate_petrol_cost_npr(distance_km, 'petrol')
        diesel_cost = self.calculate_petrol_cost_npr(distance_km, 'diesel')
        
        # Calculate savings
        petrol_savings = petrol_cost['fuel_cost_npr'] - ev_cost['total_cost_npr']
        diesel_savings = diesel_cost['fuel_cost_npr'] - ev_cost['total_cost_npr']
        
        # Calculate percentage savings
        petrol_savings_percent = (petrol_savings / petrol_cost['fuel_cost_npr']) * 100 if petrol_cost['fuel_cost_npr'] > 0 else 0
        diesel_savings_percent = (diesel_savings / diesel_cost['fuel_cost_npr']) * 100 if diesel_cost['fuel_cost_npr'] > 0 else 0
        
        comparison = {
            'ev_cost': ev_cost,
            'petrol_cost': petrol_cost,
            'diesel_cost': diesel_cost,
            'petrol_savings_npr': petrol_savings,
            'diesel_savings_npr': diesel_savings,
            'petrol_savings_percent': petrol_savings_percent,
            'diesel_savings_percent': diesel_savings_percent
        }
        
        return comparison
    
    def calculate_annual_savings(self, energy_consumption_kwh_100km, annual_distance_km=15000):
        """
        Calculate annual cost savings for EV vs conventional vehicles
        
        Args:
            energy_consumption_kwh_100km: EV energy consumption per 100km
            annual_distance_km: Annual distance traveled (default 15,000 km)
            
        Returns:
            dict: Annual savings analysis
        """
        
        comparison = self.compare_costs(energy_consumption_kwh_100km, annual_distance_km)
        
        annual_analysis = {
            'annual_distance_km': annual_distance_km,
            'ev_annual_cost_npr': comparison['ev_cost']['total_cost_npr'],
            'petrol_annual_cost_npr': comparison['petrol_cost']['fuel_cost_npr'],
            'diesel_annual_cost_npr': comparison['diesel_cost']['fuel_cost_npr'],
            'annual_petrol_savings_npr': comparison['petrol_savings_npr'],
            'annual_diesel_savings_npr': comparison['diesel_savings_npr'],
            'annual_petrol_savings_usd': comparison['petrol_savings_npr'] * self.npr_to_usd,
            'annual_diesel_savings_usd': comparison['diesel_savings_npr'] * self.npr_to_usd
        }
        
        return annual_analysis
    
    def create_cost_comparison_chart(self, energy_consumption_kwh_100km, max_distance=1000):
        """
        Create interactive cost comparison chart
        
        Args:
            energy_consumption_kwh_100km: EV energy consumption per 100km
            max_distance: Maximum distance for chart (km)
            
        Returns:
            plotly figure
        """
        
        distances = np.arange(50, max_distance + 1, 50)
        ev_costs = []
        petrol_costs = []
        diesel_costs = []
        
        for distance in distances:
            ev_cost = self.calculate_ev_cost_npr(energy_consumption_kwh_100km, distance)
            petrol_cost = self.calculate_petrol_cost_npr(distance, 'petrol')
            diesel_cost = self.calculate_petrol_cost_npr(distance, 'diesel')
            
            ev_costs.append(ev_cost['total_cost_npr'])
            petrol_costs.append(petrol_cost['fuel_cost_npr'])
            diesel_costs.append(diesel_cost['fuel_cost_npr'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=distances,
            y=ev_costs,
            mode='lines+markers',
            name='Electric Vehicle',
            line=dict(color='green', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=distances,
            y=petrol_costs,
            mode='lines+markers',
            name='Petrol Vehicle',
            line=dict(color='red', width=3),
            marker=dict(size=6)
        ))
        
        fig.add_trace(go.Scatter(
            x=distances,
            y=diesel_costs,
            mode='lines+markers',
            name='Diesel Vehicle',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ))
        
        fig.update_layout(
            title='Vehicle Operating Cost Comparison (Nepal)',
            xaxis_title='Distance (km)',
            yaxis_title='Operating Cost (NPR)',
            hovermode='x unified',
            template='plotly_white',
            showlegend=True
        )
        
        return fig
    
    def create_savings_breakdown_chart(self, annual_analysis):
        """
        Create savings breakdown chart
        
        Args:
            annual_analysis: Annual analysis results
            
        Returns:
            plotly figure
        """
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Annual Operating Costs', 'Annual Savings vs Petrol', 
                           'Annual Savings vs Diesel', 'Cost per 100km Comparison'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Annual costs comparison
        vehicles = ['Electric', 'Petrol', 'Diesel']
        costs = [
            annual_analysis['ev_annual_cost_npr'],
            annual_analysis['petrol_annual_cost_npr'],
            annual_analysis['diesel_annual_cost_npr']
        ]
        colors = ['green', 'red', 'blue']
        
        fig.add_trace(
            go.Bar(x=vehicles, y=costs, marker_color=colors, name='Annual Cost'),
            row=1, col=1
        )
        
        # Savings bars
        savings_petrol = [annual_analysis['annual_petrol_savings_npr']]
        savings_diesel = [annual_analysis['annual_diesel_savings_npr']]
        
        fig.add_trace(
            go.Bar(x=['EV vs Petrol'], y=savings_petrol, marker_color='green', name='Savings vs Petrol'),
            row=1, col=2
        )
        
        fig.add_trace(
            go.Bar(x=['EV vs Diesel'], y=savings_diesel, marker_color='green', name='Savings vs Diesel'),
            row=2, col=1
        )
        
        # Cost per 100km
        cost_per_100km = [
            (annual_analysis['ev_annual_cost_npr'] / annual_analysis['annual_distance_km']) * 100,
            (annual_analysis['petrol_annual_cost_npr'] / annual_analysis['annual_distance_km']) * 100,
            (annual_analysis['diesel_annual_cost_npr'] / annual_analysis['annual_distance_km']) * 100
        ]
        
        fig.add_trace(
            go.Bar(x=vehicles, y=cost_per_100km, marker_color=colors, name='Cost per 100km'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text="Annual Cost Analysis - Nepal (NPR)",
            showlegend=False
        )
        
        # Update y-axis labels
        fig.update_yaxes(title_text="Cost (NPR)", row=1, col=1)
        fig.update_yaxes(title_text="Savings (NPR)", row=1, col=2)
        fig.update_yaxes(title_text="Savings (NPR)", row=2, col=1)
        fig.update_yaxes(title_text="Cost per 100km (NPR)", row=2, col=2)
        
        return fig
    
    def get_cost_rates_info(self):
        """
        Get current cost rates information
        
        Returns:
            dict: Current rates and assumptions
        """
        
        rates_info = {
            'electricity_rate_npr_per_kwh': self.electricity_rate_npr,
            'petrol_price_npr_per_liter': self.petrol_price_npr,
            'diesel_price_npr_per_liter': self.diesel_price_npr,
            'petrol_efficiency_km_per_liter': self.petrol_car_efficiency,
            'diesel_efficiency_km_per_liter': self.diesel_car_efficiency,
            'charging_efficiency_loss_percent': 10,
            'npr_to_usd_rate': self.npr_to_usd
        }
        
        return rates_info
    
    def calculate_payback_period(self, ev_price_npr, conventional_price_npr, 
                                energy_consumption_kwh_100km, annual_distance_km=15000):
        """
        Calculate payback period for EV purchase
        
        Args:
            ev_price_npr: EV purchase price in NPR
            conventional_price_npr: Conventional vehicle price in NPR
            energy_consumption_kwh_100km: EV energy consumption
            annual_distance_km: Annual driving distance
            
        Returns:
            dict: Payback analysis
        """
        
        price_difference = ev_price_npr - conventional_price_npr
        annual_analysis = self.calculate_annual_savings(energy_consumption_kwh_100km, annual_distance_km)
        
        # Use petrol savings for payback calculation
        annual_savings = annual_analysis['annual_petrol_savings_npr']
        
        if annual_savings > 0:
            payback_years = price_difference / annual_savings
        else:
            payback_years = float('inf')  # No payback if no savings
        
        payback_analysis = {
            'ev_price_npr': ev_price_npr,
            'conventional_price_npr': conventional_price_npr,
            'price_difference_npr': price_difference,
            'annual_savings_npr': annual_savings,
            'payback_period_years': payback_years,
            'total_5_year_savings_npr': annual_savings * 5 - price_difference,
            'total_10_year_savings_npr': annual_savings * 10 - price_difference
        }
        
        return payback_analysis