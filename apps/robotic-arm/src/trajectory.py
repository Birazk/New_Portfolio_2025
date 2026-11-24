import numpy as np
from typing import List, Tuple, Callable, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import scipy.interpolate as interp

@dataclass
class TrajectoryPoint:
    """Single point in a trajectory"""
    time: float
    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray

class Trajectory(ABC):
    """Abstract base class for trajectories"""
    
    def __init__(self, duration: float):
        self.duration = duration
    
    @abstractmethod
    def __call__(self, t: float) -> np.ndarray:
        """Get position at time t"""
        pass
    
    @abstractmethod
    def velocity(self, t: float) -> np.ndarray:
        """Get velocity at time t"""
        pass
    
    @abstractmethod
    def acceleration(self, t: float) -> np.ndarray:
        """Get acceleration at time t"""
        pass

class PolynomialTrajectory(Trajectory):
    """
    Polynomial trajectory with position, velocity, and acceleration continuity
    """
    
    def __init__(self, waypoints: List[np.ndarray], times: List[float], 
                 initial_velocity: Optional[np.ndarray] = None,
                 final_velocity: Optional[np.ndarray] = None):
        """
        Initialize polynomial trajectory
        
        Args:
            waypoints: List of position waypoints
            times: Time at each waypoint
            initial_velocity: Initial velocity (default: zero)
            final_velocity: Final velocity (default: zero)
        """
        super().__init__(times[-1])
        
        self.waypoints = [np.array(wp) for wp in waypoints]
        self.times = np.array(times)
        self.n_dims = len(self.waypoints[0])
        
        if initial_velocity is None:
            initial_velocity = np.zeros(self.n_dims)
        if final_velocity is None:
            final_velocity = np.zeros(self.n_dims)
        
        self.initial_velocity = np.array(initial_velocity)
        self.final_velocity = np.array(final_velocity)
        
        # Generate polynomial coefficients
        self._generate_polynomials()
    
    def _generate_polynomials(self):
        """Generate polynomial coefficients for smooth trajectory"""
        n_segments = len(self.waypoints) - 1
        self.polynomials = []
        
        for dim in range(self.n_dims):
            # Extract positions for this dimension
            positions = [wp[dim] for wp in self.waypoints]
            
            # Create spline with velocity constraints
            velocities = [0] * len(positions)
            velocities[0] = self.initial_velocity[dim]
            velocities[-1] = self.final_velocity[dim]
            
            # Use scipy's PchipInterpolator for smooth interpolation
            spline = interp.PchipInterpolator(self.times, positions)
            self.polynomials.append(spline)
    
    def __call__(self, t: float) -> np.ndarray:
        """Get position at time t"""
        t = np.clip(t, 0, self.duration)
        position = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            position[dim] = self.polynomials[dim](t)
        
        return position
    
    def velocity(self, t: float) -> np.ndarray:
        """Get velocity at time t"""
        t = np.clip(t, 0, self.duration)
        velocity = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            velocity[dim] = self.polynomials[dim](t, 1)  # First derivative
        
        return velocity
    
    def acceleration(self, t: float) -> np.ndarray:
        """Get acceleration at time t"""
        t = np.clip(t, 0, self.duration)
        acceleration = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            acceleration[dim] = self.polynomials[dim](t, 2)  # Second derivative
        
        return acceleration

