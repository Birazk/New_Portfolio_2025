import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Tuple, Optional
import pandas as pd

class RobotVisualizer:
    """
    Visualization utilities for 2DOF robotic arm simulation
    
    This class provides methods for creating interactive visualizations
    of the robot arm, workspace, trajectories, and simulation results.
    """
    
    def __init__(self):
        """Initialize the visualizer with default settings"""
        self.colors = {
            'link1': '#FF6B35',
            'link2': '#004E89', 
            'joint': '#FF9500',
            'end_effector': '#C5351B',
            'target': '#00A8CC',
            'trajectory': '#7209B7',
            'workspace': '#A663CC',
            'base': '#2E8B57'
        }
        
        self.default_layout = {
            'showlegend': True,
            'legend': dict(x=0.02, y=0.98),
            'margin': dict(l=50, r=50, t=50, b=50),
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white'
        }
    
    def create_robot_plot(self, kinematics, q1: float, q2: float, 
                         target_x: Optional[float] = None, target_y: Optional[float] = None,
                         show_workspace: bool = False, workspace_data: Optional[dict] = None,
                         trajectory_points: Optional[List[Tuple[float, float]]] = None) -> go.Figure:
        """
        Create interactive plot of the robotic arm
        
        Args:
            kinematics: RobotKinematics instance
            q1: Joint 1 angle (rad)
            q2: Joint 2 angle (rad)
            target_x: Target x position (optional)
            target_y: Target y position (optional)
            show_workspace: Whether to show workspace boundary
            workspace_data: Workspace points data (optional)
            trajectory_points: List of trajectory points to display (optional)
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Get joint positions
        joint_positions = kinematics.get_joint_positions(q1, q2)
        base_pos = joint_positions[0]
        joint1_pos = joint_positions[1]
        end_effector_pos = joint_positions[2]
        
        # Add workspace if requested
        if show_workspace and workspace_data is not None:
            fig.add_trace(go.Scatter(
                x=workspace_data['x'],
                y=workspace_data['y'],
                mode='markers',
                marker=dict(
                    size=2,
                    color=self.colors['workspace'],
                    opacity=0.3
                ),
                name='Workspace',
                hoverinfo='skip'
            ))
        
        # Add trajectory if provided
        if trajectory_points is not None:
            traj_x = [point[0] for point in trajectory_points]
            traj_y = [point[1] for point in trajectory_points]
            fig.add_trace(go.Scatter(
                x=traj_x,
                y=traj_y,
                mode='lines',
                line=dict(
                    color=self.colors['trajectory'],
                    width=2,
                    dash='dash'
                ),
                name='Trajectory',
                opacity=0.7
            ))
        
        # Add robot links
        # Link 1 (base to joint 1)
        fig.add_trace(go.Scatter(
            x=[base_pos[0], joint1_pos[0]],
            y=[base_pos[1], joint1_pos[1]],
            mode='lines',
            line=dict(
                color=self.colors['link1'],
                width=8
            ),
            name='Link 1',
            hovertemplate='Link 1<br>Length: %.2f m<extra></extra>' % kinematics.l1
        ))
        
        # Link 2 (joint 1 to end effector)
        fig.add_trace(go.Scatter(
            x=[joint1_pos[0], end_effector_pos[0]],
            y=[joint1_pos[1], end_effector_pos[1]],
            mode='lines',
            line=dict(
                color=self.colors['link2'],
                width=8
            ),
            name='Link 2',
            hovertemplate='Link 2<br>Length: %.2f m<extra></extra>' % kinematics.l2
        ))
        
        # Add joints
        # Base joint
        fig.add_trace(go.Scatter(
            x=[base_pos[0]],
            y=[base_pos[1]],
            mode='markers',
            marker=dict(
                size=12,
                color=self.colors['base'],
                symbol='square',
                line=dict(width=2, color='black')
            ),
            name='Base',
            hovertemplate='Base Joint<br>Position: (%.2f, %.2f)<extra></extra>' % (base_pos[0], base_pos[1])
        ))
        
        # Joint 1
        fig.add_trace(go.Scatter(
            x=[joint1_pos[0]],
            y=[joint1_pos[1]],
            mode='markers',
            marker=dict(
                size=10,
                color=self.colors['joint'],
                symbol='circle',
                line=dict(width=2, color='black')
            ),
            name='Joint 1',
            hovertemplate='Joint 1<br>Position: (%.2f, %.2f)<br>Angle: %.1f°<extra></extra>' % 
                         (joint1_pos[0], joint1_pos[1], np.degrees(q1))
        ))
        
        # End effector
        fig.add_trace(go.Scatter(
            x=[end_effector_pos[0]],
            y=[end_effector_pos[1]],
            mode='markers',
            marker=dict(
                size=12,
                color=self.colors['end_effector'],
                symbol='diamond',
                line=dict(width=2, color='black')
            ),
            name='End Effector',
            hovertemplate='End Effector<br>Position: (%.2f, %.2f)<extra></extra>' % 
                         (end_effector_pos[0], end_effector_pos[1])
        ))
        
        # Add target if specified
        if target_x is not None and target_y is not None:
            fig.add_trace(go.Scatter(
                x=[target_x],
                y=[target_y],
                mode='markers',
                marker=dict(
                    size=15,
                    color=self.colors['target'],
                    symbol='x',
                    line=dict(width=3)
                ),
                name='Target',
                hovertemplate='Target<br>Position: (%.2f, %.2f)<extra></extra>' % (target_x, target_y)
            ))
        
        # Update layout
        max_reach = kinematics.l1 + kinematics.l2
        margin = max_reach * 0.2
        
        fig.update_layout(
            title="2DOF Robotic Arm Visualization",
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            xaxis=dict(
                range=[-max_reach - margin, max_reach + margin],
                scaleanchor="y",
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                range=[-max_reach - margin, max_reach + margin],
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            **self.default_layout,
            width=600,
            height=600
        )
        
        return fig
    
    def create_workspace_plot(self, workspace_data: dict, highlight_points: Optional[List[Tuple[float, float]]] = None) -> go.Figure:
        """
        Create workspace visualization
        
        Args:
            workspace_data: Dictionary with 'x' and 'y' arrays of workspace points
            highlight_points: Optional points to highlight on workspace
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Add workspace points
        fig.add_trace(go.Scatter(
            x=workspace_data['x'],
            y=workspace_data['y'],
            mode='markers',
            marker=dict(
                size=3,
                color=self.colors['workspace'],
                opacity=0.6
            ),
            name='Reachable Workspace',
            hovertemplate='Position: (%.2f, %.2f)<extra></extra>'
        ))
        
        # Add highlighted points if provided
        if highlight_points is not None:
            highlight_x = [point[0] for point in highlight_points]
            highlight_y = [point[1] for point in highlight_points]
            fig.add_trace(go.Scatter(
                x=highlight_x,
                y=highlight_y,
                mode='markers',
                marker=dict(
                    size=8,
                    color=self.colors['target'],
                    symbol='star'
                ),
                name='Highlighted Points'
            ))
        
        fig.update_layout(
            title="Robot Workspace Analysis",
            xaxis_title="X Position (m)",
            yaxis_title="Y Position (m)",
            xaxis=dict(scaleanchor="y", scaleratio=1),
            **self.default_layout
        )
        
        return fig
    
    def create_joint_analysis_plot(self, q1_range: np.ndarray, q2_range: np.ndarray, 
                                  analysis_data: dict, analysis_type: str = "manipulability") -> go.Figure:
        """
        Create joint space analysis plot (manipulability, singularities, etc.)
        
        Args:
            q1_range: Array of joint 1 angles
            q2_range: Array of joint 2 angles
            analysis_data: Dictionary containing analysis results
            analysis_type: Type of analysis ("manipulability", "condition_number", etc.)
            
        Returns:
            Plotly figure object
        """
        fig = go.Figure()
        
        # Create heatmap
        fig.add_trace(go.Heatmap(
            x=np.degrees(q1_range),
            y=np.degrees(q2_range),
            z=analysis_data[analysis_type],
            colorscale='Viridis',
            colorbar=dict(title=analysis_type.capitalize()),
            hovertemplate='Joint 1: %{x}°<br>Joint 2: %{y}°<br>' + 
                         analysis_type.capitalize() + ': %{z:.4f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"Joint Space {analysis_type.capitalize()} Analysis",
            xaxis_title="Joint 1 Angle (degrees)",
            yaxis_title="Joint 2 Angle (degrees)",
            **self.default_layout
        )
        
        return fig
    
    def create_trajectory_analysis_plot(self, trajectory_data: pd.DataFrame) -> go.Figure:
        """
        Create trajectory analysis plot with multiple subplots
        
        Args:
            trajectory_data: DataFrame containing trajectory data
            
        Returns:
            Plotly figure object with subplots
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('End-Effector Path', 'Joint Angles', 'Joint Velocities', 'Tracking Error'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # End-effector path
        if 'actual_x' in trajectory_data.columns and 'actual_y' in trajectory_data.columns:
            fig.add_trace(
                go.Scatter(x=trajectory_data['actual_x'], y=trajectory_data['actual_y'],
                          mode='lines', name='Actual Path', line=dict(color=self.colors['link1'])),
                row=1, col=1
            )
        
        if 'desired_x' in trajectory_data.columns and 'desired_y' in trajectory_data.columns:
            fig.add_trace(
                go.Scatter(x=trajectory_data['desired_x'], y=trajectory_data['desired_y'],
                          mode='lines', name='Desired Path', line=dict(color=self.colors['target'], dash='dash')),
                row=1, col=1
            )
        
        # Joint angles
        fig.add_trace(
            go.Scatter(x=trajectory_data['time'], y=np.degrees(trajectory_data['q1']),
                      mode='lines', name='Joint 1', line=dict(color=self.colors['link1'])),
            row=1, col=2
        )
        fig.add_trace(
            go.Scatter(x=trajectory_data['time'], y=np.degrees(trajectory_data['q2']),
                      mode='lines', name='Joint 2', line=dict(color=self.colors['link2'])),
            row=1, col=2
        )
        
        # Joint velocities (if available)
        if 'q1_dot' in trajectory_data.columns:
            fig.add_trace(
                go.Scatter(x=trajectory_data['time'], y=trajectory_data['q1_dot'],
                          mode='lines', name='Joint 1 Vel', line=dict(color=self.colors['link1'])),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=trajectory_data['time'], y=trajectory_data['q2_dot'],
                          mode='lines', name='Joint 2 Vel', line=dict(color=self.colors['link2'])),
                row=2, col=1
            )
        
        # Tracking error
        if 'error_x' in trajectory_data.columns and 'error_y' in trajectory_data.columns:
            error_magnitude = np.sqrt(trajectory_data['error_x']**2 + trajectory_data['error_y']**2)
            fig.add_trace(
                go.Scatter(x=trajectory_data['time'], y=error_magnitude,
                          mode='lines', name='Position Error', line=dict(color=self.colors['end_effector'])),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Trajectory Analysis",
            height=800,
            **self.default_layout
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="X Position (m)", row=1, col=1)
        fig.update_yaxes(title_text="Y Position (m)", row=1, col=1)
        fig.update_xaxes(title_text="Time (s)", row=1, col=2)
        fig.update_yaxes(title_text="Angle (degrees)", row=1, col=2)
        fig.update_xaxes(title_text="Time (s)", row=2, col=1)
        fig.update_yaxes(title_text="Velocity (rad/s)", row=2, col=1)
        fig.update_xaxes(title_text="Time (s)", row=2, col=2)
        fig.update_yaxes(title_text="Error (m)", row=2, col=2)
        
        return fig
    
    def create_dynamics_plot(self, simulation_data: pd.DataFrame) -> go.Figure:
        """
        Create dynamics analysis plot
        
        Args:
            simulation_data: DataFrame containing simulation data
            
        Returns:
            Plotly figure object with dynamics plots
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Joint Torques', 'Joint Accelerations', 'Energy Analysis', 'Phase Portrait'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Joint torques
        if 'tau1' in simulation_data.columns:
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['tau1'],
                          mode='lines', name='Joint 1 Torque', line=dict(color=self.colors['link1'])),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['tau2'],
                          mode='lines', name='Joint 2 Torque', line=dict(color=self.colors['link2'])),
                row=1, col=1
            )
        
        # Joint accelerations (if available)
        if 'q1_ddot' in simulation_data.columns:
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['q1_ddot'],
                          mode='lines', name='Joint 1 Accel', line=dict(color=self.colors['link1'])),
                row=1, col=2
            )
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['q2_ddot'],
                          mode='lines', name='Joint 2 Accel', line=dict(color=self.colors['link2'])),
                row=1, col=2
            )
        
        # Energy analysis (if available)
        if 'kinetic_energy' in simulation_data.columns:
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['kinetic_energy'],
                          mode='lines', name='Kinetic', line=dict(color=self.colors['target'])),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['potential_energy'],
                          mode='lines', name='Potential', line=dict(color=self.colors['joint'])),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['total_energy'],
                          mode='lines', name='Total', line=dict(color=self.colors['end_effector'])),
                row=2, col=1
            )
        
        # Phase portrait
        if 'q1_dot' in simulation_data.columns:
            fig.add_trace(
                go.Scatter(x=np.degrees(simulation_data['q1']), y=simulation_data['q1_dot'],
                          mode='lines', name='Joint 1 Phase', line=dict(color=self.colors['link1'])),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(x=np.degrees(simulation_data['q2']), y=simulation_data['q2_dot'],
                          mode='lines', name='Joint 2 Phase', line=dict(color=self.colors['link2'])),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Dynamics Analysis",
            height=800,
            **self.default_layout
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Time (s)", row=1, col=1)
        fig.update_yaxes(title_text="Torque (Nm)", row=1, col=1)
        fig.update_xaxes(title_text="Time (s)", row=1, col=2)
        fig.update_yaxes(title_text="Acceleration (rad/s²)", row=1, col=2)
        fig.update_xaxes(title_text="Time (s)", row=2, col=1)
        fig.update_yaxes(title_text="Energy (J)", row=2, col=1)
        fig.update_xaxes(title_text="Angle (degrees)", row=2, col=2)
        fig.update_yaxes(title_text="Velocity (rad/s)", row=2, col=2)
        
        return fig
    
    def create_control_performance_plot(self, simulation_data: pd.DataFrame) -> go.Figure:
        """
        Create control performance analysis plot
        
        Args:
            simulation_data: DataFrame containing simulation data
            
        Returns:
            Plotly figure object
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Position Error', 'Control Effort', 'Error vs Control', 'Control Signals'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}],
                   [{"type": "scatter"}, {"type": "scatter"}]]
        )
        
        # Position error
        if 'error_x' in simulation_data.columns and 'error_y' in simulation_data.columns:
            error_magnitude = np.sqrt(simulation_data['error_x']**2 + simulation_data['error_y']**2)
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=error_magnitude,
                          mode='lines', name='Position Error', line=dict(color=self.colors['end_effector'])),
                row=1, col=1
            )
        
        # Control effort
        if 'tau1' in simulation_data.columns:
            control_effort = np.sqrt(simulation_data['tau1']**2 + simulation_data['tau2']**2)
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=control_effort,
                          mode='lines', name='Control Effort', line=dict(color=self.colors['joint'])),
                row=1, col=2
            )
        
        # Error vs Control (scatter plot)
        if 'tau1' in simulation_data.columns and 'error_x' in simulation_data.columns:
            error_magnitude = np.sqrt(simulation_data['error_x']**2 + simulation_data['error_y']**2)
            control_effort = np.sqrt(simulation_data['tau1']**2 + simulation_data['tau2']**2)
            fig.add_trace(
                go.Scatter(x=error_magnitude, y=control_effort,
                          mode='markers', name='Error vs Control',
                          marker=dict(color=self.colors['target'], size=4, opacity=0.6)),
                row=2, col=1
            )
        
        # Individual control signals
        if 'tau1' in simulation_data.columns:
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['tau1'],
                          mode='lines', name='τ₁', line=dict(color=self.colors['link1'])),
                row=2, col=2
            )
            fig.add_trace(
                go.Scatter(x=simulation_data['time'], y=simulation_data['tau2'],
                          mode='lines', name='τ₂', line=dict(color=self.colors['link2'])),
                row=2, col=2
            )
        
        # Update layout
        fig.update_layout(
            title="Control Performance Analysis",
            height=800,
            **self.default_layout
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Time (s)", row=1, col=1)
        fig.update_yaxes(title_text="Error (m)", row=1, col=1)
        fig.update_xaxes(title_text="Time (s)", row=1, col=2)
        fig.update_yaxes(title_text="Control Effort", row=1, col=2)
        fig.update_xaxes(title_text="Position Error (m)", row=2, col=1)
        fig.update_yaxes(title_text="Control Effort", row=2, col=1)
        fig.update_xaxes(title_text="Time (s)", row=2, col=2)
        fig.update_yaxes(title_text="Torque (Nm)", row=2, col=2)
        
        return fig
    
    def create_3d_animation_plot(self, trajectory_data: pd.DataFrame, time_steps: int = 50) -> go.Figure:
        """
        Create 3D animation plot of robot motion
        
        Args:
            trajectory_data: DataFrame containing trajectory data
            time_steps: Number of time steps to include in animation
            
        Returns:
            Plotly figure object with animation
        """
        # Sample data for animation
        if len(trajectory_data) > time_steps:
            indices = np.linspace(0, len(trajectory_data) - 1, time_steps, dtype=int)
            sampled_data = trajectory_data.iloc[indices]
        else:
            sampled_data = trajectory_data
        
        fig = go.Figure()
        
        # Add frames for animation
        frames = []
        for i, row in sampled_data.iterrows():
            frame_data = []
            
            # End-effector trace
            if 'actual_x' in sampled_data.columns:
                trace_data = sampled_data.iloc[:sampled_data.index.get_loc(i) + 1]
                frame_data.append(go.Scatter3d(
                    x=trace_data['actual_x'],
                    y=trace_data['actual_y'],
                    z=trace_data['time'],
                    mode='lines',
                    line=dict(color=self.colors['end_effector'], width=4),
                    name='End-Effector Path'
                ))
            
            frames.append(go.Frame(data=frame_data, name=str(i)))
        
        # Initial trace
        if 'actual_x' in trajectory_data.columns:
            fig.add_trace(go.Scatter3d(
                x=trajectory_data['actual_x'][:1],
                y=trajectory_data['actual_y'][:1],
                z=trajectory_data['time'][:1],
                mode='lines',
                line=dict(color=self.colors['end_effector'], width=4),
                name='End-Effector Path'
            ))
        
        fig.frames = frames
        
        # Add animation controls
        fig.update_layout(
            title="3D Robot Motion Animation",
            scene=dict(
                xaxis_title="X Position (m)",
                yaxis_title="Y Position (m)",
                zaxis_title="Time (s)"
            ),
            updatemenus=[{
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 100, "redraw": True},
                                       "fromcurrent": True, "transition": {"duration": 50}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                         "mode": "immediate", "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }],
            **self.default_layout
        )
        
        return fig

