import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
import os

def calculate_workspace(kinematics, robot_params: Dict[str, Any], resolution: int = 200) -> Dict[str, np.ndarray]:
    """
    Calculate the reachable workspace of the robot
    
    Args:
        kinematics: RobotKinematics instance
        robot_params: Dictionary containing robot parameters including joint limits
        resolution: Number of points per joint for workspace sampling
        
    Returns:
        Dictionary containing workspace x and y coordinates
    """
    # Extract joint limits
    q1_limits = robot_params['q1_limits']
    q2_limits = robot_params['q2_limits']
    
    # Generate joint angle arrays
    q1_vals = np.linspace(q1_limits[0], q1_limits[1], resolution)
    q2_vals = np.linspace(q2_limits[0], q2_limits[1], resolution)
    
    # Calculate all reachable positions
    x_points = []
    y_points = []
    
    for q1 in q1_vals:
        for q2 in q2_vals:
            pos = kinematics.forward_kinematics(q1, q2)
            x_points.append(pos[0])
            y_points.append(pos[1])
    
    return {
        'x': np.array(x_points),
        'y': np.array(y_points)
    }

def calculate_manipulability_map(kinematics, robot_params: Dict[str, Any], 
                                resolution: int = 50) -> Dict[str, np.ndarray]:
    """
    Calculate manipulability index across the joint space
    
    Args:
        kinematics: RobotKinematics instance
        robot_params: Dictionary containing robot parameters
        resolution: Grid resolution for calculation
        
    Returns:
        Dictionary containing joint angles and manipulability values
    """
    q1_limits = robot_params['q1_limits']
    q2_limits = robot_params['q2_limits']
    
    q1_vals = np.linspace(q1_limits[0], q1_limits[1], resolution)
    q2_vals = np.linspace(q2_limits[0], q2_limits[1], resolution)
    
    Q1, Q2 = np.meshgrid(q1_vals, q2_vals)
    manipulability = np.zeros_like(Q1)
    
    for i in range(resolution):
        for j in range(resolution):
            try:
                manip = kinematics.compute_manipulability(Q1[i, j], Q2[i, j])
                manipulability[i, j] = manip
            except:
                manipulability[i, j] = 0
    
    return {
        'q1': q1_vals,
        'q2': q2_vals,
        'manipulability': manipulability
    }

def find_singularities(kinematics, robot_params: Dict[str, Any], 
                      tolerance: float = 1e-3, resolution: int = 100) -> List[Tuple[float, float]]:
    """
    Find singular configurations in the robot workspace
    
    Args:
        kinematics: RobotKinematics instance
        robot_params: Dictionary containing robot parameters
        tolerance: Tolerance for singularity detection
        resolution: Grid resolution for search
        
    Returns:
        List of singular joint configurations
    """
    q1_limits = robot_params['q1_limits']
    q2_limits = robot_params['q2_limits']
    
    q1_vals = np.linspace(q1_limits[0], q1_limits[1], resolution)
    q2_vals = np.linspace(q2_limits[0], q2_limits[1], resolution)
    
    singularities = []
    
    for q1 in q1_vals:
        for q2 in q2_vals:
            if kinematics.check_singularity(q1, q2, tolerance):
                singularities.append((q1, q2))
    
    return singularities

