# Define target variables for each model
targets = ['PTS', 'TOT', 'A']  # Points, Rebounds, Assists

# Identify current game stats that would cause data leakage
current_game_stats = [
    'MIN', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'OR', 'DR', 'TOT', 'A', 
    'PF', 'ST', 'TO', 'BL', 'PTS', 'FG%', '3P%', 'eFG%', 'TS%', 'TSA', 
    'PTS_per36', 'TOT_per36', 'A_per36', 'GmSc'
]

# Identify non-feature columns
non_feature_cols = [
    'date', 'BIGDATABALL\nDATASET'  # game_id already dropped
]

# Function to train and evaluate an XGBoost model
def train_xgb_model(target, train_df, val_df, test_df):
    # Identify features (exclude current game stats, target, and non-feature columns)
    exclude_cols = current_game_stats + non_feature_cols + categorical_columns
    
    # For each target model, also exclude other direct target-related features
    if target == 'PTS':
        target_related = [col for col in train_df.columns if 'PTS' in col and col != 'PTS' and col not in exclude_cols]
        exclude_cols += target_related
    elif target == 'TOT':
        target_related = [col for col in train_df.columns if 'TOT' in col and col != 'TOT' and col not in exclude_cols]
        exclude_cols += target_related  
    elif target == 'A':
        target_related = [col for col in train_df.columns if '_A' in col and col != 'A' and col not in exclude_cols]
        exclude_cols += target_related
    
    # Identify feature columns
    feature_cols = [col for col in train_df.columns if col not in exclude_cols and col != target]
    
    # Prepare the training data
    X_train = train_df[feature_cols]
    y_train = train_df[target]
    X_val = val_df[feature_cols]
    y_val = val_df[target]
    X_test = test_df[feature_cols]
    y_test = test_df[target]
    
    print(f"\nFeatures used for {target} model: {len(feature_cols)}")
    
    # Create DMatrix objects
    dtrain = xgb.DMatrix(X_train, label=y_train)
    dval = xgb.DMatrix(X_val, label=y_val)
    dtest = xgb.DMatrix(X_test, label=y_test)
    
    # Set XGBoost parameters
    params = {
        'objective': 'reg:squarederror',
        'eval_metric': 'rmse',
        'eta': 0.1,                # Learning rate
        'max_depth': 6,            # Maximum tree depth
        'subsample': 0.8,          # Subsample ratio of training instances
        'colsample_bytree': 0.8,   # Subsample ratio of columns for each tree
        'min_child_weight': 1,     # Minimum sum of instance weight needed in a child
        'lambda': 1,               # L2 regularization
        'alpha': 0                 # L1 regularization
    }
    
    # Define watchlist to monitor training
    watchlist = [(dtrain, 'train'), (dval, 'validation')]
    
    # Train the model
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=1000,
        evals=watchlist,
        early_stopping_rounds=50,
        verbose_eval=100
    )
    
    # Make predictions
    val_preds = model.predict(dval)
    test_preds = model.predict(dtest)
    
    # Evaluate validation set performance
    val_rmse = np.sqrt(mean_squared_error(y_val, val_preds))
    val_mae = mean_absolute_error(y_val, val_preds)
    val_r2 = r2_score(y_val, val_preds)
    
    # Evaluate test set performance
    test_rmse = np.sqrt(mean_squared_error(y_test, test_preds))
    test_mae = mean_absolute_error(y_test, test_preds)
    test_r2 = r2_score(y_test, test_preds)
    
    print(f"\n{target} Model Performance:")
    print(f"Validation RMSE: {val_rmse:.4f}")
    print(f"Validation MAE: {val_mae:.4f}")
    print(f"Validation R²: {val_r2:.4f}")
    print(f"Test RMSE: {test_rmse:.4f}")
    print(f"Test MAE: {test_mae:.4f}")
    print(f"Test R²: {test_r2:.4f}")
    
    # Plot feature importance
    importance = model.get_score(importance_type='gain')
    importance_df = pd.DataFrame({'Feature': list(importance.keys()), 'Importance': list(importance.values())})
    importance_df = importance_df.sort_values('Importance', ascending=False).head(20)
    
    plt.figure(figsize=(12, 8))
    plt.barh(importance_df['Feature'], importance_df['Importance'])
    plt.xlabel('Importance')
    plt.ylabel('Feature')
    plt.title(f'Top 20 Features for {target} Prediction')
    plt.gca().invert_yaxis()  # Display the most important feature at the top
    plt.tight_layout()
    plt.savefig(f'{target}_feature_importance.png')
    plt.show()
    
    # Plot actual vs predicted values for test set
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, test_preds, alpha=0.5)
    plt.plot([0, y_test.max()], [0, y_test.max()], 'r--')
    plt.xlabel(f'Actual {target}')
    plt.ylabel(f'Predicted {target}')
    plt.title(f'{target} - Actual vs Predicted (Test Set)')
    plt.tight_layout()
    plt.savefig(f'{target}_actual_vs_predicted.png')
    plt.show()
    
    # Return model and metrics for further analysis
    return {
        'model': model,
        'features': feature_cols,
        'val_preds': val_preds,
        'test_preds': test_preds,
        'val_metrics': {'rmse': val_rmse, 'mae': val_mae, 'r2': val_r2},
        'test_metrics': {'rmse': test_rmse, 'mae': test_mae, 'r2': test_r2},
        'importance': importance_df
    }

# Train models for each target
models = {}
for target in targets:
    print(f"\n=== Training {target} Prediction Model ===")
    models[target] = train_xgb_model(target, train_df, val_df, test_df)

# Generate a summary of model performance
summary = pd.DataFrame({
    'Target': targets,
    'Test RMSE': [models[t]['test_metrics']['rmse'] for t in targets],
    'Test MAE': [models[t]['test_metrics']['mae'] for t in targets],
    'Test R²': [models[t]['test_metrics']['r2'] for t in targets],
    'Val RMSE': [models[t]['val_metrics']['rmse'] for t in targets],
    'Val MAE': [models[t]['val_metrics']['mae'] for t in targets],
    'Val R²': [models[t]['val_metrics']['r2'] for t in targets],
    'Num Features': [len(models[t]['features']) for t in targets]
})

print("\n=== Model Performance Summary ===")
print(summary)

# Save models
for target in targets:
    models[target]['model'].save_model(f'xgb_{target}_model.json')
    print(f"Saved {target} model to xgb_{target}_model.json")

# Optional: Save feature importance for later analysis
for target in targets:
    models[target]['importance'].to_csv(f'{target}_feature_importance.csv', index=False)