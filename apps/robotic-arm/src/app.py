import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import time

from kinematics import RobotKinematics
from dynamics import RobotDynamics
from control import PIDController
from trajectory import TrajectoryPlanner
from visualization import RobotVisualizer
from utils import calculate_workspace, export_simulation_data

# Page configuration
st.set_page_config(
    page_title="2DOF Robotic Arm Simulation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'robot_kinematics' not in st.session_state:
    st.session_state.robot_kinematics = None
if 'robot_dynamics' not in st.session_state:
    st.session_state.robot_dynamics = None
if 'simulation_data' not in st.session_state:
    st.session_state.simulation_data = []
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'current_time' not in st.session_state:
    st.session_state.current_time = 0.0

def main():
    st.title("🤖 2DOF Robotic Arm Simulation")
    st.markdown("*Comprehensive kinematics, dynamics, and control simulation*")
    
    # Sidebar for parameters
    with st.sidebar:
        st.header("Robot Parameters")
        
        # Physical parameters
        st.subheader("Physical Properties")
        l1 = st.slider("Link 1 Length (m)", 0.1, 2.0, 1.0, 0.01)
        l2 = st.slider("Link 2 Length (m)", 0.1, 2.0, 0.8, 0.01)
        m1 = st.slider("Link 1 Mass (kg)", 0.1, 10.0, 2.0, 0.1)
        m2 = st.slider("Link 2 Mass (kg)", 0.1, 10.0, 1.5, 0.1)
        I1 = st.slider("Link 1 Inertia (kg⋅m²)", 0.01, 1.0, 0.1, 0.01)
        I2 = st.slider("Link 2 Inertia (kg⋅m²)", 0.01, 1.0, 0.08, 0.01)
        
        # Joint limits
        st.subheader("Joint Limits")
        q1_min = st.slider("Joint 1 Min (rad)", -np.pi, 0.0, -np.pi/2, 0.1)
        q1_max = st.slider("Joint 1 Max (rad)", 0.0, np.pi, np.pi/2, 0.1)
        q2_min = st.slider("Joint 2 Min (rad)", -np.pi, 0.0, -np.pi/2, 0.1)
        q2_max = st.slider("Joint 2 Max (rad)", 0.0, np.pi, np.pi/2, 0.1)
        
        # Control parameters
        st.subheader("PID Controller")
        kp1 = st.slider("Joint 1 Kp", 0.0, 100.0, 50.0, 1.0)
        ki1 = st.slider("Joint 1 Ki", 0.0, 10.0, 2.0, 0.1)
        kd1 = st.slider("Joint 1 Kd", 0.0, 20.0, 5.0, 0.1)
        kp2 = st.slider("Joint 2 Kp", 0.0, 100.0, 40.0, 1.0)
        ki2 = st.slider("Joint 2 Ki", 0.0, 10.0, 1.5, 0.1)
        kd2 = st.slider("Joint 2 Kd", 0.0, 20.0, 4.0, 0.1)
        
        # Simulation parameters
        st.subheader("Simulation")
        dt = st.slider("Time Step (s)", 0.001, 0.1, 0.01, 0.001)
        gravity = st.slider("Gravity (m/s²)", 0.0, 15.0, 9.81, 0.1)
        
        if st.button("Reset Simulation"):
            st.session_state.simulation_data = []
            st.session_state.current_time = 0.0
            st.session_state.simulation_running = False
            st.rerun()
    
    # Initialize robot components
    robot_params = {
        'l1': l1, 'l2': l2, 'm1': m1, 'm2': m2, 'I1': I1, 'I2': I2,
        'q1_limits': (q1_min, q1_max), 'q2_limits': (q2_min, q2_max),
        'gravity': gravity
    }
    
    kinematics = RobotKinematics(l1, l2)
    dynamics = RobotDynamics(l1, l2, m1, m2, I1, I2, gravity)
    controller = PIDController(
        kp=[kp1, kp2], ki=[ki1, ki2], kd=[kd1, kd2], dt=dt
    )
    trajectory_planner = TrajectoryPlanner()
    visualizer = RobotVisualizer()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Real-time Simulation", "Kinematics Analysis", "Dynamics Analysis", 
        "Trajectory Planning", "Data Export"
    ])
    
    with tab1:
        real_time_simulation(kinematics, dynamics, controller, visualizer, dt, robot_params)
    
    with tab2:
        kinematics_analysis(kinematics, robot_params)
    
    with tab3:
        dynamics_analysis(dynamics, robot_params)
    
    with tab4:
        trajectory_planning(kinematics, dynamics, controller, trajectory_planner, visualizer, robot_params)
    
    with tab5:
        data_export()

