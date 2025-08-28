import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torch.autograd import Variable
import cv2
import tempfile
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from PIL import Image
from io import BytesIO
import os
import base64

app = Flask(__name__)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])

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

def test_transform(image_size=None):
    resize = [transforms.Resize(image_size)] if image_size else []
    transform = transforms.Compose(resize + [transforms.ToTensor(), transforms.Normalize(mean, std)])
    return transform

def denormalize(tensors):
    for c in range(3):
        tensors[:, c].mul_(std[c]).add_(mean[c])
    return tensors

def preprocess_frame(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])

    tensor_rgb = transform(frame_rgb).unsqueeze(0)
    return tensor_rgb.to(device)

def postprocess_frame(tensor):
    img_np = tensor.squeeze(0).detach().cpu().numpy().transpose(1, 2, 0)
    img_np = np.clip(img_np, 0, 1)
    img_np = (img_np * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_bgr

def get_video_info(video):
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_frame = length
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return fps, length, total_frame, w, h

def inference(content_image, checkpoint_model):
    model = TransformerNet()
    model.load_state_dict(torch.load(checkpoint_model, map_location=device))
    model.to(device)
    model.eval()
    
    transform = test_transform(256)
    image = transform(content_image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(image)
    
    output = denormalize(output)
    output = output.squeeze(0).detach().cpu().numpy().transpose(1, 2, 0)
    output = np.clip(output, 0, 1)
    
    return output

def inference_video(content_video, checkpoint_model, output_path):
    model = TransformerNet()
    model.load_state_dict(torch.load(checkpoint_model, map_location=device))
    model.to(device)
    model.eval()
    
    cap = cv2.VideoCapture(content_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        tensor = preprocess_frame(frame)
        
        with torch.no_grad():
            output = model(tensor)
        
        output = denormalize(output)
        styled_frame = postprocess_frame(output)
        out.write(styled_frame)
    
    cap.release()
    out.release()
    
    return output_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/stylize', methods=['POST'])
def stylize():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        style = request.form.get('style', 'Post Impressionism')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Load and process image
        image = Image.open(file.stream).convert('RGB')
        
        # Style mapping
        style_dict = {
            'Post Impressionism': 'weights/best_model-Post_Impressionism.pth',
            'Cubism': 'weights/best_model-Cubism.pth',
            'Abstract Expressionism': 'weights/best_model-Abstract_Expressionism.pth',
            'Digital Painting': 'weights/best_model-Digital_Painting.pth'
        }
        
        if style not in style_dict:
            return jsonify({'error': 'Invalid style'}), 400
        
        # Apply style transfer
        result = inference(image, style_dict[style])
        
        # Convert result to base64
        result_img = Image.fromarray((result * 255).astype(np.uint8))
        buffer = BytesIO()
        result_img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': img_str
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
