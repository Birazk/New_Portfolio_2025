import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
import io

class DataProcessor:
    """
    Data processing utilities for EV energy consumption analysis
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
    
    def load_data(self, uploaded_file):
        """
        Load data from uploaded file (CSV or Excel)
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            DataFrame: Loaded data
        """
        
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                raise ValueError("Unsupported file format. Please use CSV or Excel files.")
            
            # Basic data cleaning
            df = self.basic_cleaning(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")
    
    def basic_cleaning(self, df):
        """
        Perform basic data cleaning operations
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame: Cleaned data
        """
        
        # Remove completely empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Strip whitespace from column names
        df.columns = df.columns.str.strip()
        
        # Convert column names to lowercase and replace spaces with underscores
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Handle numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            # Remove outliers using IQR method
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers instead of removing them
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def validate_data(self, df):
        """
        Validate EV dataset for required columns and data quality
        
        Args:
            df: Input DataFrame
            
        Returns:
            dict: Validation results
        """
        
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Required columns for basic EV analysis
        recommended_columns = [
            'speed', 'acceleration', 'energy_consumption'
        ]
        
        # Check for recommended columns
        missing_columns = [col for col in recommended_columns if col not in df.columns]
        if missing_columns:
            validation_results['warnings'].append(
                f"Recommended columns missing: {missing_columns}"
            )
        
        # Check if there's at least one target column
        target_columns = [col for col in df.columns if 'energy' in col.lower() or 'consumption' in col.lower()]
        if not target_columns:
            validation_results['errors'].append(
                "No energy consumption target column found"
            )
            validation_results['is_valid'] = False
        
        # Check data types
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) < 3:
            validation_results['errors'].append(
                "Insufficient numeric columns for analysis (minimum 3 required)"
            )
            validation_results['is_valid'] = False
        
        # Check for sufficient data
        if len(df) < 50:
            validation_results['warnings'].append(
                f"Small dataset ({len(df)} rows). Consider using more data for better model performance."
            )
        
        # Check for missing values
        missing_percentage = (df.isnull().sum() / len(df)) * 100
        high_missing_cols = missing_percentage[missing_percentage > 50].index.tolist()
        if high_missing_cols:
            validation_results['warnings'].append(
                f"Columns with >50% missing values: {high_missing_cols}"
            )
        
        # Check for constant columns
        constant_cols = [col for col in numeric_columns if df[col].nunique() <= 1]
        if constant_cols:
            validation_results['warnings'].append(
                f"Constant columns detected: {constant_cols}"
            )
        
        return validation_results
    
    def handle_missing_values(self, df, strategy='mean'):
        """
        Handle missing values in the dataset
        
        Args:
            df: Input DataFrame
            strategy: Strategy for handling missing values
            
        Returns:
            DataFrame: Data with missing values handled
        """
        
        df_processed = df.copy()
        
        for column in df_processed.columns:
            if df_processed[column].dtype in ['float64', 'int64']:
                if strategy == 'mean':
                    df_processed[column].fillna(df_processed[column].mean(), inplace=True)
                elif strategy == 'median':
                    df_processed[column].fillna(df_processed[column].median(), inplace=True)
                elif strategy == 'forward_fill':
                    df_processed[column] = df_processed[column].ffill()
                elif strategy == 'backward_fill':
                    df_processed[column] = df_processed[column].bfill()
            else:
                # For categorical columns, use mode
                df_processed[column].fillna(df_processed[column].mode()[0], inplace=True)
        
        return df_processed
    
    def scale_features(self, df, columns=None, method='standard'):
        """
        Scale numerical features
        
        Args:
            df: Input DataFrame
            columns: Columns to scale (if None, scale all numeric columns)
            method: Scaling method ('standard' or 'minmax')
            
        Returns:
            DataFrame: Scaled data
        """
        
        df_scaled = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Method must be 'standard' or 'minmax'")
        
        df_scaled[columns] = scaler.fit_transform(df[columns])
        self.scalers[method] = scaler
        
        return df_scaled
    
    def encode_categorical_features(self, df, columns=None):
        """
        Encode categorical features
        
        Args:
            df: Input DataFrame
            columns: Columns to encode (if None, encode all categorical columns)
            
        Returns:
            DataFrame: Encoded data
        """
        
        df_encoded = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns.tolist()
        
        for column in columns:
            encoder = LabelEncoder()
            df_encoded[column] = encoder.fit_transform(df[column].astype(str))
            self.encoders[column] = encoder
        
        return df_encoded
    
    def create_features(self, df):
        """
        Create additional features for EV analysis
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame: Data with additional features
        """
        
        df_features = df.copy()
        
        # Speed-based features
        if 'speed' in df.columns:
            df_features['speed_squared'] = df['speed'] ** 2
            df_features['speed_category'] = pd.cut(
                df['speed'], 
                bins=[0, 30, 60, 90, 200], 
                labels=['Low', 'Medium', 'High', 'Very High']
            )
        
        # Acceleration-based features
        if 'acceleration' in df.columns:
            df_features['abs_acceleration'] = abs(df['acceleration'])
            df_features['acceleration_category'] = pd.cut(
                df['acceleration'],
                bins=[-10, -1, 0, 1, 10],
                labels=['Hard_Brake', 'Light_Brake', 'Cruise', 'Accelerate']
            )
        
        # Energy efficiency features
        if 'speed' in df.columns and 'energy_consumption' in df.columns:
            df_features['energy_per_speed'] = df['energy_consumption'] / (df['speed'] + 1)  # Add 1 to avoid division by zero
        
        # Temperature-based features
        if 'temperature' in df.columns:
            df_features['temperature_category'] = pd.cut(
                df['temperature'],
                bins=[-50, 0, 15, 25, 50],
                labels=['Very_Cold', 'Cold', 'Optimal', 'Warm']
            )
        
        # Road slope features
        if 'road_slope' in df.columns:
            df_features['abs_road_slope'] = abs(df['road_slope'])
            df_features['uphill'] = (df['road_slope'] > 0).astype(int)
            df_features['downhill'] = (df['road_slope'] < 0).astype(int)
        
        # Time-based features (if time column exists)
        time_columns = [col for col in df.columns if 'time' in col.lower()]
        if time_columns:
            time_col = time_columns[0]
            try:
                df_features[time_col] = pd.to_datetime(df[time_col])
                df_features['hour'] = df_features[time_col].dt.hour
                df_features['day_of_week'] = df_features[time_col].dt.dayofweek
                df_features['is_weekend'] = (df_features['day_of_week'] >= 5).astype(int)
            except:
                pass  # Skip if time conversion fails
        
        return df_features
    
    def generate_sample_data(self, n_samples=1000):
        """
        Generate sample EV energy consumption data for testing
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            DataFrame: Sample data
        """
        
        np.random.seed(42)
        
        # Generate base features
        speed = np.random.normal(60, 20, n_samples)  # km/h
        speed = np.clip(speed, 0, 180)
        
        acceleration = np.random.normal(0, 1.5, n_samples)  # m/s²
        acceleration = np.clip(acceleration, -5, 5)
        
        road_slope = np.random.normal(0, 2, n_samples)  # degrees
        road_slope = np.clip(road_slope, -10, 10)
        
        temperature = np.random.normal(20, 10, n_samples)  # °C
        temperature = np.clip(temperature, -20, 45)
        
        # Auxiliary power (heating/cooling, electronics)
        auxiliary_power = np.random.normal(1.5, 0.5, n_samples)  # kW
        auxiliary_power = np.clip(auxiliary_power, 0.5, 3.0)
        
        # Generate energy consumption based on physics-based model
        # Base consumption depends on speed (aerodynamic and rolling resistance)
        base_consumption = 0.15 * speed + 0.0008 * speed**2  # kWh/100km
        
        # Add acceleration effect
        acceleration_effect = np.abs(acceleration) * 2  # kWh/100km
        
        # Add road slope effect
        slope_effect = road_slope * 1.5  # kWh/100km
        
        # Add temperature effect (heating/cooling)
        temp_effect = np.abs(temperature - 22) * 0.1  # kWh/100km
        
        # Add auxiliary power effect
        aux_effect = auxiliary_power * 0.5  # kWh/100km
        
        # Calculate total energy consumption
        energy_consumption = (base_consumption + acceleration_effect + 
                            slope_effect + temp_effect + aux_effect)
        
        # Add some noise
        noise = np.random.normal(0, 1, n_samples)
        energy_consumption += noise
        energy_consumption = np.clip(energy_consumption, 5, 50)  # Reasonable bounds
        
        # Create DataFrame
        data = {
            'speed': speed,
            'acceleration': acceleration,
            'road_slope': road_slope,
            'temperature': temperature,
            'auxiliary_power': auxiliary_power,
            'energy_consumption': energy_consumption,
            'time': pd.date_range('2024-01-01', periods=n_samples, freq='1min'),
            'distance': np.cumsum(np.random.uniform(0.1, 2.0, n_samples)),  # km
            'battery_soc': np.random.uniform(20, 100, n_samples)  # %
        }
        
        df = pd.DataFrame(data)
        
        return df
    
    def prepare_for_modeling(self, df, target_column, feature_columns=None):
        """
        Prepare data for machine learning modeling
        
        Args:
            df: Input DataFrame
            target_column: Name of target column
            feature_columns: List of feature columns (if None, use all except target)
            
        Returns:
            tuple: (X, y) features and target
        """
        
        # Handle missing values
        df_clean = self.handle_missing_values(df)
        
        # Create additional features
        df_features = self.create_features(df_clean)
        
        # Encode categorical features
        df_encoded = self.encode_categorical_features(df_features)
        
        # Select features
        if feature_columns is None:
            feature_columns = [col for col in df_encoded.columns if col != target_column]
            # Remove non-numeric columns
            feature_columns = [col for col in feature_columns 
                             if df_encoded[col].dtype in ['float64', 'int64']]
        
        X = df_encoded[feature_columns]
        y = df_encoded[target_column]
        
        return X, y
    
    def get_data_summary(self, df):
        """
        Get comprehensive data summary
        
        Args:
            df: Input DataFrame
            
        Returns:
            dict: Data summary
        """
        
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'numeric_summary': df.describe().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2  # MB
        }
        
        return summary