class QuinticPolynomialTrajectory(Trajectory):
    """
    Quintic polynomial trajectory for point-to-point motion
    """
    
    def __init__(self, start_pos: np.ndarray, end_pos: np.ndarray, duration: float,
                 start_vel: Optional[np.ndarray] = None, end_vel: Optional[np.ndarray] = None,
                 start_acc: Optional[np.ndarray] = None, end_acc: Optional[np.ndarray] = None):
        """
        Initialize quintic polynomial trajectory
        
        Args:
            start_pos: Starting position
            end_pos: Ending position
            duration: Trajectory duration
            start_vel: Starting velocity (default: zero)
            end_vel: Ending velocity (default: zero)
            start_acc: Starting acceleration (default: zero)
            end_acc: Ending acceleration (default: zero)
        """
        super().__init__(duration)
        
        self.start_pos = np.array(start_pos)
        self.end_pos = np.array(end_pos)
        self.n_dims = len(self.start_pos)
        
        # Default to zero if not specified
        self.start_vel = np.zeros(self.n_dims) if start_vel is None else np.array(start_vel)
        self.end_vel = np.zeros(self.n_dims) if end_vel is None else np.array(end_vel)
        self.start_acc = np.zeros(self.n_dims) if start_acc is None else np.array(start_acc)
        self.end_acc = np.zeros(self.n_dims) if end_acc is None else np.array(end_acc)
        
        # Compute polynomial coefficients
        self._compute_coefficients()
    
    def _compute_coefficients(self):
        """Compute quintic polynomial coefficients"""
        # For each dimension, solve for 6 coefficients (a0 to a5)
        # q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5
        
        T = self.duration
        self.coefficients = np.zeros((self.n_dims, 6))
        
        for dim in range(self.n_dims):
            # Boundary conditions
            q0 = self.start_pos[dim]
            qf = self.end_pos[dim]
            v0 = self.start_vel[dim]
            vf = self.end_vel[dim]
            a0 = self.start_acc[dim]
            af = self.end_acc[dim]
            
            # Solve linear system for coefficients
            # [1  0   0    0     0     0  ] [a0]   [q0]
            # [0  1   0    0     0     0  ] [a1]   [v0]
            # [0  0   2    0     0     0  ] [a2]   [a0]
            # [1  T   T^2  T^3   T^4   T^5] [a3] = [qf]
            # [0  1   2T   3T^2  4T^3  5T^4] [a4]   [vf]
            # [0  0   2    6T    12T^2 20T^3] [a5]   [af]
            
            A = np.array([
                [1, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 2, 0, 0, 0],
                [1, T, T**2, T**3, T**4, T**5],
                [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],
                [0, 0, 2, 6*T, 12*T**2, 20*T**3]
            ])
            
            b = np.array([q0, v0, a0, qf, vf, af])
            
            self.coefficients[dim] = np.linalg.solve(A, b)
    
    def __call__(self, t: float) -> np.ndarray:
        """Get position at time t"""
        t = np.clip(t, 0, self.duration)
        position = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            coeffs = self.coefficients[dim]
            position[dim] = (coeffs[0] + coeffs[1]*t + coeffs[2]*t**2 + 
                           coeffs[3]*t**3 + coeffs[4]*t**4 + coeffs[5]*t**5)
        
        return position
    
    def velocity(self, t: float) -> np.ndarray:
        """Get velocity at time t"""
        t = np.clip(t, 0, self.duration)
        velocity = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            coeffs = self.coefficients[dim]
            velocity[dim] = (coeffs[1] + 2*coeffs[2]*t + 3*coeffs[3]*t**2 + 
                           4*coeffs[4]*t**3 + 5*coeffs[5]*t**4)
        
        return velocity
    
    def acceleration(self, t: float) -> np.ndarray:
        """Get acceleration at time t"""
        t = np.clip(t, 0, self.duration)
        acceleration = np.zeros(self.n_dims)
        
        for dim in range(self.n_dims):
            coeffs = self.coefficients[dim]
            acceleration[dim] = (2*coeffs[2] + 6*coeffs[3]*t + 
                               12*coeffs[4]*t**2 + 20*coeffs[5]*t**3)
        
        return acceleration

class CircularTrajectory(Trajectory):
    """
    Circular trajectory in 2D space
    """
    
    def __init__(self, center: List[float], radius: float, duration: float, 
                 start_angle: float = 0.0, clockwise: bool = False):
        """
        Initialize circular trajectory
        
        Args:
            center: Center of circle [x, y]
            radius: Circle radius
            duration: Time to complete the circle
            start_angle: Starting angle (rad)
            clockwise: Direction of motion
        """
        super().__init__(duration)
        
        self.center = np.array(center)
        self.radius = radius
        self.start_angle = start_angle
        self.angular_velocity = 2 * np.pi / duration
        
        if clockwise:
            self.angular_velocity *= -1
    
    def __call__(self, t: float) -> np.ndarray:
        """Get position at time t"""
        t = np.clip(t, 0, self.duration)
        angle = self.start_angle + self.angular_velocity * t
        
        x = self.center[0] + self.radius * np.cos(angle)
        y = self.center[1] + self.radius * np.sin(angle)
        
        return np.array([x, y])
    
    def velocity(self, t: float) -> np.ndarray:
        """Get velocity at time t"""
        t = np.clip(t, 0, self.duration)
        angle = self.start_angle + self.angular_velocity * t
        
        vx = -self.radius * self.angular_velocity * np.sin(angle)
        vy = self.radius * self.angular_velocity * np.cos(angle)
        
        return np.array([vx, vy])
    
    def acceleration(self, t: float) -> np.ndarray:
        """Get acceleration at time t"""
        t = np.clip(t, 0, self.duration)
        angle = self.start_angle + self.angular_velocity * t
        
        ax = -self.radius * self.angular_velocity**2 * np.cos(angle)
        ay = -self.radius * self.angular_velocity**2 * np.sin(angle)
        
        return np.array([ax, ay])

