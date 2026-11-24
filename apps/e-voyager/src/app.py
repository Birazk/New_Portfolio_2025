import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import io
import base64
from datetime import datetime

# Import custom modules
from models.ml_models import MLModels
from utils.data_processor import DataProcessor
from utils.visualization import Visualizer
from utils.energy_calculator import EnergyCalculator
# Database removed for VS Code compatibility
from utils.map_utils import MapVisualizer
from utils.cost_calculator import CostCalculator

db = None  # database layer is not used in the web demo

# Configure page
st.set_page_config(
    page_title="EV Energy Consumption & Range Prediction Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'models' not in st.session_state:
    st.session_state.models = None
if 'trained_models' not in st.session_state:
    st.session_state.trained_models = {}
if 'predictions' not in st.session_state:
    st.session_state.predictions = {}
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now())}"
if 'current_data_record_id' not in st.session_state:
    st.session_state.current_data_record_id = None

# Database functionality removed for VS Code compatibility

# Database removed for simplified VS Code setup

def help_documentation_page():
    st.header("📚 Help & Documentation")
    st.markdown("*Comprehensive guide to formulas, models, and processes used in the EV Energy Dashboard*")
    
    # Table of Contents
    st.subheader("📋 Table of Contents")
    st.markdown("""
    1. [Physics-Based Energy Consumption Model](#physics-based-energy-consumption-model)
    2. [Machine Learning Models](#machine-learning-models)
    3. [Data Processing Pipeline](#data-processing-pipeline)
    4. [Range Estimation Methods](#range-estimation-methods)
    5. [Database Schema](#database-schema)
    6. [References](#references)
    """)
    
    # Physics-Based Energy Consumption Model
    st.subheader("⚡ Physics-Based Energy Consumption Model")
    st.markdown("*Based on BMW i3 case study methodology from Miri et al. (2020)*")
    
    with st.expander("🔬 Fundamental Physics Equations", expanded=False):
        st.markdown("""
        **Total Energy Consumption Formula:**
        ```
        E_total = (P_mechanical + P_auxiliary + P_temperature) / η_system
        ```
        
        **Forces Acting on Vehicle:**
        
        1. **Aerodynamic Drag Force:**
        ```
        F_aero = 0.5 × ρ_air × A_front × C_d × v²
        ```
        - ρ_air: Air density (1.225 kg/m³ at sea level)
        - A_front: Frontal area (2.38 m² for BMW i3)
        - C_d: Drag coefficient (0.29 for BMW i3)
        - v: Vehicle speed (m/s)
        
        2. **Rolling Resistance Force:**
        ```
        F_rolling = C_r × m × g × cos(θ)
        ```
        - C_r: Rolling resistance coefficient (0.01)
        - m: Vehicle mass (1195 kg for BMW i3)
        - g: Gravitational acceleration (9.81 m/s²)
        - θ: Road slope angle (radians)
        
        3. **Gravitational Force (Road Slope):**
        ```
        F_gravity = m × g × sin(θ)
        ```
        
        4. **Inertial Force (Acceleration/Deceleration):**
        ```
        F_inertial = m × a
        ```
        - a: Vehicle acceleration (m/s²)
        
        **Total Tractive Force:**
        ```
        F_total = F_aero + F_rolling + F_gravity + F_inertial
        ```
        
        **Mechanical Power at Wheels:**
        ```
        P_mechanical = F_total × v / 1000  (kW)
        ```
        
        **System Efficiencies:**
        - Motor efficiency (η_motor): 90%
        - Transmission efficiency (η_trans): 95%
        - Battery efficiency (η_battery): 95%
        - Regenerative braking efficiency: 70%
        """)
    
    with st.expander("🌡️ Temperature Effects on Energy Consumption", expanded=False):
        st.markdown("""
        **HVAC Power Consumption:**
        
        The heating, ventilation, and air conditioning (HVAC) system power consumption varies with ambient temperature:
        
        ```
        P_hvac = |T_ambient - T_optimal| × k_hvac
        ```
        
        Where:
        - T_optimal = 22°C (minimal HVAC usage)
        - k_hvac = 0.15 kW/°C for heating (T < 22°C)
        - k_hvac = 0.12 kW/°C for cooling (T > 22°C)
        - Maximum HVAC power capped at 5 kW
        
        **Total Auxiliary Power:**
        ```
        P_auxiliary = P_base + P_hvac
        ```
        - P_base: Base auxiliary power (1.0 kW for electronics, lights, etc.)
        """)
    
    with st.expander("🔋 Energy Consumption Calculation", expanded=False):
        st.markdown("""
        **Final Energy Consumption (kWh/100km):**
        
        ```
        E_consumption = (P_total × 100) / v_kmh
        ```
        
        Where:
        ```
        P_total = (P_mechanical / η_motor / η_trans) + P_auxiliary + P_hvac
        ```
        
        **With Battery Efficiency:**
        ```
        E_final = E_consumption / η_battery
        ```
        
        **Range Calculation:**
        ```
        Range = (E_available / E_consumption) × 100
        ```
        
        Where:
        ```
        E_available = Battery_capacity × (SOC_current / 100)
        ```
        """)
    
    # Machine Learning Models
    st.subheader("🤖 Machine Learning Models")
    
    with st.expander("📊 Model Descriptions and Applications", expanded=False):
        st.markdown("""
        **1. Linear Regression**
        ```
        y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε
        ```
        - **Use case:** Baseline model for understanding linear relationships
        - **Advantages:** Interpretable coefficients, fast training
        - **Limitations:** Assumes linear relationships
        
        **2. Random Forest Regressor**
        ```
        ŷ = (1/B) × Σ(Tree_b(x))
        ```
        - **Use case:** Capturing non-linear relationships and feature interactions
        - **Advantages:** Handles non-linearity, provides feature importance
        - **Parameters:** 100 estimators, max_depth=10
        
        **3. Neural Network (MLP Regressor)**
        ```
        h₁ = σ(W₁x + b₁)
        h₂ = σ(W₂h₁ + b₂)
        y = W₃h₂ + b₃
        ```
        - **Use case:** Complex pattern recognition in energy consumption
        - **Architecture:** Configurable hidden layers (1-3), neurons per layer (10-200)
        - **Activation:** ReLU for hidden layers, linear for output
        
        **4. Support Vector Regression (SVR)**
        ```
        f(x) = Σ(αᵢ - αᵢ*)K(xᵢ, x) + b
        ```
        - **Use case:** Robust prediction with RBF kernel
        - **Kernel:** Radial Basis Function (RBF)
        - **Advantages:** Effective in high-dimensional spaces
        
        **5. Gradient Boosting Regressor**
        ```
        F_m(x) = F_{m-1}(x) + γ_m × h_m(x)
        ```
        - **Use case:** Sequential improvement of predictions
        - **Parameters:** 100 estimators, learning_rate=0.1, max_depth=6
        """)
    
    with st.expander("📈 Model Evaluation Metrics", expanded=False):
        st.markdown("""
        **R² Score (Coefficient of Determination):**
        ```
        R² = 1 - (SS_res / SS_tot)
        ```
        Where:
        - SS_res = Σ(yᵢ - ŷᵢ)² (Sum of squares of residuals)
        - SS_tot = Σ(yᵢ - ȳ)² (Total sum of squares)
        
        **Root Mean Square Error (RMSE):**
        ```
        RMSE = √[(1/n) × Σ(yᵢ - ŷᵢ)²]
        ```
        
        **Mean Absolute Error (MAE):**
        ```
        MAE = (1/n) × Σ|yᵢ - ŷᵢ|
        ```
        
        **Interpretation:**
        - R² closer to 1.0 indicates better model fit
        - Lower RMSE and MAE indicate better prediction accuracy
        - RMSE penalizes larger errors more than MAE
        """)
    
    # Data Processing Pipeline
    st.subheader("🔧 Data Processing Pipeline")
    
    with st.expander("📋 Data Validation and Cleaning", expanded=False):
        st.markdown("""
        **Required Data Columns:**
        - `speed` (km/h): Vehicle speed
        - `acceleration` (m/s²): Vehicle acceleration
        - `energy_consumption` (kWh/100km): Target variable
        
        **Optional Columns:**
        - `road_slope` (degrees): Road gradient
        - `temperature` (°C): Ambient temperature
        - `auxiliary_power` (kW): Auxiliary device power
        - `time`, `distance`, `battery_soc`
        
        **Data Cleaning Process:**
        1. Remove completely empty rows and columns
        2. Standardize column names (lowercase, underscores)
        3. Outlier detection using IQR method:
        ```
        Q1 = 25th percentile
        Q3 = 75th percentile
        IQR = Q3 - Q1
        Lower_bound = Q1 - 1.5 × IQR
        Upper_bound = Q3 + 1.5 × IQR
        ```
        4. Cap outliers instead of removal to preserve data
        """)

