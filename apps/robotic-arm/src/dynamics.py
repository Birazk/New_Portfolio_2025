import numpy as np
import sympy as sp
from typing import Tuple, Optional
from scipy.integrate import solve_ivp

class RobotDynamics:
    """
    2DOF Robotic Arm Dynamics
    
    This class implements the dynamic model of a 2-degree-of-freedom planar robotic arm
    using Lagrangian mechanics. It includes mass matrix, Coriolis/centrifugal forces,
    gravity effects, and forward/inverse dynamics.
    """
    
    def __init__(self, l1: float, l2: float, m1: float, m2: float, 
                 I1: float, I2: float, gravity: float = 9.81):
        """
        Initialize the dynamics model
        
        Args:
            l1: Length of first link (m)
            l2: Length of second link (m)
            m1: Mass of first link (kg)
            m2: Mass of second link (kg)
            I1: Moment of inertia of first link about its center (kg⋅m²)
            I2: Moment of inertia of second link about its center (kg⋅m²)
            gravity: Gravitational acceleration (m/s²)
        """
        self.l1 = l1
        self.l2 = l2
        self.m1 = m1
        self.m2 = m2
        self.I1 = I1
        self.I2 = I2
        self.g = gravity
        
        # Center of mass positions (assuming uniform density)
        self.lc1 = l1 / 2  # Center of mass of link 1
        self.lc2 = l2 / 2  # Center of mass of link 2
        
        # Setup symbolic model for analytical dynamics
        self._setup_symbolic_dynamics()
    
    def _setup_symbolic_dynamics(self):
        """Setup symbolic dynamic equations using Lagrangian mechanics"""
        # Define symbolic variables
        q1, q2 = sp.symbols('q1 q2')
        q1_dot, q2_dot = sp.symbols('q1_dot q2_dot')
        q1_ddot, q2_ddot = sp.symbols('q1_ddot q2_ddot')
        
        # Physical parameters as symbols
        l1, l2, lc1, lc2 = sp.symbols('l1 l2 lc1 lc2', positive=True)
        m1, m2, I1, I2, g = sp.symbols('m1 m2 I1 I2 g', positive=True)
        
        # Position of center of mass of link 1
        x1_cm = lc1 * sp.cos(q1)
        y1_cm = lc1 * sp.sin(q1)
        
        # Position of center of mass of link 2
        x2_cm = l1 * sp.cos(q1) + lc2 * sp.cos(q1 + q2)
        y2_cm = l1 * sp.sin(q1) + lc2 * sp.sin(q1 + q2)
        
        # Velocities of centers of mass
        x1_cm_dot = sp.diff(x1_cm, q1) * q1_dot
        y1_cm_dot = sp.diff(y1_cm, q1) * q1_dot
        
        x2_cm_dot = sp.diff(x2_cm, q1) * q1_dot + sp.diff(x2_cm, q2) * q2_dot
        y2_cm_dot = sp.diff(y2_cm, q1) * q1_dot + sp.diff(y2_cm, q2) * q2_dot
        
        # Kinetic energy
        T1_trans = sp.Rational(1, 2) * m1 * (x1_cm_dot**2 + y1_cm_dot**2)
        T1_rot = sp.Rational(1, 2) * I1 * q1_dot**2
        T1 = T1_trans + T1_rot
        
        T2_trans = sp.Rational(1, 2) * m2 * (x2_cm_dot**2 + y2_cm_dot**2)
        T2_rot = sp.Rational(1, 2) * I2 * (q1_dot + q2_dot)**2
        T2 = T2_trans + T2_rot
        
        T_total = T1 + T2
        
        # Potential energy
        V1 = m1 * g * y1_cm
        V2 = m2 * g * y2_cm
        V_total = V1 + V2
        
        # Lagrangian
        L = T_total - V_total
        
        # Euler-Lagrange equations
        # d/dt(∂L/∂q̇ᵢ) - ∂L/∂qᵢ = τᵢ
        
        # For joint 1
        dL_dq1dot = sp.diff(L, q1_dot)
        dt_dL_dq1dot = sp.diff(dL_dq1dot, q1) * q1_dot + sp.diff(dL_dq1dot, q2) * q2_dot + \
                       sp.diff(dL_dq1dot, q1_dot) * q1_ddot + sp.diff(dL_dq1dot, q2_dot) * q2_ddot
        dL_dq1 = sp.diff(L, q1)
        
        eq1 = dt_dL_dq1dot - dL_dq1
        
        # For joint 2
        dL_dq2dot = sp.diff(L, q2_dot)
        dt_dL_dq2dot = sp.diff(dL_dq2dot, q1) * q1_dot + sp.diff(dL_dq2dot, q2) * q2_dot + \
                       sp.diff(dL_dq2dot, q1_dot) * q1_ddot + sp.diff(dL_dq2dot, q2_dot) * q2_ddot
        dL_dq2 = sp.diff(L, q2)
        
        eq2 = dt_dL_dq2dot - dL_dq2
        
        # Extract mass matrix, Coriolis matrix, and gravity vector
        # M(q)q̈ + C(q,q̇)q̇ + G(q) = τ
        
        # Mass matrix M(q)
        M11 = eq1.coeff(q1_ddot)
        M12 = eq1.coeff(q2_ddot)
        M21 = eq2.coeff(q1_ddot)
        M22 = eq2.coeff(q2_ddot)
        
        self.M_symbolic = sp.Matrix([[M11, M12], [M21, M22]])
        
        # Store symbolic expressions
        self.T_symbolic = T_total
        self.V_symbolic = V_total
        self.L_symbolic = L
        
        # Create numerical functions
        self._create_numerical_functions()
    
    def _create_numerical_functions(self):
        """Create fast numerical functions from symbolic expressions"""
        # Define substitution dictionary for numerical values
        self.param_subs = {
            'l1': self.l1, 'l2': self.l2, 'lc1': self.lc1, 'lc2': self.lc2,
            'm1': self.m1, 'm2': self.m2, 'I1': self.I1, 'I2': self.I2, 'g': self.g
        }
    
    def mass_matrix(self, q1: float, q2: float) -> np.ndarray:
        """
        Compute the mass matrix M(q)
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            2x2 mass matrix
        """
        # Analytical expressions for mass matrix elements
        cos_q2 = np.cos(q2)
        
        # M11 element
        M11 = (self.m1 * self.lc1**2 + self.m2 * (self.l1**2 + self.lc2**2 + 2*self.l1*self.lc2*cos_q2) + 
               self.I1 + self.I2)
        
        # M12 = M21 element (symmetric matrix)
        M12 = self.m2 * (self.lc2**2 + self.l1 * self.lc2 * cos_q2) + self.I2
        
        # M22 element
        M22 = self.m2 * self.lc2**2 + self.I2
        
        return np.array([[M11, M12], [M12, M22]])
    
    def coriolis_matrix(self, q1: float, q2: float, q1_dot: float, q2_dot: float) -> np.ndarray:
        """
        Compute the Coriolis/centrifugal matrix C(q,q̇)
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            q1_dot: Joint 1 velocity (rad/s)
            q2_dot: Joint 2 velocity (rad/s)
            
        Returns:
            2x2 Coriolis matrix
        """
        sin_q2 = np.sin(q2)
        
        # Coriolis coefficients
        h = -self.m2 * self.l1 * self.lc2 * sin_q2
        
        # C matrix elements
        C11 = h * q2_dot
        C12 = h * (q1_dot + q2_dot)
        C21 = -h * q1_dot
        C22 = 0
        
        return np.array([[C11, C12], [C21, C22]])
    
    def gravity_vector(self, q1: float, q2: float) -> np.ndarray:
        """
        Compute the gravity vector G(q)
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            2x1 gravity vector
        """
        cos_q1 = np.cos(q1)
        cos_q12 = np.cos(q1 + q2)
        
        G1 = (self.m1 * self.lc1 + self.m2 * self.l1) * self.g * cos_q1 + \
             self.m2 * self.lc2 * self.g * cos_q12
        
        G2 = self.m2 * self.lc2 * self.g * cos_q12
        
        return np.array([G1, G2])
    
    def forward_dynamics(self, state: np.ndarray, torques: np.ndarray) -> np.ndarray:
        """
        Compute forward dynamics: q̈ = M⁻¹(τ - C*q̇ - G)
        
        Args:
            state: State vector [q1, q2, q1_dot, q2_dot]
            torques: Applied torques [tau1, tau2]
            
        Returns:
            Joint accelerations [q1_ddot, q2_ddot]
        """
        q1, q2, q1_dot, q2_dot = state
        tau1, tau2 = torques
        
        # Compute dynamics matrices
        M = self.mass_matrix(q1, q2)
        C = self.coriolis_matrix(q1, q2, q1_dot, q2_dot)
        G = self.gravity_vector(q1, q2)
        
        # Joint velocities
        q_dot = np.array([q1_dot, q2_dot])
        
        # Applied torques vector
        tau = np.array([tau1, tau2])
        
        # Compute accelerations
        q_ddot = np.linalg.solve(M, tau - C @ q_dot - G)
        
        return q_ddot
    
    def inverse_dynamics(self, q1: float, q2: float, q1_dot: float, q2_dot: float,
                        q1_ddot: float, q2_ddot: float) -> np.ndarray:
        """
        Compute inverse dynamics: τ = M*q̈ + C*q̇ + G
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            q1_dot: Joint 1 velocity (rad/s)
            q2_dot: Joint 2 velocity (rad/s)
            q1_ddot: Joint 1 acceleration (rad/s²)
            q2_ddot: Joint 2 acceleration (rad/s²)
            
        Returns:
            Required torques [tau1, tau2]
        """
        # Compute dynamics matrices
        M = self.mass_matrix(q1, q2)
        C = self.coriolis_matrix(q1, q2, q1_dot, q2_dot)
        G = self.gravity_vector(q1, q2)
        
        # State vectors
        q_dot = np.array([q1_dot, q2_dot])
        q_ddot = np.array([q1_ddot, q2_ddot])
        
        # Compute required torques
        tau = M @ q_ddot + C @ q_dot + G
        
        return tau
    
    def compute_kinetic_energy(self, state: np.ndarray) -> float:
        """
        Compute total kinetic energy
        
        Args:
            state: State vector [q1, q2, q1_dot, q2_dot]
            
        Returns:
            Kinetic energy (J)
        """
        q1, q2, q1_dot, q2_dot = state
        
        # Velocities of centers of mass
        # Link 1 center of mass velocity
        v1_x = -self.lc1 * np.sin(q1) * q1_dot
        v1_y = self.lc1 * np.cos(q1) * q1_dot
        v1_sq = v1_x**2 + v1_y**2
        
        # Link 2 center of mass velocity
        v2_x = -self.l1 * np.sin(q1) * q1_dot - self.lc2 * np.sin(q1 + q2) * (q1_dot + q2_dot)
        v2_y = self.l1 * np.cos(q1) * q1_dot + self.lc2 * np.cos(q1 + q2) * (q1_dot + q2_dot)
        v2_sq = v2_x**2 + v2_y**2
        
        # Translational kinetic energy
        T_trans = 0.5 * self.m1 * v1_sq + 0.5 * self.m2 * v2_sq
        
        # Rotational kinetic energy
        T_rot = 0.5 * self.I1 * q1_dot**2 + 0.5 * self.I2 * (q1_dot + q2_dot)**2
        
        return T_trans + T_rot
    
    def compute_potential_energy(self, q1: float, q2: float) -> float:
        """
        Compute total potential energy
        
        Args:
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            
        Returns:
            Potential energy (J)
        """
        # Heights of centers of mass
        h1 = self.lc1 * np.sin(q1)
        h2 = self.l1 * np.sin(q1) + self.lc2 * np.sin(q1 + q2)
        
        # Gravitational potential energy
        V = self.m1 * self.g * h1 + self.m2 * self.g * h2
        
        return V
    
    def compute_total_energy(self, state: np.ndarray) -> float:
        """
        Compute total mechanical energy
        
        Args:
            state: State vector [q1, q2, q1_dot, q2_dot]
            
        Returns:
            Total energy (J)
        """
        q1, q2 = state[:2]
        
        T = self.compute_kinetic_energy(state)
        V = self.compute_potential_energy(q1, q2)
        
        return T + V
    
    def simulate_dynamics(self, initial_state: np.ndarray, torque_func, 
                         time_span: Tuple[float, float], dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate robot dynamics over time
        
        Args:
            initial_state: Initial state [q1, q2, q1_dot, q2_dot]
            torque_func: Function that returns torques given (t, state)
            time_span: Simulation time span (t_start, t_end)
            dt: Time step for output
            
        Returns:
            Tuple of (time_array, state_history)
        """
        def dynamics_ode(t, state):
            """ODE function for scipy integration"""
            q1, q2, q1_dot, q2_dot = state
            torques = torque_func(t, state)
            accelerations = self.forward_dynamics(state, torques)
            
            # Return state derivative [q1_dot, q2_dot, q1_ddot, q2_ddot]
            return np.array([q1_dot, q2_dot, accelerations[0], accelerations[1]])
        
        # Create time points
        t_eval = np.arange(time_span[0], time_span[1] + dt, dt)
        
        # Solve ODE
        solution = solve_ivp(
            dynamics_ode, time_span, initial_state, 
            t_eval=t_eval, method='RK45', rtol=1e-8, atol=1e-10
        )
        
        if not solution.success:
            raise RuntimeError(f"ODE integration failed: {solution.message}")
        
        return solution.t, solution.y.T
    
    def linearize_dynamics(self, q1_eq: float, q2_eq: float) -> Tuple[np.ndarray, np.ndarray]:
        """
        Linearize dynamics around equilibrium point for linear control design
        
        Args:
            q1_eq: Equilibrium joint 1 angle (rad)
            q2_eq: Equilibrium joint 2 angle (rad)
            
        Returns:
            Tuple of (A, B) matrices for linearized system ẋ = Ax + Bu
        """
        # Small perturbation for numerical differentiation
        epsilon = 1e-6
        
        # Equilibrium state (assuming zero velocities at equilibrium)
        x_eq = np.array([q1_eq, q2_eq, 0.0, 0.0])
        
        # Compute A matrix (∂f/∂x at equilibrium)
        A = np.zeros((4, 4))
        
        for i in range(4):
            x_pert_pos = x_eq.copy()
            x_pert_neg = x_eq.copy()
            x_pert_pos[i] += epsilon
            x_pert_neg[i] -= epsilon
            
            # Zero torques at equilibrium
            f_pos = self._state_derivative(x_pert_pos, np.zeros(2))
            f_neg = self._state_derivative(x_pert_neg, np.zeros(2))
            
            A[:, i] = (f_pos - f_neg) / (2 * epsilon)
        
        # Compute B matrix (∂f/∂u at equilibrium)
        B = np.zeros((4, 2))
        
        for i in range(2):
            u_pert_pos = np.zeros(2)
            u_pert_neg = np.zeros(2)
            u_pert_pos[i] = epsilon
            u_pert_neg[i] = -epsilon
            
            f_pos = self._state_derivative(x_eq, u_pert_pos)
            f_neg = self._state_derivative(x_eq, u_pert_neg)
            
            B[:, i] = (f_pos - f_neg) / (2 * epsilon)
        
        return A, B
    
    def _state_derivative(self, state: np.ndarray, torques: np.ndarray) -> np.ndarray:
        """
        Compute state derivative for linearization
        
        Args:
            state: State vector [q1, q2, q1_dot, q2_dot]
            torques: Applied torques [tau1, tau2]
            
        Returns:
            State derivative [q1_dot, q2_dot, q1_ddot, q2_ddot]
        """
        q1, q2, q1_dot, q2_dot = state
        accelerations = self.forward_dynamics(state, torques)
        
        return np.array([q1_dot, q2_dot, accelerations[0], accelerations[1]])
