import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class Visualizer:
    """
    Visualization utilities for EV energy consumption analysis
    """
    
    def __init__(self):
        # Set default color palette
        self.color_palette = px.colors.qualitative.Set1
        
    def plot_correlation_matrix(self, df, title="Correlation Matrix"):
        """
        Create an interactive correlation matrix heatmap
        
        Args:
            df: DataFrame with numeric columns
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        # Calculate correlation matrix
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title=title,
            color_continuous_scale='RdBu_r',
            range_color=[-1, 1]
        )
        
        fig.update_layout(
            width=800,
            height=600,
            title_x=0.5
        )
        
        return fig
    
    def plot_distribution(self, df, column, plot_type='histogram', title=None):
        """
        Plot distribution of a single variable
        
        Args:
            df: DataFrame
            column: Column name to plot
            plot_type: Type of plot ('histogram', 'box', 'violin')
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        if title is None:
            title = f"Distribution of {column}"
        
        if plot_type == 'histogram':
            fig = px.histogram(
                df, x=column, nbins=30, title=title,
                marginal="box"  # Add box plot on top
            )
        elif plot_type == 'box':
            fig = px.box(df, y=column, title=title)
        elif plot_type == 'violin':
            fig = px.violin(df, y=column, title=title, box=True)
        else:
            raise ValueError("plot_type must be 'histogram', 'box', or 'violin'")
        
        fig.update_layout(title_x=0.5)
        return fig
    
    def plot_scatter_matrix(self, df, columns=None, title="Scatter Matrix"):
        """
        Create a scatter matrix for multiple variables
        
        Args:
            df: DataFrame
            columns: List of columns to include (if None, use all numeric)
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
            columns = columns[:6]  # Limit to 6 columns for readability
        
        fig = px.scatter_matrix(
            df[columns],
            title=title,
            height=800
        )
        
        fig.update_layout(title_x=0.5)
        return fig
    
    def plot_energy_vs_features(self, df, energy_col='energy_consumption', features=None):
        """
        Plot energy consumption vs multiple features
        
        Args:
            df: DataFrame
            energy_col: Energy consumption column name
            features: List of feature columns
            
        Returns:
            Plotly figure with subplots
        """
        
        if features is None:
            features = [col for col in df.select_dtypes(include=[np.number]).columns 
                       if col != energy_col][:4]
        
        n_features = len(features)
        cols = 2
        rows = (n_features + 1) // 2
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=features,
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        for i, feature in enumerate(features):
            row = i // cols + 1
            col = i % cols + 1
            
            fig.add_trace(
                go.Scatter(
                    x=df[feature],
                    y=df[energy_col],
                    mode='markers',
                    name=feature,
                    opacity=0.6,
                    showlegend=False
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title="Energy Consumption vs Features",
            height=400 * rows,
            title_x=0.5
        )
        
        return fig
    
    def plot_time_series(self, df, time_col, value_col, title=None):
        """
        Plot time series data
        
        Args:
            df: DataFrame
            time_col: Time column name
            value_col: Value column name
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        if title is None:
            title = f"{value_col} over time"
        
        fig = px.line(
            df, x=time_col, y=value_col,
            title=title
        )
        
        fig.update_layout(
            title_x=0.5,
            xaxis_title="Time",
            yaxis_title=value_col
        )
        
        return fig
    
    def plot_model_comparison(self, results_dict, metric='r2_score'):
        """
        Plot comparison of model performance
        
        Args:
            results_dict: Dictionary with model results
            metric: Metric to compare
            
        Returns:
            Plotly figure
        """
        
        models = list(results_dict.keys())
        values = [results_dict[model][metric] for model in models]
        
        fig = px.bar(
            x=models, y=values,
            title=f"Model Comparison - {metric.upper()}",
            labels={'x': 'Model', 'y': metric.upper()}
        )
        
        fig.update_layout(title_x=0.5)
        return fig
    
    def plot_prediction_vs_actual(self, y_true, y_pred, model_name, title=None):
        """
        Plot predicted vs actual values
        
        Args:
            y_true: True values
            y_pred: Predicted values
            model_name: Name of the model
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        if title is None:
            title = f"Predicted vs Actual - {model_name}"
        
        # Calculate metrics for display
        from sklearn.metrics import r2_score, mean_squared_error
        r2 = r2_score(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(
            go.Scatter(
                x=y_true,
                y=y_pred,
                mode='markers',
                name='Predictions',
                opacity=0.6,
                text=[f"True: {t:.2f}<br>Pred: {p:.2f}" for t, p in zip(y_true, y_pred)],
                hovertemplate='%{text}<extra></extra>'
            )
        )
        
        # Add perfect prediction line
        min_val = min(min(y_true), min(y_pred))
        max_val = max(max(y_true), max(y_pred))
        fig.add_trace(
            go.Scatter(
                x=[min_val, max_val],
                y=[min_val, max_val],
                mode='lines',
                name='Perfect Prediction',
                line=dict(color='red', dash='dash')
            )
        )
        
        fig.update_layout(
            title=f"{title}<br>R² = {r2:.4f}, RMSE = {rmse:.4f}",
            xaxis_title="Actual Values",
            yaxis_title="Predicted Values",
            title_x=0.5
        )
        
        return fig
    
    def plot_residuals(self, y_true, y_pred, model_name):
        """
        Plot residuals analysis
        
        Args:
            y_true: True values
            y_pred: Predicted values
            model_name: Name of the model
            
        Returns:
            Plotly figure with subplots
        """
        
        residuals = y_true - y_pred
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=["Residuals vs Predicted", "Residuals Distribution"],
            horizontal_spacing=0.1
        )
        
        # Residuals vs Predicted
        fig.add_trace(
            go.Scatter(
                x=y_pred,
                y=residuals,
                mode='markers',
                name='Residuals',
                opacity=0.6
            ),
            row=1, col=1
        )
        
        # Add horizontal line at y=0
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        
        # Residuals histogram
        fig.add_trace(
            go.Histogram(
                x=residuals,
                name='Residuals Distribution',
                nbinsx=30
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=f"Residuals Analysis - {model_name}",
            title_x=0.5,
            height=400
        )
        
        fig.update_xaxes(title_text="Predicted Values", row=1, col=1)
        fig.update_yaxes(title_text="Residuals", row=1, col=1)
        fig.update_xaxes(title_text="Residuals", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        
        return fig
    
    def plot_feature_importance(self, feature_names, importances, model_name):
        """
        Plot feature importance
        
        Args:
            feature_names: List of feature names
            importances: List of importance values
            model_name: Name of the model
            
        Returns:
            Plotly figure
        """
        
        # Sort by importance
        importance_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=True)
        
        fig = px.bar(
            importance_df,
            x='Importance',
            y='Feature',
            orientation='h',
            title=f"Feature Importance - {model_name}"
        )
        
        fig.update_layout(title_x=0.5)
        return fig
    
    def plot_learning_curve(self, train_scores, val_scores, title="Learning Curve"):
        """
        Plot learning curve for neural network training
        
        Args:
            train_scores: Training scores
            val_scores: Validation scores
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        epochs = list(range(1, len(train_scores) + 1))
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=train_scores,
                mode='lines',
                name='Training',
                line=dict(color='blue')
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=epochs,
                y=val_scores,
                mode='lines',
                name='Validation',
                line=dict(color='red')
            )
        )
        
        fig.update_layout(
            title=title,
            xaxis_title="Epoch",
            yaxis_title="Score",
            title_x=0.5
        )
        
        return fig
    
    def plot_energy_breakdown(self, breakdown_dict, title="Energy Consumption Breakdown"):
        """
        Plot energy consumption breakdown as pie chart
        
        Args:
            breakdown_dict: Dictionary with component names and values
            title: Plot title
            
        Returns:
            Plotly figure
        """
        
        fig = px.pie(
            values=list(breakdown_dict.values()),
            names=list(breakdown_dict.keys()),
            title=title
        )
        
        fig.update_layout(title_x=0.5)
        return fig
    
    def plot_range_estimation(self, speed_range, consumption_range, current_speed, current_consumption):
        """
        Plot range estimation analysis
        
        Args:
            speed_range: Array of speeds
            consumption_range: Array of corresponding consumptions
            current_speed: Current speed
            current_consumption: Current consumption
            
        Returns:
            Plotly figure
        """
        
        fig = go.Figure()
        
        # Plot consumption curve
        fig.add_trace(
            go.Scatter(
                x=speed_range,
                y=consumption_range,
                mode='lines',
                name='Energy Consumption',
                line=dict(color='blue', width=3)
            )
        )
        
        # Add current point
        fig.add_trace(
            go.Scatter(
                x=[current_speed],
                y=[current_consumption],
                mode='markers',
                name='Current Condition',
                marker=dict(color='red', size=12)
            )
        )
        
        fig.update_layout(
            title="Energy Consumption vs Speed",
            xaxis_title="Speed (km/h)",
            yaxis_title="Energy Consumption (kWh/100km)",
            title_x=0.5
        )
        
        return fig
    
    def create_dashboard_summary(self, df, models_results=None):
        """
        Create a comprehensive dashboard summary
        
        Args:
            df: DataFrame with EV data
            models_results: Dictionary with model results
            
        Returns:
            Dictionary with multiple figures
        """
        
        figures = {}
        
        # Data overview
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) > 1:
            figures['correlation'] = self.plot_correlation_matrix(df[numeric_cols])
        
        # Energy consumption distribution
        if 'energy_consumption' in df.columns:
            figures['energy_dist'] = self.plot_distribution(
                df, 'energy_consumption', 'histogram'
            )
        
        # Feature relationships
        if 'energy_consumption' in df.columns and len(numeric_cols) > 1:
            other_features = [col for col in numeric_cols if col != 'energy_consumption'][:4]
            figures['energy_vs_features'] = self.plot_energy_vs_features(
                df, 'energy_consumption', other_features
            )
        
        # Model comparison
        if models_results:
            figures['model_comparison'] = self.plot_model_comparison(models_results)
        
        return figures