def main():
    st.title("🔋 Electric Vehicle Energy Consumption & Range Prediction Dashboard")
    st.markdown("*Advanced Machine Learning Analysis for EV Energy Efficiency*")
    
    # Simple, clean navigation
    st.sidebar.title("🔋 EV Dashboard")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navigate to:",
        [
            "🏠 Dashboard Overview",
            "📤 Upload Data", 
            "📊 Explore Data",
            "🤖 Train Models",
            "🎯 Make Predictions",
            "📈 Compare Models",
            "⚡ Energy Calculator",
            "💰 Cost Analysis (Nepal)",
            "🗺️ Route Maps",
            "🔥 Energy Heatmaps", 
            "📍 GPS Tracking",
            "📚 Help & Guide"
        ]
    )
    
    # Add helpful navigation tips
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Quick Start:**")
    if st.session_state.data is None:
        st.sidebar.info("Start by uploading data or use sample data")
    elif not st.session_state.trained_models:
        st.sidebar.info("Next: Train ML models with your data")
    else:
        st.sidebar.success("Ready for predictions and analysis!")
    
    # Database status and data browser in sidebar
    if db:
        with st.sidebar.expander("📊 Database Status", expanded=False):
            try:
                stats = db.get_data_statistics()
                st.metric("Total Datasets", stats['total_datasets'])
                st.metric("Total Data Points", stats['total_data_points'])
                st.metric("Total Predictions", stats['total_predictions'])
                if stats['last_upload']:
                    st.caption(f"Last upload: {stats['last_upload'].strftime('%Y-%m-%d %H:%M')}")
                st.success("Database connected")
            except Exception as e:
                st.error("Database connection issue")
        
        with st.sidebar.expander("📁 Session Data History", expanded=False):
            try:
                data_records = db.get_session_data_records(st.session_state.session_id)
                if data_records:
                    for record in data_records[:5]:  # Show last 5 records
                        st.caption(f"📄 {record['filename']}")
                        st.caption(f"Records: {record['record_count']}")
                        st.caption(f"Date: {record['upload_date'].strftime('%H:%M')}")
                        if st.button(f"Load", key=f"load_{record['id']}"):
                            loaded_df = db.load_ev_data(record['id'])
                            st.session_state.data = loaded_df
                            st.session_state.current_data_record_id = record['id']
                            st.rerun()
                        st.divider()
                else:
                    st.caption("No data uploaded yet")
            except Exception as e:
                st.error("Error loading data history")
    else:
        with st.sidebar.expander("📊 Database Status", expanded=False):
            st.error("Database not available")
    
    if page == "🏠 Dashboard Overview":
        dashboard_overview_page()
    elif page == "📤 Upload Data":
        data_upload_page()
    elif page == "📊 Explore Data":
        data_exploration_page()
    elif page == "🤖 Train Models":
        model_training_page()
    elif page == "🎯 Make Predictions":
        prediction_page()
    elif page == "📈 Compare Models":
        model_comparison_page()
    elif page == "⚡ Energy Calculator":
        realtime_calculator_page()
    elif page == "💰 Cost Analysis (Nepal)":
        cost_comparison_nepal_page()
    elif page == "🗺️ Route Maps":
        route_visualization_page()
    elif page == "🔥 Energy Heatmaps":
        energy_heatmaps_page()
    elif page == "📍 GPS Tracking":
        gps_tracking_page()
    elif page == "📚 Help & Guide":
        help_documentation_page()

