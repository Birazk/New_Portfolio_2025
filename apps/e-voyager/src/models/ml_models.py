import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
import joblib
import time
import warnings
warnings.filterwarnings('ignore')

class MLModels:
    """
    Machine Learning models for EV energy consumption prediction
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        
    def train_models(self, X, y, model_names, test_size=0.2, random_state=42, nn_params=None):
        """
        Train multiple ML models for energy consumption prediction
        
        Args:
            X: Feature matrix
            y: Target vector
            model_names: List of model names to train
            test_size: Test set size ratio
            random_state: Random state for reproducibility
            nn_params: Neural network parameters
            
        Returns:
            Dictionary containing model results
        """
        
        # Store feature names
        self.feature_names = X.columns.tolist() if hasattr(X, 'columns') else [f'feature_{i}' for i in range(X.shape[1])]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features for neural network and SVR
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['standard'] = scaler
        
        results = {}
        
        for model_name in model_names:
            print(f"Training {model_name}...")
            start_time = time.time()
            
            try:
                if model_name == "Linear Regression":
                    model = self._train_linear_regression(X_train, y_train)
                    y_pred = model.predict(X_test)
                    
                elif model_name == "Random Forest":
                    model = self._train_random_forest(X_train, y_train)
                    y_pred = model.predict(X_test)
                    
                elif model_name == "Neural Network":
                    model = self._train_neural_network(X_train_scaled, y_train, nn_params)
                    y_pred = model.predict(X_test_scaled)
                    
                elif model_name == "Support Vector Regression":
                    model = self._train_svr(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    
                elif model_name == "Gradient Boosting":
                    model = self._train_gradient_boosting(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                else:
                    raise ValueError(f"Unknown model: {model_name}")
                
                # Calculate metrics
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                training_time = time.time() - start_time
                
                # Store results
                results[model_name] = {
                    'model': model,
                    'r2_score': r2,
                    'rmse': rmse,
                    'mae': mae,
                    'training_time': training_time,
                    'y_test': y_test,
                    'y_pred': y_pred,
                    'feature_names': self.feature_names,
                    'requires_scaling': model_name in ["Neural Network", "Support Vector Regression"]
                }
                
                # Store model
                self.models[model_name] = model
                
                print(f"{model_name} - R²: {r2:.4f}, RMSE: {rmse:.4f}, MAE: {mae:.4f}")
                
            except Exception as e:
                print(f"Error training {model_name}: {str(e)}")
                continue
        
        return results
    
    def _train_linear_regression(self, X_train, y_train):
        """Train Linear Regression model"""
        model = LinearRegression()
        model.fit(X_train, y_train)
        return model
    
    def _train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        return model
    
    def _train_neural_network(self, X_train, y_train, nn_params=None):
        """Train Neural Network model using scikit-learn MLPRegressor"""
        
        if nn_params is None:
            nn_params = {'hidden_layers': 2, 'neurons_per_layer': 64, 'epochs': 100}
        
        # Create hidden layer sizes tuple
        hidden_layer_sizes = tuple([nn_params['neurons_per_layer']] * nn_params['hidden_layers'])
        
        # Build model
        model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            activation='relu',
            solver='adam',
            alpha=0.001,
            batch_size='auto',
            learning_rate='adaptive',
            max_iter=nn_params['epochs'],
            random_state=42,
            early_stopping=True,
            validation_fraction=0.2,
            n_iter_no_change=10
        )
        
        # Train model
        model.fit(X_train, y_train)
        
        return model
    
    def _train_svr(self, X_train, y_train):
        """Train Support Vector Regression model"""
        model = SVR(
            kernel='rbf',
            C=1.0,
            gamma='scale'
        )
        model.fit(X_train, y_train)
        return model
    
    def _train_gradient_boosting(self, X_train, y_train):
        """Train Gradient Boosting model"""
        model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def predict(self, model_name, X):
        """
        Make predictions using a trained model
        
        Args:
            model_name: Name of the model to use
            X: Feature matrix for prediction
            
        Returns:
            Predictions array
        """
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found. Available models: {list(self.models.keys())}")
        
        model = self.models[model_name]
        
        # Apply scaling if required
        if model_name in ["Neural Network", "Support Vector Regression"]:
            X_scaled = self.scalers['standard'].transform(X)
            predictions = model.predict(X_scaled)
        else:
            predictions = model.predict(X)
        
        return predictions
    
    def get_model_info(self, model_name):
        """Get information about a trained model"""
        
        if model_name not in self.models:
            return None
        
        model = self.models[model_name]
        info = {
            'model_type': type(model).__name__,
            'feature_names': self.feature_names
        }
        
        # Add model-specific information
        if hasattr(model, 'feature_importances_'):
            info['feature_importances'] = dict(zip(self.feature_names, model.feature_importances_))
        
        if hasattr(model, 'coef_'):
            info['coefficients'] = dict(zip(self.feature_names, model.coef_))
        
        return info
    
    def save_models(self, filepath):
        """Save trained models to file"""
        
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'feature_names': self.feature_names
        }
        
        joblib.dump(model_data, filepath)
        print(f"Models saved to {filepath}")
    
    def load_models(self, filepath):
        """Load trained models from file"""
        
        model_data = joblib.load(filepath)
        self.models = model_data['models']
        self.scalers = model_data['scalers']
        self.feature_names = model_data['feature_names']
        
        print(f"Models loaded from {filepath}")
    
    def cross_validate_model(self, model_name, X, y, cv=5):
        """
        Perform cross-validation on a model
        
        Args:
            model_name: Name of the model
            X: Feature matrix
            y: Target vector
            cv: Number of cross-validation folds
            
        Returns:
            Cross-validation scores
        """
        
        from sklearn.model_selection import cross_val_score
        
        if model_name == "Linear Regression":
            model = LinearRegression()
        elif model_name == "Random Forest":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_name == "Gradient Boosting":
            model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        elif model_name == "Support Vector Regression":
            model = SVR(kernel='rbf')
            # Scale features for SVR
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
        else:
            raise ValueError(f"Cross-validation not implemented for {model_name}")
        
        scores = cross_val_score(model, X, y, cv=cv, scoring='r2')
        
        return {
            'mean_score': scores.mean(),
            'std_score': scores.std(),
            'scores': scores
        }
    
    def tune_hyperparameters(self, model_name, X, y, param_grid=None):
        """
        Perform hyperparameter tuning using GridSearch
        
        Args:
            model_name: Name of the model
            X: Feature matrix
            y: Target vector
            param_grid: Parameter grid for tuning
            
        Returns:
            Best parameters and score
        """
        
        from sklearn.model_selection import GridSearchCV
        
        if model_name == "Random Forest":
            model = RandomForestRegressor(random_state=42)
            if param_grid is None:
                param_grid = {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, None],
                    'min_samples_split': [2, 5, 10]
                }
        
        elif model_name == "Support Vector Regression":
            model = SVR()
            # Scale features
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            if param_grid is None:
                param_grid = {
                    'C': [0.1, 1, 10],
                    'gamma': ['scale', 'auto'],
                    'kernel': ['rbf', 'linear']
                }
        
        else:
            raise ValueError(f"Hyperparameter tuning not implemented for {model_name}")
        
        grid_search = GridSearchCV(
            model, param_grid, cv=5, scoring='r2', n_jobs=-1
        )
        
        grid_search.fit(X, y)
        
        return {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'best_model': grid_search.best_estimator_
        }
