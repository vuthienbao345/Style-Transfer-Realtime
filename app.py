import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torch.autograd import Variable
import cv2
import tempfile
import numpy as np
import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(layout="wide", page_title="Style Transfer App", page_icon="🎨")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
mean   = np.array([0.485, 0.456, 0.406])
std    = np.array([0.229, 0.224, 0.225])  

    
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
    resize    = [transforms.Resize(image_size)] if image_size else []
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
    img_np  = tensor.squeeze(0).detach().cpu().numpy().transpose(1, 2, 0)
    img_np  = np.clip(img_np, 0, 1)
    img_np  = (img_np * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_bgr

def get_video_info(video):
    cap         = cv2.VideoCapture(video)
    fps         = int(cap.get(cv2.CAP_PROP_FPS))
    total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    length      = total_frame / fps
    w, h        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    return fps, length, total_frame, w, h

def inference(content_image, checkpoint_model):
    # Load model
    transformer = TransformerNet().to(device)
    transformer.load_state_dict(torch.load(checkpoint_model, weights_only=True))
    transformer.eval()
    
    # Inference
    image_tensor = Variable(test_transform()(Image.open(content_image))).to(device)
    image_tensor = image_tensor.unsqueeze(0)
    with torch.no_grad():
        stylized_image = denormalize(transformer(image_tensor)).cpu()
    
    stylized_image_np = stylized_image.squeeze(0).permute(1, 2, 0).numpy()
    stylized_image_np = np.clip(stylized_image_np, 0, 1)
    return stylized_image_np
def inference_video(content_video, checkpoint_model, output_path):
    # Load model
    transformer = TransformerNet().to(device)
    transformer.load_state_dict(torch.load(checkpoint_model, weights_only=True))
    transformer.eval()

    # Video attributes
    cap  = cv2.VideoCapture(content_video)
    fps  = int(cap.get(cv2.CAP_PROP_FPS))
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Writer for saving videop4")
    fourcc      = cv2.VideoWriter_fourcc(*'mp4v') # Codec
    out         = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    # Inference
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        tensor_rgb = preprocess_frame(frame)
        with torch.no_grad():
            stylized_tensor = transformer(tensor_rgb)
        stylized_tensor = denormalize(stylized_tensor).cpu()
        stylized_frame  = postprocess_frame(stylized_tensor)
        out.write(stylized_frame)

    # Release
    cap.release()
    out.release()


if __name__ == '__main__':
    st.title("🎨 Style Transfer App")
    st.markdown(
        """
        Welcome to the **Style Transfer App!**  
        Transform your photo or video into stunning artworks inspired by famous artistic styles. Simply upload your image/video, choose a style, and let AI do the rest!
        """
    )
    st.divider()


    sub1, space1, sub2, space2, sub3 = st.columns([10,0.2,10,0.2,10])
    content_type = None # 0-image, 1-video
    
    with sub1:
        st.subheader('**1. Upload Your Image/Video**')
        st.write('')
        
        uploaded = st.file_uploader(' ', type=['png', 'jpg', 'jpeg', '.mp4'], label_visibility='collapsed')
        if uploaded is not None:
            ext = uploaded.name.split('.')[-1].lower()
            
            if ext in ['png', 'jpg', 'jpeg']:
                content_type = 0
                content      = Image.open(uploaded)
                st.image(content, use_container_width=True)
                
            elif ext == 'mp4':
                content_type = 1
                st.video(uploaded, muted=True)
                
    with sub2:
        st.subheader('**2. Choose Your Favourite Style**')
        st.write('')
        
        col1, col2 = st.columns([2,1])
        with col1:
            chose_style = st.selectbox(
                ' ', options=['Post Impressionism', 'Cubism', 'Abstract Expressionism', 'Digital Painting'], 
                label_visibility='collapsed'
            )
        with col2:
            style_btn = st.button('Start Stylizing!', type='secondary', use_container_width=True)
        
        style1 = Image.open('resources/styles/style_1-Post_Impressionism.png')
        style2 = Image.open('resources/styles/style_2-Cubism.jpg')
        style3 = Image.open('resources/styles/style_3-Abstract_Expressionism.png')
        style4 = Image.open('resources/styles/style_4-Digital_Painting.jpg')
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(style1, caption='Post Impressionism', use_container_width=True)
            st.image(style3, caption='Abstract Expressionism', use_container_width=True)
        with col2:
            st.image(style2, caption='Cubism', use_container_width=True)
            st.image(style4, caption='Digital Painting', use_container_width=True)
        
    with sub3:
        st.subheader('**3. Your Styled Image/Video**')
        st.write('')
        
        style_dict = {
            'Post Impressionism'    : 'weights/best_model-Post_Impressionism.pth',
            'Cubism'                : 'weights/best_model-Cubism.pth',
            'Abstract Expressionism': 'weights/best_model-Abstract_Expressionism.pth',
            'Digital Painting'      : 'weights/best_model-Digital_Painting.pth'
        }
        
        if uploaded is not None and style_btn:
            
            if content_type == 0:
                result_img = inference(
                    content_image=uploaded,
                    checkpoint_model=style_dict[chose_style]
                )
                st.image(result_img, use_container_width=True)
                
                buf = BytesIO()
                Image.fromarray((result_img * 255).astype(np.uint8)).save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button(
                    label="📥 Download Stylized Image",
                    data=byte_im,
                    file_name='styled_image.png',
                    mime="image/png",
                    type="primary"
                )
                
            elif content_type == 1:                    
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    tmp_file.write(uploaded.read())
                    tmp_file_path = tmp_file.name

                fps, length, total_frame, w, h = get_video_info(tmp_file_path)
                with st.status(f"Processing... Please wait about {total_frame * 1/3:.2f} second 😅", expanded=True) as status:
                    output_path = 'styled_video.mp4'
                    result_vid = inference_video(
                        content_video=tmp_file_path,
                        checkpoint_model=style_dict[chose_style],
                        output_path=output_path
                    )
                    status.update(label="**✅ Done!**", state="complete")
                    
                st.video(output_path, muted=True, autoplay=True)
                
                with open(output_path, "rb") as f:
                    video_bytes = f.read()
                    
                st.download_button(
                    label="📥 Download Stylized Video",
                    data=video_bytes,
                    file_name=output_path,
                    mime="video/mp4",
                    type="primary",
                    on_click='ignore'
                )