def data_upload_page():
    st.header("📁 Data Upload & Overview")
    
    # Sample data info
    with st.expander("📋 Expected Data Format", expanded=False):
        st.markdown("""
        **Required Columns for EV Energy Consumption Analysis:**
        - `speed` (km/h): Vehicle speed
        - `acceleration` (m/s²): Vehicle acceleration
        - `road_slope` (°): Road gradient/slope
        - `temperature` (°C): Ambient temperature
        - `energy_consumption` (kWh/100km): Target variable
        
        **Optional Columns:**
        - `time` (s): Time stamps
        - `distance` (km): Distance traveled
        - `battery_soc` (%): State of Charge
        - `regenerative_braking` (kW): Regenerative braking power
        - `auxiliary_power` (kW): Power consumption of auxiliary devices
        """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload your EV dataset (CSV or Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file containing EV driving data"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            data_processor = DataProcessor()
            df = data_processor.load_data(uploaded_file)
            st.session_state.data = df
            
            # Save to database if available
            if db:
                try:
                    data_record_id = db.save_ev_data(
                        df, 
                        st.session_state.session_id, 
                        uploaded_file.name
                    )
                    st.session_state.current_data_record_id = data_record_id
                    st.success(f"✅ Data loaded and saved to database! Shape: {df.shape}")
                except Exception as e:
                    st.warning(f"Data loaded but database save failed: {str(e)}")
                    st.success(f"✅ Data loaded successfully! Shape: {df.shape}")
            else:
                st.success(f"✅ Data loaded successfully! Shape: {df.shape}")
            
            # Display basic info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(df))
            with col2:
                st.metric("Features", len(df.columns))
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            with col4:
                if 'energy_consumption' in df.columns:
                    st.metric("Avg Energy Consumption", f"{df['energy_consumption'].mean():.2f} kWh/100km")
                else:
                    st.metric("Target Column", "Not Found")
            
            # Data preview
            st.subheader("📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Data validation
            st.subheader("🔍 Data Validation")
            validation_results = data_processor.validate_data(df)
            
            if validation_results['is_valid']:
                st.success("✅ Data validation passed!")
            else:
                st.error("❌ Data validation failed:")
                for error in validation_results['errors']:
                    st.error(f"• {error}")
            
            # Data statistics
            if st.checkbox("Show Detailed Statistics"):
                st.subheader("📈 Statistical Summary")
                st.dataframe(df.describe(), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
    
    else:
        # Generate sample data option
        st.subheader("🧪 Generate Sample Data")
        st.info("No data uploaded. You can generate sample EV data for testing.")
        
        if st.button("Generate Sample EV Dataset"):
            data_processor = DataProcessor()
            sample_df = data_processor.generate_sample_data(1000)
            st.session_state.data = sample_df
            
            # Save to database if available
            if db:
                try:
                    data_record_id = db.save_ev_data(
                        sample_df, 
                        st.session_state.session_id, 
                        "Generated_Sample_Data"
                    )
                    st.session_state.current_data_record_id = data_record_id
                    st.success("✅ Sample data generated and saved to database!")
                except Exception as e:
                    st.warning(f"Sample data generated but database save failed: {str(e)}")
                    st.success("✅ Sample data generated successfully!")
            else:
                st.success("✅ Sample data generated successfully!")
            
            st.dataframe(sample_df.head(), use_container_width=True)

def data_exploration_page():
    st.header("🔍 Data Exploration & Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first in the 'Data Upload & Overview' page.")
        return
    
    df = st.session_state.data
    visualizer = Visualizer()
    
    # Correlation Analysis
    st.subheader("🔗 Correlation Analysis")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) > 1:
        fig_corr = visualizer.plot_correlation_matrix(df[numeric_cols])
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Feature Distribution
    st.subheader("📊 Feature Distributions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        feature_to_plot = st.selectbox("Select feature for distribution", numeric_cols)
        
    with col2:
        plot_type = st.selectbox("Plot type", ["Histogram", "Box Plot", "Violin Plot"])
    
    if plot_type == "Histogram":
        fig = px.histogram(df, x=feature_to_plot, nbins=30, title=f"Distribution of {feature_to_plot}")
    elif plot_type == "Box Plot":
        fig = px.box(df, y=feature_to_plot, title=f"Box Plot of {feature_to_plot}")
    else:  # Violin Plot
        fig = px.violin(df, y=feature_to_plot, title=f"Violin Plot of {feature_to_plot}")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Time Series Analysis (if time column exists)
    if 'time' in df.columns or any('time' in col.lower() for col in df.columns):
        st.subheader("⏰ Time Series Analysis")
        
        time_col = 'time' if 'time' in df.columns else [col for col in df.columns if 'time' in col.lower()][0]
        
        col1, col2 = st.columns(2)
        with col1:
            y_feature = st.selectbox("Select Y-axis feature", numeric_cols, key="time_series_y")
        
        if time_col in df.columns:
            fig_ts = px.line(df, x=time_col, y=y_feature, title=f"{y_feature} over Time")
            st.plotly_chart(fig_ts, use_container_width=True)
    
    # Scatter Plot Analysis
    st.subheader("🎯 Scatter Plot Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_feature = st.selectbox("X-axis feature", numeric_cols, key="scatter_x")
    with col2:
        y_feature = st.selectbox("Y-axis feature", numeric_cols, key="scatter_y")
    with col3:
        color_feature = st.selectbox("Color by (optional)", ["None"] + numeric_cols, key="scatter_color")
    
    if color_feature == "None":
        fig_scatter = px.scatter(df, x=x_feature, y=y_feature, title=f"{y_feature} vs {x_feature}")
    else:
        fig_scatter = px.scatter(df, x=x_feature, y=y_feature, color=color_feature, 
                               title=f"{y_feature} vs {x_feature} (colored by {color_feature})")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Energy Consumption Analysis
    if 'energy_consumption' in df.columns:
        st.subheader("⚡ Energy Consumption Analysis")
        
        # Energy consumption by different factors
        factor_options = [col for col in numeric_cols if col != 'energy_consumption']
        
        if factor_options:
            selected_factor = st.selectbox("Analyze energy consumption by:", factor_options)
            
            # Create bins for continuous variables
            df_binned = df.copy()
            df_binned[f'{selected_factor}_bin'] = pd.cut(df[selected_factor], bins=5, labels=False)
            
            fig_energy = px.box(df_binned, x=f'{selected_factor}_bin', y='energy_consumption',
                              title=f"Energy Consumption by {selected_factor} (binned)")
            st.plotly_chart(fig_energy, use_container_width=True)

def model_training_page():
    st.header("🤖 Machine Learning Model Training")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first in the 'Data Upload & Overview' page.")
        return
    
    df = st.session_state.data
    
    # Feature selection
    st.subheader("🎯 Feature Selection")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Target variable selection
    target_options = [col for col in numeric_cols if 'energy' in col.lower() or 'consumption' in col.lower()]
    if not target_options:
        target_options = numeric_cols
    
    target_col = st.selectbox("Select Target Variable", target_options)
    
    # Feature variable selection
    feature_options = [col for col in numeric_cols if col != target_col]
    selected_features = st.multiselect(
        "Select Features for Training",
        feature_options,
        default=feature_options[:5] if len(feature_options) >= 5 else feature_options
    )
    
    if not selected_features:
        st.warning("⚠️ Please select at least one feature for training.")
        return
    
    # Model configuration
    st.subheader("⚙️ Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_size = st.slider("Test Set Size", 0.1, 0.5, 0.2, 0.05)
        random_state = st.number_input("Random State", 0, 1000, 42)
    
    with col2:
        models_to_train = st.multiselect(
            "Select Models to Train",
            ["Linear Regression", "Random Forest", "Neural Network", "Support Vector Regression", "Gradient Boosting"],
            default=["Linear Regression", "Random Forest", "Neural Network"]
        )
    
    # Neural Network specific parameters
    if "Neural Network" in models_to_train:
        st.subheader("🧠 Neural Network Parameters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hidden_layers = st.selectbox("Hidden Layers", [1, 2, 3], index=1)
        with col2:
            neurons_per_layer = st.slider("Neurons per Layer", 10, 200, 64)
        with col3:
            epochs = st.slider("Training Epochs", 50, 500, 100)
    
    # Train models
    if st.button("🚀 Train Models", type="primary"):
        try:
            with st.spinner("Training models..."):
                # Prepare data
                X = df[selected_features]
                y = df[target_col]
                
                # Initialize ML models
                ml_models = MLModels()
                
                # Neural network parameters
                nn_params = {
                    'hidden_layers': hidden_layers if "Neural Network" in models_to_train else 2,
                    'neurons_per_layer': neurons_per_layer if "Neural Network" in models_to_train else 64,
                    'epochs': epochs if "Neural Network" in models_to_train else 100
                }
                
                # Train models
                results = ml_models.train_models(X, y, models_to_train, test_size, random_state, nn_params)
                
                # Store results
                st.session_state.models = ml_models
                st.session_state.trained_models = results
                
                # Save model results to database
                if db and st.session_state.current_data_record_id:
                    try:
                        db.save_model_results(
                            results, 
                            st.session_state.session_id, 
                            st.session_state.current_data_record_id
                        )
                        st.success("✅ Models trained successfully and saved to database!")
                    except Exception as e:
                        st.warning(f"Models trained but database save failed: {str(e)}")
                        st.success("✅ Models trained successfully!")
                else:
                    st.success("✅ Models trained successfully!")
                
                # Display results
                st.subheader("📊 Training Results")
                
                results_df = pd.DataFrame({
                    'Model': list(results.keys()),
                    'R² Score': [results[model]['r2_score'] for model in results.keys()],
                    'RMSE': [results[model]['rmse'] for model in results.keys()],
                    'MAE': [results[model]['mae'] for model in results.keys()]
                })
                
                st.dataframe(results_df, use_container_width=True)
                
                # Plot model comparison
                fig = px.bar(results_df, x='Model', y='R² Score', title="Model Performance Comparison (R² Score)")
                st.plotly_chart(fig, use_container_width=True)
                
                # Feature importance (for tree-based models)
                if "Random Forest" in results or "Gradient Boosting" in results:
                    st.subheader("🎯 Feature Importance")
                    
                    for model_name in ["Random Forest", "Gradient Boosting"]:
                        if model_name in results and hasattr(results[model_name]['model'], 'feature_importances_'):
                            importance_df = pd.DataFrame({
                                'Feature': selected_features,
                                'Importance': results[model_name]['model'].feature_importances_
                            }).sort_values('Importance', ascending=False)
                            
                            fig_imp = px.bar(importance_df, x='Importance', y='Feature', 
                                           title=f"Feature Importance - {model_name}", orientation='h')
                            st.plotly_chart(fig_imp, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error training models: {str(e)}")

def prediction_page():
    st.header("🔮 Energy Consumption Prediction & Range Estimation")
    
    if st.session_state.trained_models is None or len(st.session_state.trained_models) == 0:
        st.warning("⚠️ Please train models first in the 'Model Training' page.")
        return
    
    # Model selection for prediction
    available_models = list(st.session_state.trained_models.keys())
    selected_model = st.selectbox("Select Model for Prediction", available_models)
    
    # Input method selection
    input_method = st.radio("Input Method", ["Manual Input", "Batch Prediction"])
    
    if input_method == "Manual Input":
        manual_prediction_interface(selected_model)
    else:
        batch_prediction_interface(selected_model)

def manual_prediction_interface(selected_model):
    st.subheader("🎛️ Manual Input for Prediction")
    
    # Get feature names from the trained model
    model_info = st.session_state.trained_models[selected_model]
    feature_names = model_info['feature_names']
    
    # Create input widgets for each feature
    col1, col2 = st.columns(2)
    input_values = {}
    
    for i, feature in enumerate(feature_names):
        with col1 if i % 2 == 0 else col2:
            if feature == 'speed':
                input_values[feature] = st.slider(f"{feature} (km/h)", 0, 200, 50)
            elif feature == 'acceleration':
                input_values[feature] = st.slider(f"{feature} (m/s²)", -5.0, 5.0, 0.0, 0.1)
            elif feature == 'road_slope':
                input_values[feature] = st.slider(f"{feature} (°)", -10.0, 10.0, 0.0, 0.5)
            elif feature == 'temperature':
                input_values[feature] = st.slider(f"{feature} (°C)", -20, 50, 20)
            else:
                # Default numeric input for other features
                input_values[feature] = st.number_input(f"{feature}", value=0.0)
    
    # Prediction button
    if st.button("🔮 Predict Energy Consumption", type="primary"):
        try:
            # Prepare input data
            input_df = pd.DataFrame([input_values])
            
            # Make prediction
            ml_models = st.session_state.models
            prediction = ml_models.predict(selected_model, input_df)
            
            # Log prediction to database
            if db:
                try:
                    db.log_prediction(
                        st.session_state.session_id,
                        selected_model,
                        input_values,
                        prediction[0]
                    )
                except Exception as e:
                    pass  # Silently continue if logging fails
            
            # Display prediction
            st.success(f"Predicted Energy Consumption: **{prediction[0]:.2f} kWh/100km**")
            
            # Range estimation
            st.subheader("🔋 Range Estimation")
            
            col1, col2 = st.columns(2)
            with col1:
                battery_capacity = st.number_input("Battery Capacity (kWh)", 10.0, 200.0, 60.0, 1.0)
            with col2:
                current_soc = st.slider("Current State of Charge (%)", 0, 100, 80)
            
            # Calculate range
            energy_calc = EnergyCalculator()
            estimated_range = energy_calc.calculate_range(
                prediction[0], battery_capacity, current_soc
            )
            
            st.metric("Estimated Range", f"{estimated_range:.1f} km")
            
            # Range visualization
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = estimated_range,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Estimated Range (km)"},
                delta = {'reference': 300},
                gauge = {
                    'axis': {'range': [None, 600]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 150], 'color': "lightgray"},
                        {'range': [150, 300], 'color': "yellow"},
                        {'range': [300, 600], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 100
                    }
                }
            ))
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error making prediction: {str(e)}")

def batch_prediction_interface(selected_model):
    st.subheader("📊 Batch Prediction")
    
    uploaded_file = st.file_uploader(
        "Upload data for batch prediction (CSV or Excel)",
        type=['csv', 'xlsx', 'xls'],
        key="batch_prediction"
    )
    
    if uploaded_file is not None:
        try:
            # Load data
            data_processor = DataProcessor()
            df = data_processor.load_data(uploaded_file)
            
            st.success(f"✅ Data loaded successfully! Shape: {df.shape}")
            
            # Make predictions
            ml_models = st.session_state.models
            predictions = ml_models.predict(selected_model, df)
            
            # Add predictions to dataframe
            df['predicted_energy_consumption'] = predictions
            
            # Display results
            st.subheader("📈 Prediction Results")
            st.dataframe(df, use_container_width=True)
            
            # Download results
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="predictions.csv">Download Predictions CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
            
            # Visualize predictions
            fig = px.histogram(df, x='predicted_energy_consumption', 
                             title="Distribution of Predicted Energy Consumption")
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error processing batch prediction: {str(e)}")

def model_comparison_page():
    st.header("📊 Model Comparison & Analysis")
    
    if st.session_state.trained_models is None or len(st.session_state.trained_models) == 0:
        st.warning("⚠️ Please train models first in the 'Model Training' page.")
        return
    
    results = st.session_state.trained_models
    
    # Performance metrics comparison
    st.subheader("📈 Performance Metrics Comparison")
    
    metrics_df = pd.DataFrame({
        'Model': list(results.keys()),
        'R² Score': [results[model]['r2_score'] for model in results.keys()],
        'RMSE': [results[model]['rmse'] for model in results.keys()],
        'MAE': [results[model]['mae'] for model in results.keys()],
        'Training Time (s)': [results[model].get('training_time', 0) for model in results.keys()]
    })
    
    st.dataframe(metrics_df, use_container_width=True)
    
    # Visual comparison
    col1, col2 = st.columns(2)
    
    with col1:
        fig_r2 = px.bar(metrics_df, x='Model', y='R² Score', title="R² Score Comparison")
        st.plotly_chart(fig_r2, use_container_width=True)
    
    with col2:
        fig_rmse = px.bar(metrics_df, x='Model', y='RMSE', title="RMSE Comparison")
        st.plotly_chart(fig_rmse, use_container_width=True)
    
    # Prediction vs Actual scatter plots
    st.subheader("🎯 Prediction vs Actual Analysis")
    
    selected_models = st.multiselect(
        "Select models to compare",
        list(results.keys()),
        default=list(results.keys())[:3]
    )
    
    if selected_models:
        fig = make_subplots(
            rows=1, cols=len(selected_models),
            subplot_titles=selected_models,
            shared_yaxes=True
        )
        
        for i, model_name in enumerate(selected_models):
            model_data = results[model_name]
            y_true = model_data['y_test']
            y_pred = model_data['y_pred']
            
            fig.add_trace(
                go.Scatter(
                    x=y_true,
                    y=y_pred,
                    mode='markers',
                    name=model_name,
                    opacity=0.6
                ),
                row=1, col=i+1
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
                    line=dict(color='red', dash='dash'),
                    showlegend=(i == 0)
                ),
                row=1, col=i+1
            )
        
        fig.update_layout(
            title="Predicted vs Actual Values",
            height=400
        )
        
        fig.update_xaxes(title_text="Actual Values")
        fig.update_yaxes(title_text="Predicted Values", col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Model rankings
    st.subheader("🏆 Model Rankings")
    
    # Rank by different metrics
    ranking_metric = st.selectbox("Rank by metric", ["R² Score", "RMSE", "MAE"])
    
    if ranking_metric == "R² Score":
        ranked_df = metrics_df.sort_values("R² Score", ascending=False)
    else:
        ranked_df = metrics_df.sort_values(ranking_metric, ascending=True)
    
    ranked_df['Rank'] = range(1, len(ranked_df) + 1)
    
    st.dataframe(ranked_df[['Rank', 'Model', ranking_metric]], use_container_width=True)

def realtime_calculator_page():
    st.header("⚡ Real-time Energy Consumption Calculator")
    
    # Vehicle parameters
    st.subheader("🚗 Vehicle Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        vehicle_mass = st.number_input("Vehicle Mass (kg)", 500, 3000, 1500)
        frontal_area = st.number_input("Frontal Area (m²)", 1.0, 5.0, 2.3, 0.1)
    
    with col2:
        drag_coefficient = st.number_input("Drag Coefficient", 0.1, 0.8, 0.29, 0.01)
        rolling_resistance = st.number_input("Rolling Resistance", 0.005, 0.02, 0.01, 0.001)
    
    with col3:
        motor_efficiency = st.slider("Motor Efficiency (%)", 70, 98, 90)
        regenerative_efficiency = st.slider("Regenerative Braking Efficiency (%)", 0, 90, 70)
    
    # Environmental conditions
    st.subheader("🌡️ Environmental Conditions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temperature = st.slider("Temperature (°C)", -20, 50, 20)
        air_density = st.number_input("Air Density (kg/m³)", 1.0, 1.4, 1.225, 0.001)
    
    with col2:
        road_slope = st.slider("Road Slope (°)", -10, 10, 0)
        wind_speed = st.slider("Wind Speed (km/h)", 0, 50, 0)
    
    with col3:
        auxiliary_power = st.slider("Auxiliary Power (kW)", 0.0, 5.0, 1.0, 0.1)
    
    # Driving parameters
    st.subheader("🛣️ Driving Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        speed = st.slider("Speed (km/h)", 0, 200, 50)
        acceleration = st.slider("Acceleration (m/s²)", -5.0, 5.0, 0.0, 0.1)
    
    with col2:
        trip_distance = st.number_input("Trip Distance (km)", 1, 1000, 100)
    
    # Calculate energy consumption
    energy_calc = EnergyCalculator()
    
    consumption = energy_calc.calculate_energy_consumption(
        speed=speed,
        acceleration=acceleration,
        road_slope=road_slope,
        temperature=temperature,
        vehicle_mass=vehicle_mass,
        frontal_area=frontal_area,
        drag_coefficient=drag_coefficient,
        rolling_resistance=rolling_resistance,
        motor_efficiency=motor_efficiency/100,
        auxiliary_power=auxiliary_power,
        air_density=air_density
    )
    
    # Display results
    st.subheader("📊 Energy Consumption Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Energy Consumption", f"{consumption:.2f} kWh/100km")
    
    with col2:
        total_energy = (consumption / 100) * trip_distance
        st.metric("Total Energy for Trip", f"{total_energy:.2f} kWh")
    
    with col3:
        # Estimate cost (assuming 0.15 €/kWh)
        cost = total_energy * 0.15
        st.metric("Estimated Cost", f"€{cost:.2f}")
    
    with col4:
        # CO2 equivalent (assuming 0.4 kg CO2/kWh)
        co2 = total_energy * 0.4
        st.metric("CO2 Equivalent", f"{co2:.2f} kg")
    
    # Energy breakdown visualization
    st.subheader("⚡ Energy Consumption Breakdown")
    
    # Calculate component energy consumption
    energy_components = energy_calc.get_energy_breakdown(
        speed=speed,
        acceleration=acceleration,
        road_slope=road_slope,
        vehicle_mass=vehicle_mass,
        frontal_area=frontal_area,
        drag_coefficient=drag_coefficient,
        rolling_resistance=rolling_resistance,
        auxiliary_power=auxiliary_power,
        air_density=air_density
    )
    
    fig_pie = px.pie(
        values=list(energy_components.values()),
        names=list(energy_components.keys()),
        title="Energy Consumption Breakdown"
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Range estimation
    st.subheader("🔋 Range Estimation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        battery_capacity = st.number_input("Battery Capacity (kWh)", 10.0, 200.0, 60.0, 1.0)
        current_soc = st.slider("Current State of Charge (%)", 0, 100, 80)
    
    estimated_range = energy_calc.calculate_range(consumption, battery_capacity, current_soc)
    
    with col2:
        st.metric("Estimated Range", f"{estimated_range:.1f} km")
    
    # Speed vs Energy Consumption curve
    st.subheader("📈 Speed vs Energy Consumption Analysis")
    
    speeds = np.arange(10, 201, 10)
    consumptions = []
    
    for spd in speeds:
        cons = energy_calc.calculate_energy_consumption(
            speed=spd,
            acceleration=0,  # Constant speed
            road_slope=road_slope,
            temperature=temperature,
            vehicle_mass=vehicle_mass,
            frontal_area=frontal_area,
            drag_coefficient=drag_coefficient,
            rolling_resistance=rolling_resistance,
            motor_efficiency=motor_efficiency/100,
            auxiliary_power=auxiliary_power,
            air_density=air_density
        )
        consumptions.append(cons)
    
    fig_speed = px.line(
        x=speeds,
        y=consumptions,
        title="Energy Consumption vs Speed",
        labels={'x': 'Speed (km/h)', 'y': 'Energy Consumption (kWh/100km)'}
    )
    
    # Add current speed point
    fig_speed.add_scatter(
        x=[speed],
        y=[consumption],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='Current Speed'
    )
    
    st.plotly_chart(fig_speed, use_container_width=True)

def route_visualization_page():
    st.header("🗺️ Route Visualization")
    st.markdown("*Interactive map visualization of EV routes and energy consumption*")
    
    if st.session_state.data is None:
        st.warning("Please upload data first in the 'Data Upload & Overview' page.")
        
        # Offer to generate sample GPS data for demonstration
        st.subheader("🧪 Generate Sample GPS Route")
        st.info("Generate sample GPS data with route visualization for demonstration purposes.")
        
        col1, col2 = st.columns(2)
        with col1:
            n_points = st.slider("Number of GPS Points", 50, 500, 200)
        with col2:
            city_choice = st.selectbox("Demo Location", ["London", "New York", "Tokyo", "Berlin"])
        
        city_coords = {
            "London": [51.5074, -0.1278],
            "New York": [40.7128, -74.0060],
            "Tokyo": [35.6762, 139.6503],
            "Berlin": [52.5200, 13.4050]
        }
        
        if st.button("Generate Sample Route"):
            map_viz = MapVisualizer()
            center_lat, center_lon = city_coords[city_choice]
            sample_data = map_viz.generate_sample_gps_data(
                n_points=n_points,
                center_lat=center_lat,
                center_lon=center_lon
            )
            st.session_state.data = sample_data
            st.success(f"Generated {n_points} GPS points for {city_choice}")
            st.rerun()
        return
    
    df = st.session_state.data
    map_viz = MapVisualizer()
    
    # Check for GPS columns
    lat_cols = [col for col in df.columns if 'lat' in col.lower()]
    lon_cols = [col for col in df.columns if 'lon' in col.lower()]
    
    if not lat_cols or not lon_cols:
        st.error("No GPS coordinates found in data. Upload data with latitude/longitude columns.")
        return
    
    # Column selection
    st.subheader("🎯 Map Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lat_col = st.selectbox("Latitude Column", lat_cols)
    with col2:
        lon_col = st.selectbox("Longitude Column", lon_cols)
    with col3:
        energy_col = st.selectbox("Energy Column", 
                                [col for col in df.columns if 'energy' in col.lower() or 'consumption' in col.lower()],
                                index=0 if any('energy' in col.lower() for col in df.columns) else None)
    
    # Map visualization options
    st.subheader("🗺️ Visualization Options")
    col1, col2 = st.columns(2)
    
    with col1:
        show_route = st.checkbox("Show Route Line", value=True)
        show_markers = st.checkbox("Show Data Points", value=False)
    with col2:
        show_charging = st.checkbox("Show Charging Stations", value=True)
        color_by_energy = st.checkbox("Color by Energy Consumption", value=True)
    
    # Create map
    if lat_col and lon_col:
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = map_viz.create_base_map(center_lat, center_lon, zoom_start=12)
        
        # Add route if requested
        if show_route:
            if color_by_energy and energy_col:
                m = map_viz.add_route_from_coordinates(m, df, lat_col, lon_col, energy_col)
            else:
                m = map_viz.add_route_from_coordinates(m, df, lat_col, lon_col)
        
        # Add markers if requested
        if show_markers:
            popup_cols = [energy_col] if energy_col else ['speed']
            if 'speed' in df.columns:
                popup_cols.append('speed')
            m = map_viz.add_markers_with_data(m, df, lat_col, lon_col, popup_cols)
        
        # Add charging stations if requested
        if show_charging:
            m = map_viz.add_charging_stations(m)
        
        # Display map
        st.subheader("🗺️ Interactive Route Map")
        map_data = st_folium(m, width=700, height=500)
        
        # Route statistics
        st.subheader("📊 Route Statistics")
        stats = map_viz.calculate_route_statistics(df, lat_col, lon_col, energy_col)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if 'total_distance_km' in stats:
                st.metric("Total Distance", f"{stats['total_distance_km']:.1f} km")
        with col2:
            if 'avg_energy_consumption' in stats:
                st.metric("Avg Energy", f"{stats['avg_energy_consumption']:.1f} kWh/100km")
        with col3:
            if 'total_energy_used_kwh' in stats:
                st.metric("Total Energy", f"{stats['total_energy_used_kwh']:.1f} kWh")
        with col4:
            if 'avg_speed_kmh' in stats:
                st.metric("Avg Speed", f"{stats['avg_speed_kmh']:.1f} km/h")

def energy_heatmaps_page():
    st.header("🔥 Energy Consumption Heatmaps")
    st.markdown("*Spatial analysis of energy consumption patterns*")
    
    if st.session_state.data is None:
        st.warning("Please upload data first or generate sample data in Route Visualization.")
        return
    
    df = st.session_state.data
    map_viz = MapVisualizer()
    
    # Check for required columns
    lat_cols = [col for col in df.columns if 'lat' in col.lower()]
    lon_cols = [col for col in df.columns if 'lon' in col.lower()]
    energy_cols = [col for col in df.columns if 'energy' in col.lower() or 'consumption' in col.lower()]
    
    if not lat_cols or not lon_cols or not energy_cols:
        st.error("GPS coordinates and energy consumption data required for heatmap visualization.")
        return
    
    # Column selection
    st.subheader("🎯 Heatmap Configuration")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        lat_col = st.selectbox("Latitude Column", lat_cols)
    with col2:
        lon_col = st.selectbox("Longitude Column", lon_cols)
    with col3:
        energy_col = st.selectbox("Energy Column", energy_cols)
    
    # Heatmap options
    st.subheader("🔥 Heatmap Options")
    col1, col2 = st.columns(2)
    
    with col1:
        show_route_overlay = st.checkbox("Show Route Overlay", value=True)
        show_high_consumption = st.checkbox("Highlight High Consumption Areas", value=True)
    with col2:
        min_intensity = st.slider("Minimum Intensity", 0.1, 1.0, 0.4, 0.1)
        blur_radius = st.slider("Blur Radius", 5, 30, 15)
    
    if lat_col and lon_col and energy_col:
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = map_viz.create_base_map(center_lat, center_lon, zoom_start=12)
        
        # Add energy heatmap
        m = map_viz.create_energy_heatmap(m, df, lat_col, lon_col, energy_col)
        
        # Add route overlay if requested
        if show_route_overlay:
            m = map_viz.add_route_from_coordinates(m, df, lat_col, lon_col)
        
        # Display heatmap
        st.subheader("🔥 Energy Consumption Heatmap")
        map_data = st_folium(m, width=700, height=500)
        
        # Energy analysis
        st.subheader("📊 Energy Consumption Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Energy distribution
            fig_hist = px.histogram(df, x=energy_col, nbins=30, 
                                  title="Energy Consumption Distribution")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # High consumption areas
            if show_high_consumption:
                high_consumption_threshold = df[energy_col].quantile(0.8)
                high_consumption_df = df[df[energy_col] > high_consumption_threshold]
                
                st.metric("High Consumption Threshold", f"{high_consumption_threshold:.1f} kWh/100km")
                st.metric("High Consumption Points", f"{len(high_consumption_df)} / {len(df)}")
                
                if len(high_consumption_df) > 0:
                    avg_high = high_consumption_df[energy_col].mean()
                    st.metric("Avg High Consumption", f"{avg_high:.1f} kWh/100km")

def gps_tracking_page():
    st.header("📍 GPS Tracking Analysis")
    st.markdown("*Detailed analysis of GPS tracking data and driving patterns*")
    
    if st.session_state.data is None:
        st.warning("Please upload data first or generate sample data in Route Visualization.")
        return
    
    df = st.session_state.data
    
    # Check for required columns
    lat_cols = [col for col in df.columns if 'lat' in col.lower()]
    lon_cols = [col for col in df.columns if 'lon' in col.lower()]
    time_cols = [col for col in df.columns if 'time' in col.lower() or 'timestamp' in col.lower()]
    
    if not lat_cols or not lon_cols:
        st.error("GPS coordinates required for tracking analysis.")
        return
    
    lat_col = lat_cols[0]
    lon_col = lon_cols[0]
    time_col = time_cols[0] if time_cols else None
    
    st.subheader("📊 GPS Data Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total GPS Points", len(df))
    with col2:
        if time_col:
            duration = (pd.to_datetime(df[time_col]).max() - pd.to_datetime(df[time_col]).min())
            st.metric("Duration", f"{duration.total_seconds()/3600:.1f} hours")
    with col3:
        lat_range = df[lat_col].max() - df[lat_col].min()
        st.metric("Latitude Range", f"{lat_range:.4f}°")
    with col4:
        lon_range = df[lon_col].max() - df[lon_col].min()
        st.metric("Longitude Range", f"{lon_range:.4f}°")
    
    # Time-based analysis
    if time_col:
        st.subheader("⏰ Time-based Analysis")
        
        # Convert time column
        df_time = df.copy()
        df_time[time_col] = pd.to_datetime(df_time[time_col])
        df_time['hour'] = df_time[time_col].dt.hour
        df_time['day_of_week'] = df_time[time_col].dt.day_name()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Hourly distribution
            hourly_counts = df_time['hour'].value_counts().sort_index()
            fig_hourly = px.bar(x=hourly_counts.index, y=hourly_counts.values,
                               title="GPS Points by Hour of Day",
                               labels={'x': 'Hour', 'y': 'Number of Points'})
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        with col2:
            # Daily distribution
            daily_counts = df_time['day_of_week'].value_counts()
            fig_daily = px.pie(values=daily_counts.values, names=daily_counts.index,
                              title="GPS Points by Day of Week")
            st.plotly_chart(fig_daily, use_container_width=True)
    
    # Speed analysis (if available)
    if 'speed' in df.columns:
        st.subheader("🚗 Speed Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Speed over time
            if time_col:
                fig_speed_time = px.line(df, x=time_col, y='speed',
                                       title="Speed Over Time")
                st.plotly_chart(fig_speed_time, use_container_width=True)
        
        with col2:
            # Speed distribution
            fig_speed_dist = px.histogram(df, x='speed', nbins=30,
                                        title="Speed Distribution")
            st.plotly_chart(fig_speed_dist, use_container_width=True)
    
    # Interactive map with time controls
    st.subheader("🗺️ Interactive GPS Tracking Map")
    
    map_viz = MapVisualizer()
    center_lat = df[lat_col].mean()
    center_lon = df[lon_col].mean()
    
    m = map_viz.create_base_map(center_lat, center_lon, zoom_start=12)
    
    # Add full route
    m = map_viz.add_route_from_coordinates(m, df, lat_col, lon_col)
    
    # Sample points for markers (to avoid overcrowding)
    sample_size = min(50, len(df))
    df_sample = df.sample(n=sample_size) if len(df) > sample_size else df
    
    popup_cols = ['speed'] if 'speed' in df.columns else []
    if 'energy_consumption' in df.columns:
        popup_cols.append('energy_consumption')
    
    m = map_viz.add_markers_with_data(m, df_sample, lat_col, lon_col, popup_cols)
    
    map_data = st_folium(m, width=700, height=500)

def dashboard_overview_page():
    st.header("🏠 Welcome to the EV Energy Dashboard")
    st.markdown("*Your complete solution for electric vehicle energy analysis and cost optimization*")
    
    # Quick action cards for new users
    st.subheader("🚀 Get Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("### 📤 1. Upload Your Data")
            st.markdown("Start by uploading your EV data (CSV/Excel) or generate sample data for testing.")
            if st.button("Go to Upload Data", key="nav_upload"):
                st.session_state.page = "📤 Upload Data"
                st.rerun()
    
    with col2:
        with st.container():
            st.markdown("### 💰 2. Check Cost Savings")
            st.markdown("See how much you can save with EVs vs petrol/diesel in Nepal (NPR).")
            if st.button("View Cost Analysis", key="nav_cost"):
                st.session_state.page = "💰 Cost Analysis (Nepal)"
                st.rerun()
    
    with col3:
        with st.container():
            st.markdown("### 🗺️ 3. Visualize Routes")
            st.markdown("Map your routes and analyze energy consumption patterns.")
            if st.button("Explore Maps", key="nav_maps"):
                st.session_state.page = "🗺️ Route Maps"
                st.rerun()
    
    st.markdown("---")
    
    # Dashboard introduction
    st.subheader("🔋 About This Dashboard")
    st.markdown("""
    Analyze electric vehicle energy consumption and make data-driven decisions about EV adoption. 
    The dashboard combines machine learning with physics-based calculations to provide accurate 
    insights for the Nepali market.
    """)
    
    # Feature overview
    st.subheader("🚀 Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Data & Analysis**
        - CSV/Excel data upload with validation
        - Comprehensive data exploration tools
        - Real-time energy consumption calculator
        - Sample data generation for testing
        
        **🤖 Machine Learning & Predictions**
        - Multiple ML models (Linear, RF, NN, SVR, GB)
        - Model training with hyperparameter tuning
        - Prediction interface with range estimation
        - Model performance comparison
        """)
    
    with col2:
        st.markdown("""
        **🗺️ Maps & Routes**
        - Interactive route visualization
        - Energy consumption heatmaps
        - GPS tracking analysis
        - Charging station locations
        
        **📚 Help & Tools**
        - Comprehensive documentation
        - Physics equations and formulas
        - Model explanations and limitations
        - Usage guidelines and best practices
        """)
    
    # Quick start guide
    st.subheader("🎯 Quick Start Guide")
    
    with st.expander("1. Data Upload & Preparation", expanded=True):
        st.markdown("""
        - Navigate to **Data & Analysis → Data Upload & Overview**
        - Upload CSV/Excel file with EV data or generate sample data
        - Required columns: speed, acceleration, energy_consumption
        - Optional: GPS coordinates, temperature, time stamps
        """)
    
    with st.expander("2. Data Exploration"):
        st.markdown("""
        - Go to **Data & Analysis → Data Exploration**
        - Review correlation matrices and feature distributions
        - Analyze relationships between variables
        - Identify patterns and outliers in your data
        """)
    
    with st.expander("3. Model Training"):
        st.markdown("""
        - Access **ML & Predictions → Model Training**
        - Select features and target variable
        - Choose models and configure parameters
        - Train multiple models simultaneously
        """)
    
    with st.expander("4. Predictions & Analysis"):
        st.markdown("""
        - Use **ML & Predictions → Prediction & Range Estimation**
        - Make single predictions or batch processing
        - Get range estimates with battery parameters
        - Compare model performance metrics
        """)
    
    with st.expander("5. Map Visualization"):
        st.markdown("""
        - Explore **Maps & Routes** section
        - Visualize routes with energy consumption overlay
        - Analyze spatial patterns with heatmaps
        - Track GPS data and driving patterns
        """)
    
    # System status
    st.subheader("🔧 System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Data status
        if st.session_state.data is not None:
            st.success("✅ Data Loaded")
            st.caption(f"Shape: {st.session_state.data.shape}")
        else:
            st.info("📤 No Data Loaded")
    
    with col2:
        # Models status
        if st.session_state.trained_models:
            st.success("✅ Models Trained")
            st.caption(f"Models: {len(st.session_state.trained_models)}")
        else:
            st.info("🤖 No Models Trained")
    
    with col3:
        # Database status
        if db:
            st.success("✅ Database Connected")
        else:
            st.error("❌ Database Unavailable")
    
    # Recent activity
    if db:
        st.subheader("📈 Recent Activity")
        try:
            stats = db.get_data_statistics()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Datasets", stats.get('total_datasets', 0))
            with col2:
                st.metric("Total Predictions", stats.get('total_predictions', 0))
            with col3:
                st.metric("Data Points", stats.get('total_data_points', 0))
            
        except Exception as e:
            st.error("Unable to load database statistics")
    
    # Tips and recommendations
    st.subheader("💡 Tips & Recommendations")
    
    st.markdown("""
    **For Best Results:**
    - Use datasets with at least 500 data points
    - Include diverse driving conditions (city, highway, different weather)
    - Validate GPS coordinates are accurate
    - Check for data quality issues before training
    - Use cross-validation for model selection
    - Monitor prediction accuracy over time
    
    **Performance Optimization:**
    - Sample large datasets for map visualization
    - Use appropriate zoom levels for map displays
    - Cache model results for repeated use
    - Regular database cleanup for large deployments
    """)

def help_documentation_page():
    st.header("📚 Help & Documentation")
    st.markdown("*Comprehensive guide to formulas, models, and processes used in the EV Energy Dashboard*")
    
    # Table of Contents
    st.subheader("📋 Table of Contents")
    st.markdown("""
    1. [Physics-Based Energy Consumption Model](#physics-based-energy-consumption-model)
    2. [Machine Learning Models](#machine-learning-models)
    3. [Data Processing Pipeline](#data-processing-pipeline)
    4. [Range Estimation Methods](#range-estimation-methods)
    5. [Database Schema](#database-schema)
    6. [References](#references)
    """)
    
    # Physics-Based Energy Consumption Model
    st.subheader("⚡ Physics-Based Energy Consumption Model")
    st.markdown("*Based on BMW i3 case study methodology from Miri et al. (2020)*")
    
    with st.expander("🔬 Fundamental Physics Equations", expanded=False):
        st.markdown("""
        **Total Energy Consumption Formula:**
        ```
        E_total = (P_mechanical + P_auxiliary + P_temperature) / η_system
        ```
        
        **Forces Acting on Vehicle:**
        
        1. **Aerodynamic Drag Force:**
        ```
        F_aero = 0.5 × ρ_air × A_front × C_d × v²
        ```
        - ρ_air: Air density (1.225 kg/m³ at sea level)
        - A_front: Frontal area (2.38 m² for BMW i3)
        - C_d: Drag coefficient (0.29 for BMW i3)
        - v: Vehicle speed (m/s)
        
        2. **Rolling Resistance Force:**
        ```
        F_rolling = C_r × m × g × cos(θ)
        ```
        - C_r: Rolling resistance coefficient (0.01)
        - m: Vehicle mass (1195 kg for BMW i3)
        - g: Gravitational acceleration (9.81 m/s²)
        - θ: Road slope angle (radians)
        
        3. **Gravitational Force (Road Slope):**
        ```
        F_gravity = m × g × sin(θ)
        ```
        
        4. **Inertial Force (Acceleration/Deceleration):**
        ```
        F_inertial = m × a
        ```
        - a: Vehicle acceleration (m/s²)
        
        **Total Tractive Force:**
        ```
        F_total = F_aero + F_rolling + F_gravity + F_inertial
        ```
        
        **Mechanical Power at Wheels:**
        ```
        P_mechanical = F_total × v / 1000  (kW)
        ```
        
        **System Efficiencies:**
        - Motor efficiency (η_motor): 90%
        - Transmission efficiency (η_trans): 95%
        - Battery efficiency (η_battery): 95%
        - Regenerative braking efficiency: 70%
        """)
    
    with st.expander("🌡️ Temperature Effects on Energy Consumption", expanded=False):
        st.markdown("""
        **HVAC Power Consumption:**
        
        The heating, ventilation, and air conditioning (HVAC) system power consumption varies with ambient temperature:
        
        ```
        P_hvac = |T_ambient - T_optimal| × k_hvac
        ```
        
        Where:
        - T_optimal = 22°C (minimal HVAC usage)
        - k_hvac = 0.15 kW/°C for heating (T < 22°C)
        - k_hvac = 0.12 kW/°C for cooling (T > 22°C)
        - Maximum HVAC power capped at 5 kW
        
        **Total Auxiliary Power:**
        ```
        P_auxiliary = P_base + P_hvac
        ```
        - P_base: Base auxiliary power (1.0 kW for electronics, lights, etc.)
        """)
    
    with st.expander("🔋 Energy Consumption Calculation", expanded=False):
        st.markdown("""
        **Final Energy Consumption (kWh/100km):**
        
        ```
        E_consumption = (P_total × 100) / v_kmh
        ```
        
        Where:
        ```
        P_total = (P_mechanical / η_motor / η_trans) + P_auxiliary + P_hvac
        ```
        
        **With Battery Efficiency:**
        ```
        E_final = E_consumption / η_battery
        ```
        
        **Range Calculation:**
        ```
        Range = (E_available / E_consumption) × 100
        ```
        
        Where:
        ```
        E_available = Battery_capacity × (SOC_current / 100)
        ```
        """)
    
    # Machine Learning Models
    st.subheader("🤖 Machine Learning Models")
    
    with st.expander("📊 Model Descriptions and Applications", expanded=False):
        st.markdown("""
        **1. Linear Regression**
        ```
        y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε
        ```
        - **Use case:** Baseline model for understanding linear relationships
        - **Advantages:** Interpretable coefficients, fast training
        - **Limitations:** Assumes linear relationships
        
        **2. Random Forest Regressor**
        ```
        ŷ = (1/B) × Σ(Tree_b(x))
        ```
        - **Use case:** Capturing non-linear relationships and feature interactions
        - **Advantages:** Handles non-linearity, provides feature importance
        - **Parameters:** 100 estimators, max_depth=10
        
        **3. Neural Network (MLP Regressor)**
        ```
        h₁ = σ(W₁x + b₁)
        h₂ = σ(W₂h₁ + b₂)
        y = W₃h₂ + b₃
        ```
        - **Use case:** Complex pattern recognition in energy consumption
        - **Architecture:** Configurable hidden layers (1-3), neurons per layer (10-200)
        - **Activation:** ReLU for hidden layers, linear for output
        
        **4. Support Vector Regression (SVR)**
        ```
        f(x) = Σ(αᵢ - αᵢ*)K(xᵢ, x) + b
        ```
        - **Use case:** Robust prediction with RBF kernel
        - **Kernel:** Radial Basis Function (RBF)
        - **Advantages:** Effective in high-dimensional spaces
        
        **5. Gradient Boosting Regressor**
        ```
        F_m(x) = F_{m-1}(x) + γ_m × h_m(x)
        ```
        - **Use case:** Sequential improvement of predictions
        - **Parameters:** 100 estimators, learning_rate=0.1, max_depth=6
        """)
    
    with st.expander("📈 Model Evaluation Metrics", expanded=False):
        st.markdown("""
        **R² Score (Coefficient of Determination):**
        ```
        R² = 1 - (SS_res / SS_tot)
        ```
        Where:
        - SS_res = Σ(yᵢ - ŷᵢ)² (Sum of squares of residuals)
        - SS_tot = Σ(yᵢ - ȳ)² (Total sum of squares)
        
        **Root Mean Square Error (RMSE):**
        ```
        RMSE = √[(1/n) × Σ(yᵢ - ŷᵢ)²]
        ```
        
        **Mean Absolute Error (MAE):**
        ```
        MAE = (1/n) × Σ|yᵢ - ŷᵢ|
        ```
        
        **Interpretation:**
        - R² closer to 1.0 indicates better model fit
        - Lower RMSE and MAE indicate better prediction accuracy
        - RMSE penalizes larger errors more than MAE
        """)
    
    # Data Processing Pipeline
    st.subheader("🔧 Data Processing Pipeline")
    
    with st.expander("📋 Data Validation and Cleaning", expanded=False):
        st.markdown("""
        **Required Data Columns:**
        - `speed` (km/h): Vehicle speed
        - `acceleration` (m/s²): Vehicle acceleration
        - `energy_consumption` (kWh/100km): Target variable
        
        **Optional Columns:**
        - `road_slope` (degrees): Road gradient
        - `temperature` (°C): Ambient temperature
        - `auxiliary_power` (kW): Auxiliary device power
        - `time`, `distance`, `battery_soc`
        
        **Data Cleaning Process:**
        1. Remove completely empty rows and columns
        2. Standardize column names (lowercase, underscores)
        3. Outlier detection using IQR method:
        ```
        Q1 = 25th percentile
        Q3 = 75th percentile
        IQR = Q3 - Q1
        Lower_bound = Q1 - 1.5 × IQR
        Upper_bound = Q3 + 1.5 × IQR
        ```
        4. Cap outliers instead of removal to preserve data
        """)
    
    # Usage Guidelines
    st.subheader("📋 Usage Guidelines")
    
    with st.expander("🚀 Getting Started Guide", expanded=False):
        st.markdown("""
        **Step-by-Step Workflow:**
        
        1. **Data Upload:**
        - Use CSV/Excel files with required columns
        - Or generate sample data for testing
        - Data automatically saved to database
        
        2. **Data Exploration:**
        - Review correlation matrices
        - Analyze feature distributions
        - Identify patterns and outliers
        
        3. **Model Training:**
        - Select relevant features
        - Choose appropriate models
        - Configure hyperparameters
        - Results saved to database
        
        4. **Prediction & Range Estimation:**
        - Manual input for single predictions
        - Batch processing for multiple scenarios
        - Real-time range calculations
        
        5. **Map Visualization:**
        - Interactive route mapping
        - Energy consumption heatmaps
        - GPS tracking analysis
        """)

def cost_comparison_nepal_page():
    st.header("💰 Cost Comparison: EV vs Petrol/Diesel (Nepal)")
    st.markdown("*Complete cost analysis for electric vs conventional vehicles in Nepal*")
    
    cost_calc = CostCalculator()
    
    # Display current rates
    st.subheader("📊 Current Fuel & Electricity Rates in Nepal")
    rates_info = cost_calc.get_cost_rates_info()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Electricity Rate", f"NPR {rates_info['electricity_rate_npr_per_kwh']:.1f}/kWh")
        st.caption("Residential rate (NEA)")
    with col2:
        st.metric("Petrol Price", f"NPR {rates_info['petrol_price_npr_per_liter']:.0f}/L")
        st.caption("Current market rate")
    with col3:
        st.metric("Diesel Price", f"NPR {rates_info['diesel_price_npr_per_liter']:.0f}/L")
        st.caption("Current market rate")
    
    # Vehicle efficiency assumptions
    st.subheader("🚗 Vehicle Efficiency Assumptions")
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Petrol Vehicle:** {rates_info['petrol_efficiency_km_per_liter']:.0f} km/L")
    with col2:
        st.info(f"**Diesel Vehicle:** {rates_info['diesel_efficiency_km_per_liter']:.0f} km/L")
    
    # User inputs for comparison
    st.subheader("🎯 Configure Your Comparison")
    
    col1, col2 = st.columns(2)
    with col1:
        # Energy consumption input
        if st.session_state.data is not None and 'energy_consumption' in st.session_state.data.columns:
            avg_consumption = st.session_state.data['energy_consumption'].mean()
            st.info(f"Using average from uploaded data: {avg_consumption:.1f} kWh/100km")
            energy_consumption = st.slider("EV Energy Consumption (kWh/100km)", 
                                         5.0, 40.0, float(avg_consumption), 0.5)
        else:
            energy_consumption = st.slider("EV Energy Consumption (kWh/100km)", 
                                         5.0, 40.0, 18.0, 0.5)
        
        distance_km = st.slider("Trip Distance (km)", 10, 1000, 100, 10)
    
    with col2:
        annual_distance = st.slider("Annual Distance (km/year)", 5000, 50000, 15000, 1000)
        
        # Custom rates option
        use_custom_rates = st.checkbox("Use Custom Rates")
        if use_custom_rates:
            electricity_rate = st.number_input("Electricity Rate (NPR/kWh)", 
                                             value=rates_info['electricity_rate_npr_per_kwh'])
            petrol_price = st.number_input("Petrol Price (NPR/L)", 
                                         value=rates_info['petrol_price_npr_per_liter'])
            # Update calculator rates
            cost_calc.electricity_rate_npr = electricity_rate
            cost_calc.petrol_price_npr = petrol_price
    
    # Calculate costs
    comparison = cost_calc.compare_costs(energy_consumption, distance_km)
    annual_analysis = cost_calc.calculate_annual_savings(energy_consumption, annual_distance)
    
    # Trip cost comparison
    st.subheader("🛣️ Trip Cost Comparison")
    st.markdown(f"**Distance:** {distance_km} km | **EV Consumption:** {energy_consumption} kWh/100km")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Electric Vehicle",
            f"NPR {comparison['ev_cost']['total_cost_npr']:.2f}",
            f"NPR {comparison['ev_cost']['cost_per_km_npr']:.2f}/km"
        )
        with st.expander("EV Cost Breakdown"):
            st.write(f"Energy Required: {comparison['ev_cost']['energy_required_kwh']:.2f} kWh")
            st.write(f"Electricity Cost: NPR {comparison['ev_cost']['electricity_cost_npr']:.2f}")
            st.write(f"Charging Losses: NPR {comparison['ev_cost']['charging_losses_npr']:.2f}")
    
    with col2:
        savings_color = "normal" if comparison['petrol_savings_npr'] > 0 else "inverse"
        st.metric(
            "Petrol Vehicle",
            f"NPR {comparison['petrol_cost']['fuel_cost_npr']:.2f}",
            f"-NPR {comparison['petrol_savings_npr']:.2f} savings",
            delta_color=savings_color
        )
        with st.expander("Petrol Cost Breakdown"):
            st.write(f"Fuel Required: {comparison['petrol_cost']['fuel_required_liters']:.2f} L")
            st.write(f"Fuel Cost: NPR {comparison['petrol_cost']['fuel_cost_npr']:.2f}")
            st.write(f"Savings: {comparison['petrol_savings_percent']:.1f}%")
    
    with col3:
        diesel_savings_color = "normal" if comparison['diesel_savings_npr'] > 0 else "inverse"
        st.metric(
            "Diesel Vehicle",
            f"NPR {comparison['diesel_cost']['fuel_cost_npr']:.2f}",
            f"-NPR {comparison['diesel_savings_npr']:.2f} savings",
            delta_color=diesel_savings_color
        )
        with st.expander("Diesel Cost Breakdown"):
            st.write(f"Fuel Required: {comparison['diesel_cost']['fuel_required_liters']:.2f} L")
            st.write(f"Fuel Cost: NPR {comparison['diesel_cost']['fuel_cost_npr']:.2f}")
            st.write(f"Savings: {comparison['diesel_savings_percent']:.1f}%")
    
    # Annual cost analysis
    st.subheader("📅 Annual Cost Analysis")
    st.markdown(f"**Annual Distance:** {annual_distance:,} km")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("EV Annual Cost", f"NPR {annual_analysis['ev_annual_cost_npr']:,.0f}")
    with col2:
        st.metric("Petrol Annual Cost", f"NPR {annual_analysis['petrol_annual_cost_npr']:,.0f}")
        st.metric("Annual Savings vs Petrol", f"NPR {annual_analysis['annual_petrol_savings_npr']:,.0f}")
    with col3:
        st.metric("Diesel Annual Cost", f"NPR {annual_analysis['diesel_annual_cost_npr']:,.0f}")
        st.metric("Annual Savings vs Diesel", f"NPR {annual_analysis['annual_diesel_savings_npr']:,.0f}")
    
    # Interactive cost comparison chart
    st.subheader("📈 Interactive Cost Comparison Chart")
    fig_comparison = cost_calc.create_cost_comparison_chart(energy_consumption, max_distance=1000)
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Annual savings breakdown
    st.subheader("💹 Annual Savings Breakdown")
    fig_savings = cost_calc.create_savings_breakdown_chart(annual_analysis)
    st.plotly_chart(fig_savings, use_container_width=True)
    
    # Long-term financial impact
    st.subheader("🏦 Long-term Financial Impact")
    
    col1, col2 = st.columns(2)
    with col1:
        # 5-year analysis
        savings_5_years = annual_analysis['annual_petrol_savings_npr'] * 5
        st.metric("5-Year Savings vs Petrol", f"NPR {savings_5_years:,.0f}")
        st.caption(f"USD {savings_5_years * rates_info['npr_to_usd_rate']:,.0f}")
        
        # 10-year analysis
        savings_10_years = annual_analysis['annual_petrol_savings_npr'] * 10
        st.metric("10-Year Savings vs Petrol", f"NPR {savings_10_years:,.0f}")
        st.caption(f"USD {savings_10_years * rates_info['npr_to_usd_rate']:,.0f}")
    
    with col2:
        # Environmental impact (approximate)
        annual_fuel_consumption = annual_distance / rates_info['petrol_efficiency_km_per_liter']
        co2_emissions_kg = annual_fuel_consumption * 2.31  # kg CO2 per liter of petrol
        
        st.metric("Annual CO₂ Avoided", f"{co2_emissions_kg:,.0f} kg")
        st.caption("vs petrol vehicle")
        
        st.metric("10-Year CO₂ Avoided", f"{co2_emissions_kg * 10 / 1000:.1f} tonnes")
        st.caption("Environmental benefit")
    
    # Vehicle purchase payback analysis
    st.subheader("🚗 Vehicle Purchase Payback Analysis")
    st.markdown("*Calculate how long it takes for EV savings to offset higher purchase price*")
    
    col1, col2 = st.columns(2)
    with col1:
        ev_price = st.number_input("EV Purchase Price (NPR)", 
                                  value=4000000, step=100000, format="%d")
        st.caption("Include all costs (vehicle, registration, insurance)")
    
    with col2:
        conventional_price = st.number_input("Conventional Vehicle Price (NPR)", 
                                           value=3000000, step=100000, format="%d")
        st.caption("Equivalent conventional vehicle cost")
    
    if st.button("Calculate Payback Period"):
        payback_analysis = cost_calc.calculate_payback_period(
            ev_price, conventional_price, energy_consumption, annual_distance
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Price Difference", f"NPR {payback_analysis['price_difference_npr']:,.0f}")
        with col2:
            if payback_analysis['payback_period_years'] < 50:
                st.metric("Payback Period", f"{payback_analysis['payback_period_years']:.1f} years")
            else:
                st.metric("Payback Period", "No payback")
        with col3:
            st.metric("5-Year Net Savings", f"NPR {payback_analysis['total_5_year_savings_npr']:,.0f}")
        
        # Payback visualization
        if payback_analysis['payback_period_years'] < 20:
            years = np.arange(0, 11)
            cumulative_savings = years * payback_analysis['annual_savings_npr'] - payback_analysis['price_difference_npr']
            
            fig_payback = go.Figure()
            fig_payback.add_trace(go.Scatter(
                x=years,
                y=cumulative_savings,
                mode='lines+markers',
                name='Cumulative Savings',
                line=dict(color='green', width=3)
            ))
            
            fig_payback.add_hline(y=0, line_dash="dash", line_color="red", 
                                 annotation_text="Break-even point")
            
            fig_payback.update_layout(
                title="EV Purchase Payback Analysis",
                xaxis_title="Years",
                yaxis_title="Cumulative Savings (NPR)",
                template='plotly_white'
            )
            
            st.plotly_chart(fig_payback, use_container_width=True)
    
    # Regional comparison
    st.subheader("🌏 Regional Fuel Price Context")
    
    with st.expander("Compare with Other Countries", expanded=False):
        st.markdown("""
        **Fuel Price Comparison (approximate):**
        - **Nepal:** NPR 155/L (Petrol), NPR 140/L (Diesel)
        - **India:** NPR 120-130/L (Petrol), NPR 110-120/L (Diesel)
        - **USA:** NPR 110-120/L (Gasoline)
        - **Europe:** NPR 180-220/L (Petrol)
        
        **Electricity Rate Comparison:**
        - **Nepal:** NPR 9.5/kWh (Residential)
        - **India:** NPR 7-12/kWh
        - **USA:** NPR 12-15/kWh
        - **Europe:** NPR 20-30/kWh
        
        Nepal offers competitive electricity rates making EVs more economically attractive.
        """)
    
    # Key insights
    st.subheader("💡 Key Insights")
    
    insights = []
    if comparison['petrol_savings_npr'] > 0:
        insights.append(f"✅ EV saves NPR {comparison['petrol_savings_npr']:.2f} per {distance_km}km trip vs petrol")
    if annual_analysis['annual_petrol_savings_npr'] > 0:
        insights.append(f"✅ Annual savings of NPR {annual_analysis['annual_petrol_savings_npr']:,.0f} vs petrol vehicle")
    if energy_consumption < 20:
        insights.append("✅ Efficient EV with low energy consumption")
    else:
        insights.append("⚠️ Consider more efficient EV model for better savings")
    
    for insight in insights:
        st.markdown(insight)

if __name__ == "__main__":
    main()
