import torch
import pytorch_lightning as pl
import pytorch_forecasting
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters

print(f"PyTorch version: {torch.__version__}")
print(f"PyTorch Lightning version: {pl.__version__}")
print(f"PyTorch Forecasting version: {pytorch_forecasting.__version__}")


print("Successfully imported optimize_hyperparameters")
