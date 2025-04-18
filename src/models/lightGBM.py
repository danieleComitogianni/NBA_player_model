import sklearn
import lightgbm as lgb
from scipy.stats import randint,uniform
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

pd.set_option('display.max_columns', None)
df = pd.read_parquet('../../data/merged_data_for_model/merged_model_data_collab.parquet')

unnamed_columns = [col for col in df.columns if 'Unnamed' in str(col)]

if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0']).reset_index(drop=True)

categorical_columns = [
    'player_id','team_id','opponent_id', 'offensive_archetype_id','defensive_role_id'
]
for col in categorical_columns:
    df[col] = df[col].astype('category')
df = df.drop(columns=['BIGDATABALL\nDATASET'])
df = df.drop(columns=['rotation_role_id'])
diff_columns = [col for col in df.columns if 'diff_' in col]
print(df.info())
print(df.columns.to_list())
df = df.drop(columns=diff_columns)
print(df.info())

train_ratio = 0.8
validation_ratio = 0.1
test_ratio = 0.1

train_validation_df,test_df = sklearn.model_selection.train_test_split(df,test_size=0.1,shuffle=False)
train_df,val_df = sklearn.model_selection.train_test_split(train_validation_df, test_size=0.1/(0.8+0.1),shuffle=False)
train_df = train_df.drop(columns=['game_id'])
val_df = val_df.drop(columns=['game_id'])
test_df = test_df.drop(columns=['game_id'])
print(f"Train set: {len(train_df)} rows ({train_df['date'].min()} to {train_df['date'].max()})")
print(f"Validation set: {len(val_df)} rows ({val_df['date'].min()} to {val_df['date'].max()})")
print(f"Test set: {len(test_df)} rows ({test_df['date'].min()} to {test_df['date'].max()})")

print(lgb.__version__)
target_variables = ['GmSc']
exclude_features = [
    'MIN', 'FG', 'FGA', '3P', '3PA', 'FT', 'FTA', 'OR', 'DR', 'TOT', 'A', 'PF', 'ST', 'TO', 'BL', 'PTS',
    'usage_rate(%)', 'FG%', '3P%', 'eFG%', 'TS%', 'TSA', 'PTS_per36', 'TOT_per36', 'A_per36', 'GmSc', 'date',
    'dpm', 'o_dpm', 'd_dpm', 'box_odpm', 'box_ddpm', 'on_off_odpm', 'on_off_ddpm', 
    'LEBRON WAR', 'LEBRON', 'O-LEBRON', 'D-LEBRON',
    'orr', 'drr', 'PACE'
]
categorical_features = ['player_id', 'team_id', 'opponent_id', 'offensive_archetype_id', 'defensive_role_id']

model_data = {}

for target in target_variables:
    print(f"\n\n{'='*50}")
    print(f"Tuning hyperparameters for {target}")
    print(f"{'='*50}")
    features = [col for col in train_df.columns if col not in exclude_features and col != target]
    model_data[target] = {
        'train_X': train_df[features],
        'train_y': train_df[target],
        'val_X': val_df[features],
        'val_y': val_df[target],
        'test_X': test_df[features],
        'test_y': test_df[target],
        'features': features
    }

def train_lightgbm_model(train_X, train_y, val_X, val_y, categorical_features, target_name):
    
    param_distributions = {
        'learning_rate':[0.03,0.05,0.1],
        'num_leaves': [50,100,120],
        'max_depth': [5,7,-1],
        'n_estimators': [1000,2000,3000],
        'subsample': [0.8,0.9,1.0],
        'min_child_samples': [20,30,50],
        'colsample_bytree': [0.8,0.9,1.0],
        'reg_alpha': [0.1,1,5],
        'reg_lambda': [0.1,1,5]
    }
    # Create LightGBM datasets
    train_data = lgb.Dataset(
        train_X,
        label=train_y,
        categorical_feature=categorical_features
    )
    
    valid_data = lgb.Dataset(
        val_X,
        label=val_y,
        reference=train_data,
        categorical_feature=categorical_features
    )
    
    lgb_model = lgb.LGBMRegressor(
        objective='regression',
        metric='mse',
        verbose=-1,
        random_state=42,
    )

    random_search = sklearn.model_selection.RandomizedSearchCV(
        estimator = lgb_model,
        param_distributions = param_distributions,
        n_iter = 25,
        scoring = 'neg_mean_squared_error',
        cv = 5,
        verbose = 1,
        random_state = 42,
        n_jobs = 1
    )

    print(f"starting hyperparamter tuning for {target_name}")

    random_search.fit(train_X,train_y,categorical_feature=categorical_features)

    best_params = random_search.best_params_
    print(f"\nBest parameters for {target_name}")
    for param,value in best_params.items():
      print(f"{param}: {value}")

    train_data = lgb.Dataset(
        train_X,
        label=train_y,
        categorical_feature=categorical_features
    )

    valid_data = lgb.Dataset(
        val_X,
        label=val_y,
        reference=train_data,
        categorical_feature=categorical_features
    )

    final_params = {
        'objective': 'regression',
        'metric': 'mse',
        'boosting_type': 'gbdt',
        'verbose': -1,
        'num_leaves': best_params['num_leaves'],
        'learning_rate': best_params['learning_rate'],
        'feature_fraction': best_params['colsample_bytree'],
        'bagging_fraction': best_params['subsample'],
        'bagging_freq': 5,
        'min_child_samples': best_params['min_child_samples'],
        'reg_alpha': best_params['reg_alpha'],
        'reg_lambda': best_params['reg_lambda']
    }
    if best_params['max_depth'] != -1:
        final_params['max_depth'] = best_params['max_depth']

    model = lgb.train(
        params=final_params,
        train_set=train_data,
        num_boost_round=best_params['n_estimators'],
        valid_sets=[valid_data],
        valid_names=['validation'],
        callbacks=[
            lgb.early_stopping(stopping_rounds=50),
            lgb.log_evaluation(period=100)
        ],
    )
    
    # Get predictions using best iteration
    val_preds = model.predict(val_X)
    
    # Calculate metrics
    mae = mean_absolute_error(val_y, val_preds)
    rmse = np.sqrt(mean_squared_error(val_y, val_preds))
    r2 = r2_score(val_y, val_preds)
    
    print(f"\nTuned Model Results for {target_name}:")
    print(f"Best Iteration: {model.best_iteration}")
    print(f"MAE: {mae:.4f}")
    print(f"RMSE: {rmse:.4f}")
    print(f"R²: {r2:.4f}")
    
    # Feature importance
    feature_importance = model.feature_importance(importance_type='gain')
    feature_names = model.feature_name()
    
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': feature_importance
    })
    importance_df = importance_df.sort_values('Importance', ascending=False)
    
    plt.figure(figsize=(10, 8))
    plt.barh(importance_df['Feature'].head(20), importance_df['Importance'].head(20))
    plt.title(f'Top 20 Feature Importance for {target_name}')
    plt.xlabel('Importance (Gain)')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
    
    return model, importance_df, (mae, rmse, r2)


