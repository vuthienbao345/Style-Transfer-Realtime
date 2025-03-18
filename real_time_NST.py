import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

import os
import random

import cv2
import numpy as np

def set_seed(seed):
    os.environ['PYTHONHASHSEED'] = str(seed)  # Set seed for Python's hash function
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.benchmark = True     # True = Optimize performance if input size is fixed
    torch.backends.cudnn.deterministic = False # True = Ensure reproducibility (may slow down training)
set_seed(42)

# Device
device     = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device_cnt = torch.cuda.device_count()
print(f"device: {device}, num device: {device_cnt}")

# Constant
mean = np.array([0.485, 0.456, 0.406])
std  = np.array([0.229, 0.224, 0.225])  

class TransformerNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        
        self.model = nn.Sequential(
            ConvBlock(3, 32, kernel_size=9, stride=1),
            ConvBlock(32, 64, kernel_size=3, stride=2),
            ConvBlock(64, 128, kernel_size=3, stride=2),
            ResidualBlock(128),
            ResidualBlock(128),
            ResidualBlock(128),
            ResidualBlock(128),
            ResidualBlock(128),
            ConvBlock(128, 64, kernel_size=3, upsample=True),
            ConvBlock(64, 32, kernel_size=3, upsample=True),
            ConvBlock(32, 3, kernel_size=9, stride=1, normalize=False, relu=False),
        )

    def forward(self, x):
        return self.model(x)

class ResidualBlock(torch.nn.Module):
    def __init__(self, channels):
        super().__init__()
        
        self.block = nn.Sequential(
            ConvBlock(channels, channels, kernel_size=3, stride=1, normalize=True, relu=True),
            ConvBlock(channels, channels, kernel_size=3, stride=1, normalize=True, relu=False),
        )

    def forward(self, x):
        return self.block(x) + x

class ConvBlock(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride=1, upsample=False, normalize=True, relu=True):
        super(ConvBlock, self).__init__()
        
        self.upsample = upsample
        self.block = nn.Sequential(
            nn.ReflectionPad2d(kernel_size // 2), 
            nn.Conv2d(in_channels, out_channels, kernel_size, stride)
        )
        self.norm = nn.InstanceNorm2d(out_channels, affine=True) if normalize else None
        self.relu = relu

    def forward(self, x):
        if self.upsample:
            x = F.interpolate(x, scale_factor=2)
        x = self.block(x)
        if self.norm is not None:
            x = self.norm(x)
        if self.relu:
            x = F.relu(x)
        return x

def preprocess_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    tensor_rgb = transform(frame_rgb).unsqueeze(0)
    return tensor_rgb.to(device)

def postprocess_frame(tensor):
    img_np  = tensor.squeeze(0).detach().cpu().numpy().transpose(1, 2, 0)
    img_np  = np.clip(img_np, 0, 1)
    img_np  = (img_np * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_bgr

def denormalize(tensors):
    for c in range(3):
        tensors[:, c].mul_(std[c]).add_(mean[c])
    return tensors

def inference_video_realtime(checkpoint_model):

    # Load model
    transformer = TransformerNet().to(device)
    transformer.load_state_dict(torch.load(checkpoint_model, weights_only=True))
    transformer.eval()

    # Live
    cap  = cv2.VideoCapture(0)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Inference
        tensor_rgb = preprocess_frame(frame)
        
        with torch.no_grad():
            with torch.amp.autocast('cuda'):
                stylized_tensor = transformer(tensor_rgb)
                
        stylized_tensor = denormalize(stylized_tensor).cpu()
        stylized_frame  = postprocess_frame(stylized_tensor)
        
        # Visualize
        stylized_frame = cv2.flip(stylized_frame, 1)
        cv2.imshow("Real-time Style Transfer", stylized_frame)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
inference_video_realtime(checkpoint_model='./weights/best_model-Post_Impressionism.pth')