def real_time_simulation(kinematics, dynamics, controller, visualizer, dt, robot_params):
    st.header("Real-time Simulation")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Control Panel")
        
        # Target position input
        target_x = st.number_input("Target X (m)", -2.0, 2.0, 1.0, 0.01)
        target_y = st.number_input("Target Y (m)", -2.0, 2.0, 0.5, 0.01)
        
        # Manual joint control
        st.subheader("Manual Joint Control")
        manual_q1 = st.slider("Joint 1 Angle (rad)", robot_params['q1_limits'][0], 
                             robot_params['q1_limits'][1], 0.0, 0.01)
        manual_q2 = st.slider("Joint 2 Angle (rad)", robot_params['q2_limits'][0], 
                             robot_params['q2_limits'][1], 0.0, 0.01)
        
        control_mode = st.radio("Control Mode", ["Position Control", "Manual Control"])
        
        # Simulation controls
        col_start, col_stop = st.columns(2)
        with col_start:
            if st.button("Start Simulation"):
                st.session_state.simulation_running = True
        with col_stop:
            if st.button("Stop Simulation"):
                st.session_state.simulation_running = False
    
    with col1:
        st.subheader("Robot Visualization")
        
        # Current state
        if control_mode == "Position Control":
            # Inverse kinematics for target position
            try:
                target_angles = kinematics.inverse_kinematics(target_x, target_y)
                q1_target, q2_target = target_angles[0]  # Use first solution
            except:
                st.error("Target position is unreachable!")
                q1_target, q2_target = 0.0, 0.0
        else:
            q1_target, q2_target = manual_q1, manual_q2
        
        # Current joint angles (simplified for real-time display)
        if len(st.session_state.simulation_data) > 0:
            current_state = st.session_state.simulation_data[-1]
            q1_current = current_state['q1']
            q2_current = current_state['q2']
        else:
            q1_current, q2_current = 0.0, 0.0
        
        # Calculate forward kinematics
        end_effector_pos = kinematics.forward_kinematics(q1_current, q2_current)
        
        # Create visualization
        fig = visualizer.create_robot_plot(kinematics, q1_current, q2_current, 
                                         target_x, target_y)
        st.plotly_chart(fig, use_container_width=True)
        
        # Display current status
        col_status1, col_status2, col_status3 = st.columns(3)
        with col_status1:
            st.metric("End-Effector X", f"{end_effector_pos[0]:.3f} m")
            st.metric("End-Effector Y", f"{end_effector_pos[1]:.3f} m")
        with col_status2:
            st.metric("Joint 1 Angle", f"{np.degrees(q1_current):.1f}°")
            st.metric("Joint 2 Angle", f"{np.degrees(q2_current):.1f}°")
        with col_status3:
            if len(st.session_state.simulation_data) > 0:
                current_state = st.session_state.simulation_data[-1]
                st.metric("Joint 1 Torque", f"{current_state.get('tau1', 0):.2f} Nm")
                st.metric("Joint 2 Torque", f"{current_state.get('tau2', 0):.2f} Nm")
    
    # Simulation update (simplified for demonstration)
    if st.session_state.simulation_running:
        # Simulate one step
        if control_mode == "Position Control":
            # PID control simulation
            error1 = q1_target - q1_current
            error2 = q2_target - q2_current
            tau1, tau2 = controller.compute_control([error1, error2])
        else:
            tau1, tau2 = 0.0, 0.0
        
        # Store simulation data
        simulation_step = {
            'time': st.session_state.current_time,
            'q1': q1_current + 0.01 * (q1_target - q1_current),  # Simplified integration
            'q2': q2_current + 0.01 * (q2_target - q2_current),
            'q1_dot': 0.0,
            'q2_dot': 0.0,
            'tau1': tau1,
            'tau2': tau2,
            'target_x': target_x,
            'target_y': target_y,
            'end_x': end_effector_pos[0],
            'end_y': end_effector_pos[1]
        }
        
        st.session_state.simulation_data.append(simulation_step)
        st.session_state.current_time += dt
        
        # Limit data storage
        if len(st.session_state.simulation_data) > 1000:
            st.session_state.simulation_data = st.session_state.simulation_data[-1000:]
        
        time.sleep(0.1)  # Control simulation speed
        st.rerun()

