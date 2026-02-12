"""
ML Model Training (Optional)
Train a machine learning model for risk classification
"""

import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd

def generate_sample_data(n_samples=1000):
    """
    Generate synthetic training data
    In production, use real historical data
    """
    np.random.seed(42)
    
    data = []
    for _ in range(n_samples):
        # Generate features
        risk_score = np.random.uniform(0, 100)
        motion_count = np.random.randint(0, 15)
        time_of_day = np.random.randint(0, 24)
        day_of_week = np.random.randint(0, 7)
        frequency = np.random.uniform(0, 10)
        
        # Determine label based on rules (simulate ground truth)
        if risk_score >= 80 or motion_count >= 8:
            label = 3  # CRITICAL
        elif risk_score >= 60 or motion_count >= 5:
            label = 2  # HIGH
        elif risk_score >= 35 or motion_count >= 2:
            label = 1  # MEDIUM
        else:
            label = 0  # LOW
        
        # Add some noise to make it interesting
        if np.random.random() < 0.1:
            label = (label + np.random.randint(-1, 2)) % 4
        
        data.append([risk_score, motion_count, time_of_day, day_of_week, frequency, label])
    
    df = pd.DataFrame(data, columns=[
        'risk_score', 'motion_count', 'time_of_day', 
        'day_of_week', 'frequency', 'label'
    ])
    
    return df

def train_model(data_path=None, output_path='trained_model.pkl'):
    """
    Train Random Forest classifier
    
    Args:
        data_path: Path to CSV with training data (optional)
        output_path: Path to save trained model
    """
    print("=" * 60)
    print("Training Risk Classification Model")
    print("=" * 60)
    
    # Load or generate data
    if data_path:
        print(f"Loading data from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print("Generating synthetic training data...")
        df = generate_sample_data(n_samples=1000)
    
    print(f"Dataset size: {len(df)} samples")
    print(f"\nClass distribution:")
    print(df['label'].value_counts().sort_index())
    
    # Prepare features and labels
    feature_columns = ['risk_score', 'motion_count', 'time_of_day', 'day_of_week', 'frequency']
    X = df[feature_columns].values
    y = df['label'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train Random Forest
    print("\nTraining Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training Accuracy: {train_score:.3f}")
    print(f"Test Accuracy: {test_score:.3f}")
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Classification report
    print("\nClassification Report:")
    target_names = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # Confusion matrix
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    # Feature importance
    print("\nFeature Importance:")
    for feature, importance in zip(feature_columns, model.feature_importances_):
        print(f"  {feature:20s}: {importance:.3f}")
    
    # Save model
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\n✓ Model saved to {output_path}")
    print("\nTo use the model:")
    print("  1. Copy trained_model.pkl to cloud-intelligence folder")
    print("  2. RiskClassifier will automatically load and use it")
    
    return model

def test_model(model_path='trained_model.pkl'):
    """Test the trained model with example inputs"""
    print("\n" + "=" * 60)
    print("Testing Model with Examples")
    print("=" * 60)
    
    # Load model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Test cases
    test_cases = [
        {
            'name': 'Low Risk',
            'features': [20, 1, 14, 2, 0.5],  # Low score, 1 object, afternoon
            'expected': 'LOW'
        },
        {
            'name': 'Medium Risk',
            'features': [45, 3, 10, 1, 2.0],  # Medium score, 3 objects, morning
            'expected': 'MEDIUM'
        },
        {
            'name': 'High Risk',
            'features': [70, 6, 22, 5, 4.5],  # High score, 6 objects, night
            'expected': 'HIGH'
        },
        {
            'name': 'Critical Risk',
            'features': [90, 10, 3, 6, 8.0],  # Very high score, many objects, early morning
            'expected': 'CRITICAL'
        }
    ]
    
    level_map = {0: 'LOW', 1: 'MEDIUM', 2: 'HIGH', 3: 'CRITICAL'}
    
    for case in test_cases:
        prediction = model.predict([case['features']])[0]
        predicted_level = level_map[prediction]
        
        print(f"\n{case['name']}:")
        print(f"  Features: {case['features']}")
        print(f"  Expected: {case['expected']}")
        print(f"  Predicted: {predicted_level}")
        print(f"  ✓ Match!" if predicted_level == case['expected'] else "  ✗ Mismatch")

if __name__ == "__main__":
    # Train the model
    model = train_model()
    
    # Test the model
    test_model()
