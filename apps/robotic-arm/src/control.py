import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class ControllerParams:
    """Parameters for PID controller"""
    kp: List[float]  # Proportional gains for each joint
    ki: List[float]  # Integral gains for each joint
    kd: List[float]  # Derivative gains for each joint
    dt: float        # Time step
    output_limits: Optional[List[Tuple[float, float]]] = None  # Output saturation limits

class PIDController:
    """
    Multi-joint PID Controller for robotic arm
    
    Implements PID control for each joint independently with anti-windup
    and output saturation capabilities.
    """
    
    def __init__(self, kp: List[float], ki: List[float], kd: List[float], 
                 dt: float, output_limits: Optional[List[Tuple[float, float]]] = None):
        """
        Initialize PID controller
        
        Args:
            kp: Proportional gains for each joint
            ki: Integral gains for each joint  
            kd: Derivative gains for each joint
            dt: Time step (s)
            output_limits: Optional output saturation limits [(min1, max1), (min2, max2)]
        """
        self.kp = np.array(kp)
        self.ki = np.array(ki)
        self.kd = np.array(kd)
        self.dt = dt
        self.output_limits = output_limits
        
        # Number of joints
        self.n_joints = len(kp)
        
        # Internal state variables
        self.reset()
    
    def reset(self):
        """Reset controller internal state"""
        self.integral_error = np.zeros(self.n_joints)
        self.previous_error = np.zeros(self.n_joints)
        self.previous_output = np.zeros(self.n_joints)
        self.first_call = True
    
    def compute_control(self, error: np.ndarray, error_dot: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute PID control output
        
        Args:
            error: Position error for each joint [e1, e2, ...]
            error_dot: Optional velocity error (if None, computed numerically)
            
        Returns:
            Control output (torques) for each joint
        """
        error = np.array(error)
        
        # Compute derivative of error
        if error_dot is None:
            if self.first_call:
                derivative_error = np.zeros(self.n_joints)
                self.first_call = False
            else:
                derivative_error = (error - self.previous_error) / self.dt
        else:
            derivative_error = np.array(error_dot)
        
        # Update integral with anti-windup
        self.integral_error += error * self.dt
        
        # Compute PID output
        output = (self.kp * error + 
                 self.ki * self.integral_error + 
                 self.kd * derivative_error)
        
        # Apply output limits if specified
        if self.output_limits is not None:
            for i in range(self.n_joints):
                if self.output_limits[i] is not None:
                    min_limit, max_limit = self.output_limits[i]
                    
                    # Store unlimited output for anti-windup
                    unlimited_output = output[i]
                    
                    # Apply saturation
                    output[i] = np.clip(output[i], min_limit, max_limit)
                    
                    # Anti-windup: adjust integral term if output is saturated
                    if output[i] != unlimited_output and self.ki[i] != 0:
                        # Back-calculate integral term to prevent windup
                        integral_adjustment = (output[i] - (self.kp[i] * error[i] + 
                                                          self.kd[i] * derivative_error[i])) / self.ki[i]
                        self.integral_error[i] = integral_adjustment
        
        # Store current values for next iteration
        self.previous_error = error.copy()
        self.previous_output = output.copy()
        
        return output
    
    def tune_parameters(self, kp: Optional[List[float]] = None, 
                       ki: Optional[List[float]] = None, 
                       kd: Optional[List[float]] = None):
        """
        Update controller parameters
        
        Args:
            kp: New proportional gains (if provided)
            ki: New integral gains (if provided)
            kd: New derivative gains (if provided)
        """
        if kp is not None:
            self.kp = np.array(kp)
        if ki is not None:
            self.ki = np.array(ki)
            # Reset integral error when Ki changes
            self.integral_error = np.zeros(self.n_joints)
        if kd is not None:
            self.kd = np.array(kd)
    
    def get_control_signals(self, error: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get individual P, I, D components of control signal
        
        Args:
            error: Current error vector
            
        Returns:
            Tuple of (P_term, I_term, D_term)
        """
        error = np.array(error)
        
        if self.first_call:
            derivative_error = np.zeros(self.n_joints)
        else:
            derivative_error = (error - self.previous_error) / self.dt
        
        P_term = self.kp * error
        I_term = self.ki * self.integral_error
        D_term = self.kd * derivative_error
        
        return P_term, I_term, D_term

class ComputedTorqueController:
    """
    Computed Torque Controller for robotic arm
    
    Implements model-based control using inverse dynamics with PID feedback.
    """
    
    def __init__(self, robot_dynamics, kp: List[float], kd: List[float]):
        """
        Initialize computed torque controller
        
        Args:
            robot_dynamics: RobotDynamics instance
            kp: Proportional gains for error feedback
            kd: Derivative gains for error feedback
        """
        self.dynamics = robot_dynamics
        self.kp = np.array(kp)
        self.kd = np.array(kd)
    
    def compute_control(self, current_state: np.ndarray, desired_state: np.ndarray, 
                       desired_velocity: np.ndarray, desired_acceleration: np.ndarray) -> np.ndarray:
        """
        Compute control torques using computed torque method
        
        Args:
            current_state: Current state [q1, q2, q1_dot, q2_dot]
            desired_state: Desired joint positions [q1_d, q2_d]
            desired_velocity: Desired joint velocities [q1_dot_d, q2_dot_d]
            desired_acceleration: Desired joint accelerations [q1_ddot_d, q2_ddot_d]
            
        Returns:
            Control torques [tau1, tau2]
        """
        q = current_state[:2]
        q_dot = current_state[2:]
        
        # Position and velocity errors
        e_pos = desired_state - q
        e_vel = desired_velocity - q_dot
        
        # Desired acceleration with feedback
        q_ddot_desired = desired_acceleration + self.kd * e_vel + self.kp * e_pos
        
        # Compute required torques using inverse dynamics
        torques = self.dynamics.inverse_dynamics(
            q[0], q[1], q_dot[0], q_dot[1], 
            q_ddot_desired[0], q_ddot_desired[1]
        )
        
        return torques

class AdaptiveController:
    """
    Adaptive Controller with parameter estimation
    
    Implements adaptive control for handling model uncertainties.
    """
    
    def __init__(self, nominal_dynamics, adaptation_gains: List[float], 
                 kp: List[float], kd: List[float]):
        """
        Initialize adaptive controller
        
        Args:
            nominal_dynamics: Nominal robot dynamics model
            adaptation_gains: Adaptation rates for parameter estimation
            kp: Proportional feedback gains
            kd: Derivative feedback gains
        """
        self.nominal_dynamics = nominal_dynamics
        self.gamma = np.array(adaptation_gains)
        self.kp = np.array(kp)
        self.kd = np.array(kd)
        
        # Estimated parameters (simplified - only mass parameters)
        self.estimated_params = np.ones(4)  # [m1_est, m2_est, I1_est, I2_est]
        
    def compute_control(self, current_state: np.ndarray, desired_state: np.ndarray,
                       desired_velocity: np.ndarray, desired_acceleration: np.ndarray) -> np.ndarray:
        """
        Compute adaptive control with parameter update
        
        Args:
            current_state: Current state [q1, q2, q1_dot, q2_dot]
            desired_state: Desired positions [q1_d, q2_d]
            desired_velocity: Desired velocities [q1_dot_d, q2_dot_d]
            desired_acceleration: Desired accelerations [q1_ddot_d, q2_ddot_d]
            
        Returns:
            Control torques [tau1, tau2]
        """
        q = current_state[:2]
        q_dot = current_state[2:]
        
        # Tracking errors
        e_pos = desired_state - q
        e_vel = desired_velocity - q_dot
        
        # Reference acceleration
        q_ddot_ref = desired_acceleration + self.kd * e_vel + self.kp * e_pos
        
        # Compute control using estimated parameters
        # (Simplified implementation - full adaptive control would use regressor matrix)
        torques = self.nominal_dynamics.inverse_dynamics(
            q[0], q[1], q_dot[0], q_dot[1], q_ddot_ref[0], q_ddot_ref[1]
        )
        
        # Parameter adaptation (simplified)
        # In practice, this would use the regressor matrix and prediction error
        prediction_error = np.linalg.norm(e_pos)
        if prediction_error > 0.01:  # Threshold for adaptation
            self.estimated_params += self.gamma * prediction_error * 0.001
        
        return torques

class RobustController:
    """
    Robust Controller using sliding mode control
    
    Implements sliding mode control for robustness against uncertainties.
    """
    
    def __init__(self, robot_dynamics, lambda_gains: List[float], 
                 k_gains: List[float], boundary_thickness: float = 0.1):
        """
        Initialize robust sliding mode controller
        
        Args:
            robot_dynamics: RobotDynamics instance
            lambda_gains: Sliding surface parameters
            k_gains: Switching gains
            boundary_thickness: Boundary layer thickness for chattering reduction
        """
        self.dynamics = robot_dynamics
        self.lambda_gains = np.array(lambda_gains)
        self.k_gains = np.array(k_gains)
        self.phi = boundary_thickness
    
    def compute_control(self, current_state: np.ndarray, desired_state: np.ndarray,
                       desired_velocity: np.ndarray, desired_acceleration: np.ndarray) -> np.ndarray:
        """
        Compute sliding mode control torques
        
        Args:
            current_state: Current state [q1, q2, q1_dot, q2_dot]
            desired_state: Desired positions [q1_d, q2_d]
            desired_velocity: Desired velocities [q1_dot_d, q2_dot_d]
            desired_acceleration: Desired accelerations [q1_ddot_d, q2_ddot_d]
            
        Returns:
            Control torques [tau1, tau2]
        """
        q = current_state[:2]
        q_dot = current_state[2:]
        
        # Tracking errors
        e_pos = desired_state - q
        e_vel = desired_velocity - q_dot
        
        # Sliding variable
        s = e_vel + self.lambda_gains * e_pos
        
        # Equivalent control
        q_ddot_eq = desired_acceleration + self.lambda_gains * e_vel
        tau_eq = self.dynamics.inverse_dynamics(
            q[0], q[1], q_dot[0], q_dot[1], q_ddot_eq[0], q_ddot_eq[1]
        )
        
        # Switching control with boundary layer
        sat_s = np.zeros_like(s)
        for i in range(len(s)):
            if abs(s[i]) <= self.phi:
                sat_s[i] = s[i] / self.phi
            else:
                sat_s[i] = np.sign(s[i])
        
        tau_switch = -self.k_gains * sat_s
        
        return tau_eq + tau_switch

class ControllerTester:
    """
    Utility class for testing and comparing different controllers
    """
    
    def __init__(self, robot_dynamics):
        """
        Initialize controller tester
        
        Args:
            robot_dynamics: RobotDynamics instance
        """
        self.dynamics = robot_dynamics
    
    def test_step_response(self, controller, initial_state: np.ndarray, 
                          target_position: np.ndarray, duration: float, dt: float = 0.01) -> dict:
        """
        Test controller step response
        
        Args:
            controller: Controller instance
            initial_state: Initial state [q1, q2, q1_dot, q2_dot]
            target_position: Target joint positions [q1_target, q2_target]
            duration: Test duration (s)
            dt: Time step (s)
            
        Returns:
            Dictionary containing test results
        """
        # Initialize simulation
        time_steps = int(duration / dt)
        time_array = np.linspace(0, duration, time_steps)
        
        # Storage arrays
        states = np.zeros((time_steps, 4))
        torques = np.zeros((time_steps, 2))
        errors = np.zeros((time_steps, 2))
        
        # Initial conditions
        current_state = initial_state.copy()
        states[0] = current_state
        
        # Reset controller if it has reset method
        if hasattr(controller, 'reset'):
            controller.reset()
        
        # Simulation loop
        for i in range(1, time_steps):
            # Compute control
            if isinstance(controller, PIDController):
                error = target_position - current_state[:2]
                tau = controller.compute_control(error)
            else:
                # For other controllers, provide zero desired velocity and acceleration
                tau = controller.compute_control(
                    current_state, target_position, 
                    np.zeros(2), np.zeros(2)
                )
            
            # Forward dynamics
            accelerations = self.dynamics.forward_dynamics(current_state, tau)
            
            # Integrate (simple Euler integration)
            current_state[2:] += accelerations * dt  # Update velocities
            current_state[:2] += current_state[2:] * dt  # Update positions
            
            # Store results
            states[i] = current_state
            torques[i] = tau
            errors[i] = target_position - current_state[:2]
        
        # Compute performance metrics
        position_error = np.linalg.norm(errors, axis=1)
        settling_time = self._compute_settling_time(position_error, dt)
        overshoot = self._compute_overshoot(states[:, :2], target_position)
        steady_state_error = np.mean(position_error[-50:])  # Last 50 samples
        
        return {
            'time': time_array,
            'states': states,
            'torques': torques,
            'errors': errors,
            'position_error': position_error,
            'settling_time': settling_time,
            'overshoot': overshoot,
            'steady_state_error': steady_state_error
        }
    
    def _compute_settling_time(self, error_signal: np.ndarray, dt: float, 
                              tolerance: float = 0.02) -> float:
        """Compute settling time (2% criterion)"""
        final_value = error_signal[-1]
        tolerance_band = abs(final_value) + tolerance
        
        for i in range(len(error_signal) - 1, -1, -1):
            if abs(error_signal[i]) > tolerance_band:
                return (i + 1) * dt
        
        return 0.0
    
    def _compute_overshoot(self, position_history: np.ndarray, 
                          target: np.ndarray) -> float:
        """Compute maximum overshoot percentage"""
        max_overshoot = 0.0
        
        for joint in range(2):
            if target[joint] != 0:
                max_pos = np.max(position_history[:, joint])
                overshoot = abs((max_pos - target[joint]) / target[joint]) * 100
                max_overshoot = max(max_overshoot, overshoot)
        
        return max_overshoot