def kinematics_analysis(kinematics, robot_params):
    st.header("Kinematics Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Forward Kinematics")
        
        # Input joint angles
        q1_fk = st.slider("Joint 1 (rad)", robot_params['q1_limits'][0], 
                         robot_params['q1_limits'][1], 0.0, 0.01, key="fk_q1")
        q2_fk = st.slider("Joint 2 (rad)", robot_params['q2_limits'][0], 
                         robot_params['q2_limits'][1], 0.0, 0.01, key="fk_q2")
        
        # Calculate forward kinematics
        end_pos = kinematics.forward_kinematics(q1_fk, q2_fk)
        joint_positions = kinematics.get_joint_positions(q1_fk, q2_fk)
        
        st.write("**Results:**")
        st.write(f"End-effector position: ({end_pos[0]:.3f}, {end_pos[1]:.3f}) m")
        st.write(f"Joint 1 position: ({joint_positions[0][0]:.3f}, {joint_positions[0][1]:.3f}) m")
        st.write(f"Joint 2 position: ({joint_positions[1][0]:.3f}, {joint_positions[1][1]:.3f}) m")
        
        # Jacobian matrix
        jacobian = kinematics.compute_jacobian(q1_fk, q2_fk)
        st.write("**Jacobian Matrix:**")
        st.write(jacobian)
        
        # Manipulability
        manipulability = kinematics.compute_manipulability(q1_fk, q2_fk)
        st.metric("Manipulability Index", f"{manipulability:.4f}")
    
    with col2:
        st.subheader("Inverse Kinematics")
        
        # Target position input
        target_x_ik = st.number_input("Target X (m)", -3.0, 3.0, 1.0, 0.01, key="ik_x")
        target_y_ik = st.number_input("Target Y (m)", -3.0, 3.0, 0.5, 0.01, key="ik_y")
        
        try:
            solutions = kinematics.inverse_kinematics(target_x_ik, target_y_ik)
            
            st.write("**Solutions:**")
            for i, (q1_sol, q2_sol) in enumerate(solutions):
                st.write(f"Solution {i+1}: q1={np.degrees(q1_sol):.1f}°, q2={np.degrees(q2_sol):.1f}°")
                
                # Check if solution is within joint limits
                q1_valid = robot_params['q1_limits'][0] <= q1_sol <= robot_params['q1_limits'][1]
                q2_valid = robot_params['q2_limits'][0] <= q2_sol <= robot_params['q2_limits'][1]
                
                if q1_valid and q2_valid:
                    st.success("✅ Valid solution")
                else:
                    st.warning("⚠️ Outside joint limits")
                    
        except Exception as e:
            st.error(f"No solution found: {str(e)}")
    
    # Workspace visualization
    st.subheader("Workspace Analysis")
    workspace_data = calculate_workspace(kinematics, robot_params)
    
    fig_workspace = go.Figure()
    fig_workspace.add_trace(go.Scatter(
        x=workspace_data['x'], y=workspace_data['y'],
        mode='markers', marker=dict(size=2, color='blue', opacity=0.6),
        name='Reachable Workspace'
    ))
    
    fig_workspace.update_layout(
        title="Robot Workspace",
        xaxis_title="X (m)", yaxis_title="Y (m)",
        width=600, height=400
    )
    
    st.plotly_chart(fig_workspace, use_container_width=True)

