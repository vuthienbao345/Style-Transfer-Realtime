import torch

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Normalization used in pre-trained VGG19
MEAN = torch.tensor([0.485, 0.456, 0.406])
STD  = torch.tensor([0.229, 0.224, 0.225])