class FigureEightTrajectory(Trajectory):
    """
    Figure-8 trajectory in 2D space
    """
    
    def __init__(self, center: List[float], scale: float, duration: float):
        """
        Initialize figure-8 trajectory
        
        Args:
            center: Center of figure-8 [x, y]
            scale: Scaling factor for figure-8 size
            duration: Time to complete one figure-8
        """
        super().__init__(duration)
        
        self.center = np.array(center)
        self.scale = scale
        self.omega = 2 * np.pi / duration
    
    def __call__(self, t: float) -> np.ndarray:
        """Get position at time t"""
        t = np.clip(t, 0, self.duration)
        
        # Parametric equations for figure-8 (lemniscate)
        omega_t = self.omega * t
        
        x = self.center[0] + self.scale * np.sin(omega_t)
        y = self.center[1] + self.scale * np.sin(omega_t) * np.cos(omega_t)
        
        return np.array([x, y])
    
    def velocity(self, t: float) -> np.ndarray:
        """Get velocity at time t"""
        t = np.clip(t, 0, self.duration)
        omega_t = self.omega * t
        
        vx = self.scale * self.omega * np.cos(omega_t)
        vy = self.scale * self.omega * (np.cos(omega_t)**2 - np.sin(omega_t)**2)
        
        return np.array([vx, vy])
    
    def acceleration(self, t: float) -> np.ndarray:
        """Get acceleration at time t"""
        t = np.clip(t, 0, self.duration)
        omega_t = self.omega * t
        
        ax = -self.scale * self.omega**2 * np.sin(omega_t)
        ay = -4 * self.scale * self.omega**2 * np.sin(omega_t) * np.cos(omega_t)
        
        return np.array([ax, ay])

