#!/usr/bin/env python3
"""
Train MiniMind baseline predictor for Love Engine
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import sys
from pathlib import Path

def load_dataset(csv_file):
    """Load the extracted dataset"""
    if not Path(csv_file).exists():
        print(f"Error: {csv_file} not found. Run extract_dataset.py first!")
        sys.exit(1)
    
    df = pd.read_csv(csv_file)
    
    if len(df) < 10:
        print(f"Error: Insufficient data ({len(df)} samples). Need at least 10 labeled samples.")
        sys.exit(1)
    
    return df

def train_minimind(df):
    """Train the baseline predictor"""
    # Feature selection
    feature_cols = ['message_length', 'answer_length', 'safety_triggered', 'love_applied', 'thermo_cooled']
    available_features = [col for col in feature_cols if col in df.columns]
    
    if not available_features:
        print("Error: No valid features found in dataset")
        sys.exit(1)
    
    X = df[available_features]
    y = df['target']
    
    print(f"Training with features: {available_features}")
    print(f"Dataset shape: {X.shape}")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Handle small datasets
    if len(df) < 30:
        print("Small dataset detected. Using simple validation.")
        model = RandomForestClassifier(n_estimators=10, random_state=42, max_depth=3)
        model.fit(X, y)
        
        # Simple validation
        train_score = model.score(X, y)
        print(f"Training accuracy: {train_score:.3f}")
        
        return model, available_features
    
    # Standard train/test split for larger datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Train model
    model = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Training accuracy: {train_score:.3f}")
    print(f"Test accuracy: {test_score:.3f}")
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=min(5, len(df)//2))
    print(f"CV accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature importance:")
    print(importance)
    
    return model, available_features

def save_model(model, features, model_path='minimind_model.joblib'):
    """Save the trained model"""
    model_data = {
        'model': model,
        'features': features,
        'version': 'minimind-0.1'
    }
    
    joblib.dump(model_data, model_path)
    print(f"Model saved to {model_path}")

def main():
    csv_file = sys.argv[1] if len(sys.argv) > 1 else 'minimind_dataset.csv'
    model_path = sys.argv[2] if len(sys.argv) > 2 else 'minimind_model.joblib'
    
    print("=== MINIMIND TRAINING ===")
    print(f"Loading dataset from {csv_file}...")
    
    df = load_dataset(csv_file)
    
    print(f"Training MiniMind with {len(df)} samples...")
    model, features = train_minimind(df)
    
    save_model(model, features, model_path)
    
    print("\n🧠 MiniMind training complete!")
    print("The system can now predict response quality patterns.")

if __name__ == '__main__':
    main()