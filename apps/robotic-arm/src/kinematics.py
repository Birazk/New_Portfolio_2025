import numpy as np
from typing import List, Tuple, Optional
import sympy as sp

class RobotKinematics:
    """
    2DOF Robotic Arm Kinematics
    
    This class implements forward and inverse kinematics for a 2-degree-of-freedom
    planar robotic arm with revolute joints.
    """
    
    def __init__(self, l1: float, l2: float):
        """
        Initialize the kinematics model
        
        Args:
            l1: Length of first link (m)
            l2: Length of second link (m)
        """
        self.l1 = l1
        self.l2 = l2
        
        # Create symbolic variables for analytical solutions
        self._setup_symbolic_model()
    
    def _setup_symbolic_model(self):
        """Setup symbolic mathematical model using SymPy"""
        self.q1_sym, self.q2_sym = sp.symbols('q1 q2')
        self.l1_sym, self.l2_sym = sp.symbols('l1 l2', positive=True)
        
        # Symbolic forward kinematics
        self.x_sym = self.l1_sym * sp.cos(self.q1_sym) + self.l2_sym * sp.cos(self.q1_sym + self.q2_sym)
        self.y_sym = self.l1_sym * sp.sin(self.q1_sym) + self.l2_sym * sp.sin(self.q1_sym + self.q2_sym)
        
        # Compute Jacobian symbolically
        self.J_sym = sp.Matrix([
            [sp.diff(self.x_sym, self.q1_sym), sp.diff(self.x_sym, self.q2_sym)],
            [sp.diff(self.y_sym, self.q1_sym), sp.diff(self.y_sym, self.q2_sym)]
        ])
        
        # Create numerical functions
        self._create_numerical_functions()
    
    def _create_numerical_functions(self):
        """Create fast numerical functions from symbolic expressions"""
        # Forward kinematics functions
        self.x_func = sp.lambdify((self.q1_sym, self.q2_sym, self.l1_sym, self.l2_sym), self.x_sym, 'numpy')
        self.y_func = sp.lambdify((self.q1_sym, self.q2_sym, self.l1_sym, self.l2_sym), self.y_sym, 'numpy')
        
        # Jacobian function
        self.jacobian_func = sp.lambdify((self.q1_sym, self.q2_sym, self.l1_sym, self.l2_sym), self.J_sym, 'numpy')
    
    def forward_kinematics(self, q1: float, q2: float) -> np.ndarray:
        """
        Compute forward kinematics
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            End-effector position [x, y] in meters
        """
        x = self.l1 * np.cos(q1) + self.l2 * np.cos(q1 + q2)
        y = self.l1 * np.sin(q1) + self.l2 * np.sin(q1 + q2)
        
        return np.array([x, y])
    
    def get_joint_positions(self, q1: float, q2: float) -> List[np.ndarray]:
        """
        Get positions of all joints for visualization
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            List of joint positions: [base, joint1, joint2/end-effector]
        """
        # Base position (origin)
        base = np.array([0.0, 0.0])
        
        # Joint 1 position (end of first link)
        joint1 = np.array([
            self.l1 * np.cos(q1),
            self.l1 * np.sin(q1)
        ])
        
        # End-effector position (end of second link)
        end_effector = self.forward_kinematics(q1, q2)
        
        return [base, joint1, end_effector]
    
    def inverse_kinematics(self, x: float, y: float) -> List[Tuple[float, float]]:
        """
        Compute inverse kinematics (analytical solution)
        
        Args:
            x: Target x position (m)
            y: Target y position (m)
            
        Returns:
            List of solutions [(q1, q2), ...]. Each solution is a tuple of joint angles.
            
        Raises:
            ValueError: If target is unreachable
        """
        # Check if target is reachable
        distance = np.sqrt(x**2 + y**2)
        max_reach = self.l1 + self.l2
        min_reach = abs(self.l1 - self.l2)
        
        if distance > max_reach or distance < min_reach:
            raise ValueError(f"Target ({x:.3f}, {y:.3f}) is unreachable. "
                           f"Distance: {distance:.3f}, Range: [{min_reach:.3f}, {max_reach:.3f}]")
        
        # Analytical inverse kinematics solution
        solutions = []
        
        # Calculate q2 using law of cosines
        cos_q2 = (x**2 + y**2 - self.l1**2 - self.l2**2) / (2 * self.l1 * self.l2)
        
        # Clamp to valid range to handle numerical errors
        cos_q2 = np.clip(cos_q2, -1.0, 1.0)
        
        # Two possible solutions for q2
        q2_solutions = [np.arccos(cos_q2), -np.arccos(cos_q2)]
        
        for q2 in q2_solutions:
            # Calculate corresponding q1
            k1 = self.l1 + self.l2 * np.cos(q2)
            k2 = self.l2 * np.sin(q2)
            
            # Avoid division by zero
            if abs(k1) < 1e-6 and abs(k2) < 1e-6:
                continue
                
            q1 = np.arctan2(y, x) - np.arctan2(k2, k1)
            
            # Normalize angles to [-pi, pi]
            q1 = self._normalize_angle(q1)
            q2 = self._normalize_angle(q2)
            
            solutions.append((q1, q2))
        
        if not solutions:
            raise ValueError("No valid inverse kinematics solution found")
        
        return solutions
    
    def _normalize_angle(self, angle: float) -> float:
        """Normalize angle to [-pi, pi] range"""
        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi
        return angle
    
    def compute_jacobian(self, q1: float, q2: float) -> np.ndarray:
        """
        Compute the Jacobian matrix
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            2x2 Jacobian matrix
        """
        # Partial derivatives of end-effector position w.r.t. joint angles
        j11 = -self.l1 * np.sin(q1) - self.l2 * np.sin(q1 + q2)  # dx/dq1
        j12 = -self.l2 * np.sin(q1 + q2)                          # dx/dq2
        j21 = self.l1 * np.cos(q1) + self.l2 * np.cos(q1 + q2)   # dy/dq1
        j22 = self.l2 * np.cos(q1 + q2)                           # dy/dq2
        
        return np.array([[j11, j12], [j21, j22]])
    
    def compute_manipulability(self, q1: float, q2: float) -> float:
        """
        Compute manipulability index (Yoshikawa's measure)
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            Manipulability index (scalar)
        """
        J = self.compute_jacobian(q1, q2)
        return np.sqrt(np.linalg.det(J @ J.T))
    
    def velocity_kinematics(self, q1: float, q2: float, q1_dot: float, q2_dot: float) -> np.ndarray:
        """
        Compute end-effector velocity from joint velocities
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            q1_dot: Joint 1 velocity (rad/s)
            q2_dot: Joint 2 velocity (rad/s)
            
        Returns:
            End-effector velocity [vx, vy] in m/s
        """
        J = self.compute_jacobian(q1, q2)
        joint_velocities = np.array([q1_dot, q2_dot])
        
        return J @ joint_velocities
    
    def inverse_velocity_kinematics(self, q1: float, q2: float, vx: float, vy: float) -> np.ndarray:
        """
        Compute joint velocities from desired end-effector velocity
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            vx: Desired x velocity (m/s)
            vy: Desired y velocity (m/s)
            
        Returns:
            Joint velocities [q1_dot, q2_dot] in rad/s
            
        Raises:
            ValueError: If Jacobian is singular
        """
        J = self.compute_jacobian(q1, q2)
        end_effector_velocity = np.array([vx, vy])
        
        # Check for singularity
        det_J = np.linalg.det(J)
        if abs(det_J) < 1e-6:
            raise ValueError("Jacobian is singular - robot is at singularity")
        
        # Solve for joint velocities
        joint_velocities = np.linalg.solve(J, end_effector_velocity)
        
        return joint_velocities
    
    def check_singularity(self, q1: float, q2: float, tolerance: float = 1e-6) -> bool:
        """
        Check if robot is at a singular configuration
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            tolerance: Tolerance for singularity detection
            
        Returns:
            True if robot is at singularity
        """
        J = self.compute_jacobian(q1, q2)
        det_J = np.linalg.det(J)
        
        return abs(det_J) < tolerance
    
    def get_link_transforms(self, q1: float, q2: float) -> List[np.ndarray]:
        """
        Get transformation matrices for each link
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            List of 3x3 transformation matrices [T0_1, T1_2]
        """
        # Transformation from base to joint 1
        T0_1 = np.array([
            [np.cos(q1), -np.sin(q1), self.l1 * np.cos(q1)],
            [np.sin(q1),  np.cos(q1), self.l1 * np.sin(q1)],
            [0,           0,          1]
        ])
        
        # Transformation from joint 1 to end-effector
        T1_2 = np.array([
            [np.cos(q2), -np.sin(q2), self.l2 * np.cos(q2)],
            [np.sin(q2),  np.cos(q2), self.l2 * np.sin(q2)],
            [0,           0,          1]
        ])
        
        return [T0_1, T1_2]
    
    def workspace_analysis(self, q1_range: Tuple[float, float], q2_range: Tuple[float, float], 
                          resolution: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Analyze the robot workspace
        
        Args:
            q1_range: Range of joint 1 angles (min, max) in radians
            q2_range: Range of joint 2 angles (min, max) in radians
            resolution: Number of points per joint for workspace sampling
            
        Returns:
            Tuple of (x_points, y_points) arrays representing the workspace boundary
        """
        q1_vals = np.linspace(q1_range[0], q1_range[1], resolution)
        q2_vals = np.linspace(q2_range[0], q2_range[1], resolution)
        
        x_points = []
        y_points = []
        
        for q1 in q1_vals:
            for q2 in q2_vals:
                pos = self.forward_kinematics(q1, q2)
                x_points.append(pos[0])
                y_points.append(pos[1])
        
        return np.array(x_points), np.array(y_points)