def calculate_trajectory_metrics(trajectory_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate performance metrics for trajectory tracking
    
    Args:
        trajectory_data: DataFrame containing trajectory tracking data
        
    Returns:
        Dictionary containing performance metrics
    """
    metrics = {}
    
    # Position tracking metrics
    if 'error_x' in trajectory_data.columns and 'error_y' in trajectory_data.columns:
        position_error = np.sqrt(trajectory_data['error_x']**2 + trajectory_data['error_y']**2)
        
        metrics['max_position_error'] = float(np.max(position_error))
        metrics['mean_position_error'] = float(np.mean(position_error))
        metrics['rms_position_error'] = float(np.sqrt(np.mean(position_error**2)))
        metrics['final_position_error'] = float(position_error.iloc[-1])
        
        # Settling time (2% criterion)
        final_error = position_error.iloc[-1]
        settling_threshold = max(0.02, abs(final_error) * 1.02)
        
        for i in range(len(position_error) - 1, -1, -1):
            if position_error.iloc[i] > settling_threshold:
                if i < len(trajectory_data) - 1:
                    settling_time = trajectory_data['time'].iloc[i + 1]
                else:
                    settling_time = trajectory_data['time'].iloc[-1]
                break
        else:
            settling_time = 0.0
        
        metrics['settling_time'] = float(settling_time)
    
    # Control effort metrics
    if 'tau1' in trajectory_data.columns and 'tau2' in trajectory_data.columns:
        control_effort = np.sqrt(trajectory_data['tau1']**2 + trajectory_data['tau2']**2)
        
        metrics['max_control_effort'] = float(np.max(control_effort))
        metrics['mean_control_effort'] = float(np.mean(control_effort))
        metrics['total_control_energy'] = float(np.trapz(control_effort**2, trajectory_data['time']))
    
    # Smoothness metrics
    if 'q1_dot' in trajectory_data.columns and 'q2_dot' in trajectory_data.columns:
        # Jerk calculation (derivative of acceleration)
        dt = trajectory_data['time'].diff().mean()
        
        if 'q1_ddot' in trajectory_data.columns:
            q1_jerk = np.gradient(trajectory_data['q1_ddot'], dt)
            q2_jerk = np.gradient(trajectory_data['q2_ddot'], dt)
        else:
            # Approximate jerk from velocity
            q1_accel = np.gradient(trajectory_data['q1_dot'], dt)
            q2_accel = np.gradient(trajectory_data['q2_dot'], dt)
            q1_jerk = np.gradient(q1_accel, dt)
            q2_jerk = np.gradient(q2_accel, dt)
        
        jerk_magnitude = np.sqrt(q1_jerk**2 + q2_jerk**2)
        metrics['mean_jerk'] = float(np.mean(jerk_magnitude))
        metrics['max_jerk'] = float(np.max(jerk_magnitude))
    
    return metrics

def export_simulation_data(simulation_data: List[Dict], filename: Optional[str] = None, 
                          format: str = 'csv') -> str:
    """
    Export simulation data to file
    
    Args:
        simulation_data: List of simulation data dictionaries
        filename: Output filename (if None, auto-generated)
        format: Export format ('csv', 'json', 'excel')
        
    Returns:
        Filename of exported data
    """
    if not simulation_data:
        raise ValueError("No simulation data to export")
    
    # Convert to DataFrame
    df = pd.DataFrame(simulation_data)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"robot_simulation_{timestamp}"
    
    # Add extension if not present
    if format == 'csv' and not filename.endswith('.csv'):
        filename += '.csv'
    elif format == 'json' and not filename.endswith('.json'):
        filename += '.json'
    elif format == 'excel' and not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Export data
    if format == 'csv':
        df.to_csv(filename, index=False)
    elif format == 'json':
        df.to_json(filename, orient='records', indent=2)
    elif format == 'excel':
        df.to_excel(filename, index=False)
    else:
        raise ValueError(f"Unsupported export format: {format}")
    
    return filename

def validate_robot_parameters(params: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate robot parameters for physical consistency
    
    Args:
        params: Dictionary containing robot parameters
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check for required parameters
    required_params = ['l1', 'l2', 'm1', 'm2', 'I1', 'I2']
    for param in required_params:
        if param not in params:
            errors.append(f"Missing required parameter: {param}")
        elif params[param] <= 0:
            errors.append(f"Parameter {param} must be positive")
    
    # Check joint limits
    if 'q1_limits' in params:
        q1_min, q1_max = params['q1_limits']
        if q1_min >= q1_max:
            errors.append("q1_min must be less than q1_max")
        if abs(q1_max - q1_min) < 0.1:
            errors.append("Joint 1 range is too small (minimum 0.1 rad)")
    
    if 'q2_limits' in params:
        q2_min, q2_max = params['q2_limits']
        if q2_min >= q2_max:
            errors.append("q2_min must be less than q2_max")
        if abs(q2_max - q2_min) < 0.1:
            errors.append("Joint 2 range is too small (minimum 0.1 rad)")
    
    # Physical consistency checks
    if all(param in params for param in ['l1', 'l2', 'm1', 'm2', 'I1', 'I2']):
        # Check if inertias are reasonable for given masses and lengths
        # For a uniform rod: I = (1/12) * m * l^2
        I1_min = (1/12) * params['m1'] * params['l1']**2 * 0.1  # Allow 10x smaller
        I1_max = (1/12) * params['m1'] * params['l1']**2 * 10   # Allow 10x larger
        
        if not (I1_min <= params['I1'] <= I1_max):
            errors.append(f"I1 seems unrealistic for given m1 and l1 (expected range: {I1_min:.4f} - {I1_max:.4f})")
        
        I2_min = (1/12) * params['m2'] * params['l2']**2 * 0.1
        I2_max = (1/12) * params['m2'] * params['l2']**2 * 10
        
        if not (I2_min <= params['I2'] <= I2_max):
            errors.append(f"I2 seems unrealistic for given m2 and l2 (expected range: {I2_min:.4f} - {I2_max:.4f})")
    
    return len(errors) == 0, errors

def calculate_energy_efficiency(trajectory_data: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate energy efficiency metrics for the trajectory
    
    Args:
        trajectory_data: DataFrame containing trajectory data
        
    Returns:
        Dictionary containing energy efficiency metrics
    """
    metrics = {}
    
    if not all(col in trajectory_data.columns for col in ['tau1', 'tau2', 'q1_dot', 'q2_dot', 'time']):
        return metrics
    
    dt = trajectory_data['time'].diff().mean()
    
    # Mechanical power (P = τ * ω)
    power1 = trajectory_data['tau1'] * trajectory_data['q1_dot']
    power2 = trajectory_data['tau2'] * trajectory_data['q2_dot']
    total_power = power1 + power2
    
    # Energy consumption (integrate power over time)
    positive_power = np.maximum(total_power, 0)  # Only count positive power (energy input)
    total_energy = np.trapz(positive_power, trajectory_data['time'])
    
    metrics['total_energy_consumption'] = float(total_energy)
    metrics['average_power'] = float(np.mean(np.abs(total_power)))
    metrics['peak_power'] = float(np.max(np.abs(total_power)))
    
    # Energy efficiency (useful work / total energy)
    if 'desired_x' in trajectory_data.columns and 'desired_y' in trajectory_data.columns:
        # Calculate path length
        dx = np.diff(trajectory_data['desired_x'])
        dy = np.diff(trajectory_data['desired_y'])
        path_length = np.sum(np.sqrt(dx**2 + dy**2))
        
        if total_energy > 0 and path_length > 0:
            metrics['energy_per_distance'] = float(total_energy / path_length)
        
        # Time efficiency
        total_time = trajectory_data['time'].iloc[-1] - trajectory_data['time'].iloc[0]
        if total_time > 0:
            metrics['average_speed'] = float(path_length / total_time)
    
    return metrics

def analyze_control_stability(trajectory_data: pd.DataFrame, window_size: int = 50) -> Dict[str, Any]:
    """
    Analyze control system stability from trajectory data
    
    Args:
        trajectory_data: DataFrame containing trajectory data
        window_size: Window size for stability analysis
        
    Returns:
        Dictionary containing stability metrics
    """
    analysis = {}
    
    if 'error_x' not in trajectory_data.columns or 'error_y' not in trajectory_data.columns:
        return analysis
    
    position_error = np.sqrt(trajectory_data['error_x']**2 + trajectory_data['error_y']**2)
    
    # Check for oscillations
    error_diff = np.diff(position_error)
    sign_changes = np.sum(np.diff(np.sign(error_diff)) != 0)
    analysis['oscillation_frequency'] = float(sign_changes / len(error_diff))
    
    # Stability margin (how much error decreases over time)
    if len(position_error) >= window_size * 2:
        early_error = np.mean(position_error[:window_size])
        late_error = np.mean(position_error[-window_size:])
        
        if early_error > 0:
            analysis['error_reduction_ratio'] = float(late_error / early_error)
            analysis['converged'] = late_error < early_error * 0.1
        else:
            analysis['error_reduction_ratio'] = 1.0
            analysis['converged'] = True
    
    # Control saturation detection
    if 'tau1' in trajectory_data.columns and 'tau2' in trajectory_data.columns:
        # Simple saturation detection based on sudden torque limits
        tau1_saturated = np.sum(np.abs(np.diff(trajectory_data['tau1'])) < 1e-6)
        tau2_saturated = np.sum(np.abs(np.diff(trajectory_data['tau2'])) < 1e-6)
        
        total_points = len(trajectory_data)
        analysis['tau1_saturation_ratio'] = float(tau1_saturated / total_points)
        analysis['tau2_saturation_ratio'] = float(tau2_saturated / total_points)
    
    return analysis

def generate_performance_report(trajectory_data: pd.DataFrame, robot_params: Dict[str, Any]) -> str:
    """
    Generate a comprehensive performance report
    
    Args:
        trajectory_data: DataFrame containing trajectory data
        robot_params: Dictionary containing robot parameters
        
    Returns:
        String containing formatted performance report
    """
    report = []
    report.append("=" * 50)
    report.append("ROBOT PERFORMANCE ANALYSIS REPORT")
    report.append("=" * 50)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Robot configuration
    report.append("ROBOT CONFIGURATION:")
    report.append(f"  Link 1 Length: {robot_params.get('l1', 'N/A'):.3f} m")
    report.append(f"  Link 2 Length: {robot_params.get('l2', 'N/A'):.3f} m")
    report.append(f"  Link 1 Mass: {robot_params.get('m1', 'N/A'):.3f} kg")
    report.append(f"  Link 2 Mass: {robot_params.get('m2', 'N/A'):.3f} kg")
    report.append("")
    
    # Trajectory metrics
    traj_metrics = calculate_trajectory_metrics(trajectory_data)
    if traj_metrics:
        report.append("TRAJECTORY TRACKING PERFORMANCE:")
        for key, value in traj_metrics.items():
            formatted_key = key.replace('_', ' ').title()
            if 'error' in key.lower() or 'time' in key.lower():
                report.append(f"  {formatted_key}: {value:.4f}")
            else:
                report.append(f"  {formatted_key}: {value:.2f}")
        report.append("")
    
    # Energy efficiency
    energy_metrics = calculate_energy_efficiency(trajectory_data)
    if energy_metrics:
        report.append("ENERGY EFFICIENCY:")
        for key, value in energy_metrics.items():
            formatted_key = key.replace('_', ' ').title()
            report.append(f"  {formatted_key}: {value:.4f}")
        report.append("")
    
    # Stability analysis
    stability_analysis = analyze_control_stability(trajectory_data)
    if stability_analysis:
        report.append("CONTROL STABILITY:")
        for key, value in stability_analysis.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, bool):
                report.append(f"  {formatted_key}: {'Yes' if value else 'No'}")
            else:
                report.append(f"  {formatted_key}: {value:.4f}")
        report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS:")
    
    if traj_metrics.get('max_position_error', 0) > 0.1:
        report.append("  - Consider increasing control gains to reduce tracking error")
    
    if traj_metrics.get('settling_time', 0) > trajectory_data['time'].iloc[-1] * 0.8:
        report.append("  - System takes long to settle - consider adjusting damping")
    
    if energy_metrics.get('peak_power', 0) > energy_metrics.get('average_power', 0) * 5:
        report.append("  - High power peaks detected - consider smoother trajectories")
    
    if stability_analysis.get('oscillation_frequency', 0) > 0.5:
        report.append("  - High oscillation frequency - reduce derivative gain")
    
    if not stability_analysis.get('converged', True):
        report.append("  - System did not converge - check control parameters")
    
    report.append("")
    report.append("=" * 50)
    
    return "\n".join(report)

def create_parameter_sensitivity_analysis(base_params: Dict[str, Any], 
                                        param_variations: Dict[str, List[float]]) -> Dict[str, Any]:
    """
    Create parameter sensitivity analysis data
    
    Args:
        base_params: Base robot parameters
        param_variations: Dictionary of parameters and their variation values
        
    Returns:
        Dictionary containing sensitivity analysis data
    """
    sensitivity_data = {
        'parameters': list(param_variations.keys()),
        'variations': param_variations,
        'base_values': {param: base_params[param] for param in param_variations.keys()}
    }
    
    return sensitivity_data