def dynamics_analysis(dynamics, robot_params):
    st.header("Dynamics Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Dynamic Equations")
        
        # Current state input
        q1_dyn = st.slider("Joint 1 Position (rad)", robot_params['q1_limits'][0], 
                          robot_params['q1_limits'][1], 0.0, 0.01, key="dyn_q1")
        q2_dyn = st.slider("Joint 2 Position (rad)", robot_params['q2_limits'][0], 
                          robot_params['q2_limits'][1], 0.0, 0.01, key="dyn_q2")
        q1_dot = st.slider("Joint 1 Velocity (rad/s)", -5.0, 5.0, 0.0, 0.1, key="dyn_q1_dot")
        q2_dot = st.slider("Joint 2 Velocity (rad/s)", -5.0, 5.0, 0.0, 0.1, key="dyn_q2_dot")
        
        # Applied torques
        tau1_applied = st.slider("Applied Torque 1 (Nm)", -50.0, 50.0, 0.0, 1.0, key="tau1")
        tau2_applied = st.slider("Applied Torque 2 (Nm)", -50.0, 50.0, 0.0, 1.0, key="tau2")
        
        # Calculate dynamic quantities
        state = np.array([q1_dyn, q2_dyn, q1_dot, q2_dot])
        torques = np.array([tau1_applied, tau2_applied])
        
        # Mass matrix
        M = dynamics.mass_matrix(q1_dyn, q2_dyn)
        st.write("**Mass Matrix:**")
        st.write(M)
        
        # Coriolis matrix
        C = dynamics.coriolis_matrix(q1_dyn, q2_dyn, q1_dot, q2_dot)
        st.write("**Coriolis Matrix:**")
        st.write(C)
        
        # Gravity vector
        G = dynamics.gravity_vector(q1_dyn, q2_dyn)
        st.write("**Gravity Vector:**")
        st.write(G)
    
    with col2:
        st.subheader("Forward Dynamics")
        
        # Calculate accelerations
        accelerations = dynamics.forward_dynamics(state, torques)
        
        st.write("**Joint Accelerations:**")
        st.metric("Joint 1 Acceleration", f"{accelerations[0]:.3f} rad/s²")
        st.metric("Joint 2 Acceleration", f"{accelerations[1]:.3f} rad/s²")
        
        # Energy analysis
        kinetic_energy = dynamics.compute_kinetic_energy(state)
        potential_energy = dynamics.compute_potential_energy(q1_dyn, q2_dyn)
        total_energy = kinetic_energy + potential_energy
        
        st.write("**Energy Analysis:**")
        st.metric("Kinetic Energy", f"{kinetic_energy:.3f} J")
        st.metric("Potential Energy", f"{potential_energy:.3f} J")
        st.metric("Total Energy", f"{total_energy:.3f} J")
        
        # Power analysis
        power = np.dot([tau1_applied, tau2_applied], [q1_dot, q2_dot])
        st.metric("Instantaneous Power", f"{power:.3f} W")