results = {}
models = {}
feature_importance = {}
best_params_dict = {}

for target in target_variables:
    print(f"\n\n{'='*50}")
    print(f"Training model for {target}")
    print(f"{'='*50}")
    
    # Get data for this target from your model_data dictionary
    train_X = model_data[target]['train_X']
    train_y = model_data[target]['train_y']
    val_X = model_data[target]['val_X']
    val_y = model_data[target]['val_y']
    
    # Get only the categorical features that exist in the features for this target
    target_categorical_features = [feat for feat in categorical_features if feat in train_X.columns]
    
    # Train model
    model, importance, metrics = train_lightgbm_model(
        train_X, 
        train_y, 
        val_X, 
        val_y, 
        target_categorical_features,
        target
    )
    
    # Store results
    models[target] = model
    feature_importance[target] = importance
    results[target] = {
        'mae': metrics[0],
        'rmse': metrics[1],
        'r2': metrics[2]
    }

# Compare results across targets
print("\n\nSummary of Model Performance:")
print("=" * 50)
for target in target_variables:
    print(f"{target}: MAE = {results[target]['mae']:.4f}, RMSE = {results[target]['rmse']:.4f}, R² = {results[target]['r2']:.4f}")


"""
Best parameters for PTS
subsample: 0.8
reg_lambda: 1
reg_alpha: 0.1
num_leaves: 50
n_estimators: 1000
min_child_samples: 30
max_depth: 5
learning_rate: 0.05
colsample_bytree: 0.8
Training until validation scores don't improve for 50 rounds
[100]   validation's l2: 36.0992
[200]   validation's l2: 35.928
Early stopping, best iteration is:
[223]   validation's l2: 35.9005

Tuned Model Results for PTS:
Best Iteration: 223
MAE: 4.5534
RMSE: 5.9917
R²: 0.5669


Summary of Model Performance:
==================================================
PTS: MAE = 4.5534, RMSE = 5.9917, R² = 0.5669


Best parameters for TOT
subsample: 0.8
reg_lambda: 1
reg_alpha: 0.1
num_leaves: 50
n_estimators: 1000
min_child_samples: 30
max_depth: 5
learning_rate: 0.05
colsample_bytree: 0.8
Training until validation scores don't improve for 50 rounds
[100]   validation's l2: 6.0816
[200]   validation's l2: 6.06695
Early stopping, best iteration is:
[239]   validation's l2: 6.06183

Tuned Model Results for TOT:
Best Iteration: 239
MAE: 1.8544
RMSE: 2.4621
R²: 0.4945


Best parameters for A
subsample: 1.0
reg_lambda: 0.1
reg_alpha: 5
num_leaves: 120
n_estimators: 1000
min_child_samples: 50
max_depth: 5
learning_rate: 0.05
colsample_bytree: 0.8
Training until validation scores don't improve for 50 rounds
[100]   validation's l2: 3.06399
[200]   validation's l2: 3.05577
Early stopping, best iteration is:
[230]   validation's l2: 3.05401

Tuned Model Results for A:
Best Iteration: 230
MAE: 1.2722
RMSE: 1.7476
R²: 0.5566


Summary of Model Performance:
==================================================
A: MAE = 1.2722, RMSE = 1.7476, R² = 0.5566


==================================================
Tuning hyperparameters for GmSc
==================================================


==================================================
Training model for GmSc
==================================================
starting hyperparamter tuning for GmSc
Fitting 5 folds for each of 25 candidates, totalling 125 fits

Best parameters for GmSc
subsample: 0.9
reg_lambda: 1
reg_alpha: 1
num_leaves: 100
n_estimators: 1000
min_child_samples: 20
max_depth: 7
learning_rate: 0.03
colsample_bytree: 0.8
Training until validation scores don't improve for 50 rounds
[100]   validation's l2: 35.9537
[200]   validation's l2: 35.5935
Early stopping, best iteration is:
[235]   validation's l2: 35.5798

Tuned Model Results for GmSc:
Best Iteration: 235
MAE: 4.5647
RMSE: 5.9649
R²: 0.4394


Summary of Model Performance:
==================================================
GmSc: MAE = 4.5647, RMSE = 5.9649, R² = 0.4394

"""