class TrajectoryPlanner:
    """
    High-level trajectory planning utilities
    """
    
    def __init__(self):
        pass
    
    def point_to_point(self, start: List[float], end: List[float], duration: float,
                      start_vel: Optional[List[float]] = None, 
                      end_vel: Optional[List[float]] = None) -> QuinticPolynomialTrajectory:
        """
        Generate point-to-point trajectory
        
        Args:
            start: Starting position
            end: Ending position
            duration: Trajectory duration
            start_vel: Starting velocity (optional)
            end_vel: Ending velocity (optional)
            
        Returns:
            QuinticPolynomialTrajectory instance
        """
        return QuinticPolynomialTrajectory(start, end, duration, start_vel, end_vel)
    
    def circular_trajectory(self, center: List[float], radius: float, 
                           duration: float, **kwargs) -> CircularTrajectory:
        """
        Generate circular trajectory
        
        Args:
            center: Center of circle
            radius: Circle radius
            duration: Duration for one complete circle
            **kwargs: Additional arguments for CircularTrajectory
            
        Returns:
            CircularTrajectory instance
        """
        return CircularTrajectory(center, radius, duration, **kwargs)
    
    def figure_eight_trajectory(self, center: List[float], scale: float, 
                               duration: float) -> FigureEightTrajectory:
        """
        Generate figure-8 trajectory
        
        Args:
            center: Center of figure-8
            scale: Size scaling factor
            duration: Duration for one complete figure-8
            
        Returns:
            FigureEightTrajectory instance
        """
        return FigureEightTrajectory(center, scale, duration)
    
    def multi_waypoint_trajectory(self, waypoints: List[List[float]], 
                                 segment_durations: List[float],
                                 velocity_constraints: Optional[List[List[float]]] = None) -> PolynomialTrajectory:
        """
        Generate multi-waypoint trajectory
        
        Args:
            waypoints: List of waypoint positions
            segment_durations: Duration for each segment
            velocity_constraints: Velocity constraints at waypoints (optional)
            
        Returns:
            PolynomialTrajectory instance
        """
        # Calculate cumulative times
        times = [0.0]
        for duration in segment_durations:
            times.append(times[-1] + duration)
        
        # Set velocity constraints
        initial_vel = None
        final_vel = None
        if velocity_constraints:
            initial_vel = velocity_constraints[0]
            final_vel = velocity_constraints[-1]
        
        return PolynomialTrajectory(waypoints, times, initial_vel, final_vel)
    
    def minimum_jerk_trajectory(self, start: List[float], end: List[float], 
                               duration: float) -> QuinticPolynomialTrajectory:
        """
        Generate minimum jerk trajectory (zero velocity and acceleration at endpoints)
        
        Args:
            start: Starting position
            end: Ending position
            duration: Trajectory duration
            
        Returns:
            QuinticPolynomialTrajectory instance
        """
        return QuinticPolynomialTrajectory(
            start, end, duration,
            start_vel=np.zeros(len(start)),
            end_vel=np.zeros(len(end)),
            start_acc=np.zeros(len(start)),
            end_acc=np.zeros(len(end))
        )
    
    def trapezoidal_velocity_trajectory(self, start: List[float], end: List[float],
                                       max_velocity: float, acceleration: float) -> Trajectory:
        """
        Generate trapezoidal velocity profile trajectory
        
        Args:
            start: Starting position
            end: Ending position
            max_velocity: Maximum velocity
            acceleration: Acceleration/deceleration
            
        Returns:
            Trajectory instance
        """
        start = np.array(start)
        end = np.array(end)
        distance = np.linalg.norm(end - start)
        direction = (end - start) / distance if distance > 0 else np.zeros_like(start)
        
        # Calculate trajectory timing
        t_accel = max_velocity / acceleration
        d_accel = 0.5 * acceleration * t_accel**2
        
        if 2 * d_accel >= distance:
            # Triangular profile (no constant velocity phase)
            t_accel = np.sqrt(distance / acceleration)
            t_const = 0
            total_time = 2 * t_accel
        else:
            # Trapezoidal profile
            d_const = distance - 2 * d_accel
            t_const = d_const / max_velocity
            total_time = 2 * t_accel + t_const
        
        class TrapezoidalTrajectory(Trajectory):
            def __init__(self, start_pos, end_pos, direction, t_accel, t_const, total_time, max_vel, accel):
                super().__init__(total_time)
                self.start_pos = start_pos
                self.end_pos = end_pos
                self.direction = direction
                self.t_accel = t_accel
                self.t_const = t_const
                self.max_vel = max_vel
                self.accel = accel
                self.t_decel_start = t_accel + t_const
            
            def __call__(self, t):
                t = np.clip(t, 0, self.duration)
                
                if t <= self.t_accel:
                    # Acceleration phase
                    distance = 0.5 * self.accel * t**2
                elif t <= self.t_decel_start:
                    # Constant velocity phase
                    d_accel = 0.5 * self.accel * self.t_accel**2
                    distance = d_accel + self.max_vel * (t - self.t_accel)
                else:
                    # Deceleration phase
                    t_decel = t - self.t_decel_start
                    d_accel = 0.5 * self.accel * self.t_accel**2
                    d_const = self.max_vel * self.t_const
                    distance = d_accel + d_const + self.max_vel * t_decel - 0.5 * self.accel * t_decel**2
                
                return self.start_pos + distance * self.direction
            
            def velocity(self, t):
                t = np.clip(t, 0, self.duration)
                
                if t <= self.t_accel:
                    speed = self.accel * t
                elif t <= self.t_decel_start:
                    speed = self.max_vel
                else:
                    t_decel = t - self.t_decel_start
                    speed = self.max_vel - self.accel * t_decel
                
                return speed * self.direction
            
            def acceleration(self, t):
                t = np.clip(t, 0, self.duration)
                
                if t <= self.t_accel:
                    accel = self.accel
                elif t <= self.t_decel_start:
                    accel = 0
                else:
                    accel = -self.accel
                
                return accel * self.direction
        
        return TrapezoidalTrajectory(start, end, direction, t_accel, t_const, 
                                   total_time, max_velocity, acceleration)
    
    def optimize_trajectory_time(self, waypoints: List[List[float]], 
                                max_velocity: List[float], max_acceleration: List[float]) -> Tuple[List[float], float]:
        """
        Optimize trajectory timing to minimize total time while respecting constraints
        
        Args:
            waypoints: List of waypoint positions
            max_velocity: Maximum velocity constraints for each dimension
            max_acceleration: Maximum acceleration constraints for each dimension
            
        Returns:
            Tuple of (optimal_segment_durations, total_time)
        """
        n_segments = len(waypoints) - 1
        segment_durations = []
        
        for i in range(n_segments):
            start = np.array(waypoints[i])
            end = np.array(waypoints[i + 1])
            
            # Calculate minimum time for each dimension
            min_times = []
            
            for dim in range(len(start)):
                distance = abs(end[dim] - start[dim])
                
                if distance == 0:
                    min_times.append(0.1)  # Minimum non-zero time
                    continue
                
                # Time based on velocity constraint
                t_vel = distance / max_velocity[dim]
                
                # Time based on acceleration constraint (triangular profile)
                t_acc = 2 * np.sqrt(distance / max_acceleration[dim])
                
                min_times.append(max(t_vel, t_acc))
            
            # Use maximum time across all dimensions
            segment_durations.append(max(min_times))
        
        total_time = sum(segment_durations)
        
        return segment_durations, total_time