def trajectory_planning(kinematics, dynamics, controller, trajectory_planner, visualizer, robot_params):
    st.header("Trajectory Planning")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Trajectory Parameters")
        
        # Trajectory type
        traj_type = st.selectbox("Trajectory Type", 
                                ["Point-to-Point", "Circular", "Figure-8", "Custom Path"])
        
        if traj_type == "Point-to-Point":
            start_x = st.number_input("Start X (m)", -2.0, 2.0, 0.5, 0.01, key="traj_start_x")
            start_y = st.number_input("Start Y (m)", -2.0, 2.0, 0.5, 0.01, key="traj_start_y")
            end_x = st.number_input("End X (m)", -2.0, 2.0, 1.5, 0.01, key="traj_end_x")
            end_y = st.number_input("End Y (m)", -2.0, 2.0, 1.0, 0.01, key="traj_end_y")
            duration = st.slider("Duration (s)", 1.0, 10.0, 3.0, 0.1)
            
            trajectory = trajectory_planner.point_to_point(
                [start_x, start_y], [end_x, end_y], duration
            )
            
        elif traj_type == "Circular":
            center_x = st.number_input("Center X (m)", -2.0, 2.0, 1.0, 0.01, key="circ_center_x")
            center_y = st.number_input("Center Y (m)", -2.0, 2.0, 0.5, 0.01, key="circ_center_y")
            radius = st.slider("Radius (m)", 0.1, 1.0, 0.3, 0.01)
            duration = st.slider("Duration (s)", 2.0, 15.0, 5.0, 0.1, key="circ_duration")
            
            trajectory = trajectory_planner.circular_trajectory(
                [center_x, center_y], radius, duration
            )
            
        elif traj_type == "Figure-8":
            center_x = st.number_input("Center X (m)", -2.0, 2.0, 1.0, 0.01, key="fig8_center_x")
            center_y = st.number_input("Center Y (m)", -2.0, 2.0, 0.5, 0.01, key="fig8_center_y")
            scale = st.slider("Scale", 0.1, 1.0, 0.3, 0.01)
            duration = st.slider("Duration (s)", 3.0, 20.0, 8.0, 0.1, key="fig8_duration")
            
            trajectory = trajectory_planner.figure_eight_trajectory(
                [center_x, center_y], scale, duration
            )
        
        # Simulation controls
        dt_traj = st.slider("Time Step (s)", 0.01, 0.1, 0.02, 0.01, key="traj_dt")
        
        if st.button("Execute Trajectory"):
            execute_trajectory_simulation(trajectory, kinematics, dynamics, controller, dt_traj)
    
    with col2:
        st.subheader("Trajectory Visualization")
        
        if 'trajectory' in locals():
            # Plot trajectory path
            fig_traj = go.Figure()
            
            # Add trajectory path
            traj_points = np.array([trajectory(t) for t in np.linspace(0, trajectory.duration, 100)])
            fig_traj.add_trace(go.Scatter(
                x=traj_points[:, 0], y=traj_points[:, 1],
                mode='lines+markers', name='Planned Trajectory',
                line=dict(color='blue', width=3)
            ))
            
            # Add start and end points
            start_point = trajectory(0)
            end_point = trajectory(trajectory.duration)
            fig_traj.add_trace(go.Scatter(
                x=[start_point[0]], y=[start_point[1]],
                mode='markers', name='Start', marker=dict(color='green', size=10)
            ))
            fig_traj.add_trace(go.Scatter(
                x=[end_point[0]], y=[end_point[1]],
                mode='markers', name='End', marker=dict(color='red', size=10)
            ))
            
            fig_traj.update_layout(
                title="Planned Trajectory",
                xaxis_title="X (m)", yaxis_title="Y (m)",
                width=600, height=400
            )
            
            st.plotly_chart(fig_traj, use_container_width=True)
            
            # Trajectory analysis
            st.subheader("Trajectory Analysis")
            
            # Sample trajectory points for analysis
            t_samples = np.linspace(0, trajectory.duration, 50)
            positions = np.array([trajectory(t) for t in t_samples])
            velocities = np.array([trajectory.velocity(t) for t in t_samples])
            accelerations = np.array([trajectory.acceleration(t) for t in t_samples])
            
            # Plot velocity and acceleration profiles
            fig_profiles = go.Figure()
            
            fig_profiles.add_trace(go.Scatter(
                x=t_samples, y=np.linalg.norm(velocities, axis=1),
                name='Velocity Magnitude', line=dict(color='orange')
            ))
            
            fig_profiles.add_trace(go.Scatter(
                x=t_samples, y=np.linalg.norm(accelerations, axis=1),
                name='Acceleration Magnitude', line=dict(color='red')
            ))
            
            fig_profiles.update_layout(
                title="Velocity and Acceleration Profiles",
                xaxis_title="Time (s)", yaxis_title="Magnitude",
                width=600, height=300
            )
            
            st.plotly_chart(fig_profiles, use_container_width=True)

def execute_trajectory_simulation(trajectory, kinematics, dynamics, controller, dt):
    """Execute trajectory tracking simulation"""
    st.info("Executing trajectory simulation...")
    
    # Initialize simulation
    simulation_results = []
    t = 0.0
    state = np.array([0.0, 0.0, 0.0, 0.0])  # [q1, q2, q1_dot, q2_dot]
    
    progress_bar = st.progress(0)
    
    while t <= trajectory.duration:
        # Get desired position
        desired_pos = trajectory(t)
        
        try:
            # Inverse kinematics for desired joint angles
            solutions = kinematics.inverse_kinematics(desired_pos[0], desired_pos[1])
            desired_angles = solutions[0]  # Use first solution
            
            # PID control
            error = np.array(desired_angles) - state[:2]
            torques = controller.compute_control(error)
            
            # Forward dynamics
            accelerations = dynamics.forward_dynamics(state, torques)
            
            # Integrate (simple Euler integration)
            state[2:] += accelerations * dt  # Update velocities
            state[:2] += state[2:] * dt      # Update positions
            
            # Store results
            end_effector_pos = kinematics.forward_kinematics(state[0], state[1])
            
            simulation_results.append({
                'time': t,
                'q1': state[0], 'q2': state[1],
                'q1_dot': state[2], 'q2_dot': state[3],
                'tau1': torques[0], 'tau2': torques[1],
                'desired_x': desired_pos[0], 'desired_y': desired_pos[1],
                'actual_x': end_effector_pos[0], 'actual_y': end_effector_pos[1],
                'error_x': desired_pos[0] - end_effector_pos[0],
                'error_y': desired_pos[1] - end_effector_pos[1]
            })
            
        except:
            st.warning(f"Inverse kinematics failed at t={t:.2f}s")
        
        t += dt
        progress_bar.progress(min(t / trajectory.duration, 1.0))
    
    # Store results in session state
    st.session_state.simulation_data.extend(simulation_results)
    
    # Display results
    st.success("Trajectory simulation completed!")
    
    # Plot tracking results
    df_results = pd.DataFrame(simulation_results)
    
    fig_tracking = go.Figure()
    fig_tracking.add_trace(go.Scatter(
        x=df_results['desired_x'], y=df_results['desired_y'],
        mode='lines', name='Desired Path', line=dict(color='blue', width=3)
    ))
    fig_tracking.add_trace(go.Scatter(
        x=df_results['actual_x'], y=df_results['actual_y'],
        mode='lines', name='Actual Path', line=dict(color='red', width=2, dash='dash')
    ))
    
    fig_tracking.update_layout(
        title="Trajectory Tracking Results",
        xaxis_title="X (m)", yaxis_title="Y (m)"
    )
    
    st.plotly_chart(fig_tracking, use_container_width=True)
    
    # Error analysis
    fig_error = go.Figure()
    fig_error.add_trace(go.Scatter(
        x=df_results['time'], y=np.sqrt(df_results['error_x']**2 + df_results['error_y']**2),
        mode='lines', name='Position Error', line=dict(color='red')
    ))
    
    fig_error.update_layout(
        title="Position Tracking Error",
        xaxis_title="Time (s)", yaxis_title="Error (m)"
    )
    
    st.plotly_chart(fig_error, use_container_width=True)

