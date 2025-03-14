import torch
import torchvision.transforms as transforms
import cv2
from PIL import Image
import os
import numpy as np
import matplotlib.pyplot as plt

from setting import DEVICE, MEAN, STD


# Unnormalize tensor
def unnormalize(tensor):
    for t, m, s in zip(tensor, MEAN, STD):
        t.mul_(s).add_(m)
    tensor.clamp_(0, 1)
    return tensor


# Read and transform image
def load_image(img_path, size=(256,256)):
    img_transforms = transforms.Compose([
        transforms.Resize(size),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD)
    ])

    img        = Image.open(img_path).convert('RGB')
    img_tensor = img_transforms(img)
    img_tensor = img_tensor.unsqueeze(0).to(DEVICE, torch.float)
    
    return img_tensor


# Plot image with save option
def plot_image(tensor, title=None, save=False, save_path=None):
    img = tensor.detach().clone().cpu().squeeze(0)
    img = unnormalize(img)
    img = transforms.ToPILImage()(img)

    if save:
        os.makedirs(save_path, exist_ok=True)
        img.save(save_path)

    plt.figure()
    plt.imshow(img)
    if title:
        plt.title(title, pad=10)
    plt.axis('off')
    plt.show()
    
    
# Preprocess video frame before apply NST
def preprocess_frame(frame, size=(256,256)):
    img_transforms = transforms.Compose([
        transforms.Resize(size),
        transforms.CenterCrop(size),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD)
    ])
    
    numpy_rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image  = Image.fromarray(numpy_rgb)
    tensor_rgb = img_transforms(pil_image)
    tensor_rgb = tensor_rgb.unsqueeze(0).to(DEVICE, torch.float)
    return tensor_rgb


# Postprocess video after apply NST to regenerate video
def postprocess_frame(tensor):
    tensor_clone = tensor.detach().clone().cpu().squeeze(0)
    tensor_rgb   = unnormalize(tensor_clone)
    
    numpy_rgb = tensor_rgb.permute(1, 2, 0).numpy()
    numpy_rgb = (numpy_rgb * 255).astype(np.uint8)
    numpy_bgr = cv2.cvtColor(numpy_rgb, cv2.COLOR_RGB2BGR)
    return numpy_bgr