def data_export():
    st.header("Data Export")
    
    if len(st.session_state.simulation_data) == 0:
        st.info("No simulation data available. Run a simulation first.")
        return
    
    # Convert simulation data to DataFrame
    df = pd.DataFrame(st.session_state.simulation_data)
    
    st.subheader("Simulation Data Summary")
    st.write(f"Total data points: {len(df)}")
    st.write(f"Time range: {df['time'].min():.2f}s to {df['time'].max():.2f}s")
    
    # Display data preview
    st.subheader("Data Preview")
    st.dataframe(df.head(10))
    
    # Statistics
    st.subheader("Statistics")
    st.write(df.describe())
    
    # Export options
    st.subheader("Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV file",
                data=csv,
                file_name=f"robot_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download JSON"):
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="Download JSON file",
                data=json_data,
                file_name=f"robot_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Plot data
    st.subheader("Data Visualization")
    
    plot_option = st.selectbox("Select plot type", [
        "Joint Angles", "Joint Velocities", "Torques", 
        "End-Effector Position", "Tracking Error"
    ])
    
    fig_data = go.Figure()
    
    if plot_option == "Joint Angles":
        fig_data.add_trace(go.Scatter(x=df['time'], y=np.degrees(df['q1']), name='Joint 1'))
        fig_data.add_trace(go.Scatter(x=df['time'], y=np.degrees(df['q2']), name='Joint 2'))
        fig_data.update_layout(title="Joint Angles", yaxis_title="Angle (degrees)")
        
    elif plot_option == "Joint Velocities":
        if 'q1_dot' in df.columns:
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['q1_dot'], name='Joint 1 Velocity'))
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['q2_dot'], name='Joint 2 Velocity'))
        fig_data.update_layout(title="Joint Velocities", yaxis_title="Velocity (rad/s)")
        
    elif plot_option == "Torques":
        if 'tau1' in df.columns:
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['tau1'], name='Joint 1 Torque'))
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['tau2'], name='Joint 2 Torque'))
        fig_data.update_layout(title="Joint Torques", yaxis_title="Torque (Nm)")
        
    elif plot_option == "End-Effector Position":
        if 'end_x' in df.columns:
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['end_x'], name='X Position'))
            fig_data.add_trace(go.Scatter(x=df['time'], y=df['end_y'], name='Y Position'))
        fig_data.update_layout(title="End-Effector Position", yaxis_title="Position (m)")
        
    elif plot_option == "Tracking Error":
        if 'error_x' in df.columns:
            error_magnitude = np.sqrt(df['error_x']**2 + df['error_y']**2)
            fig_data.add_trace(go.Scatter(x=df['time'], y=error_magnitude, name='Position Error'))
        fig_data.update_layout(title="Tracking Error", yaxis_title="Error (m)")
    
    fig_data.update_layout(xaxis_title="Time (s)")
    st.plotly_chart(fig_data, use_container_width=True)

if __name__ == "__main__":
    main()
