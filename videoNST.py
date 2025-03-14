import os
import torch
import cv2
from tqdm import tqdm

from setting import DEVICE
from utils import load_image, preprocess_frame, postprocess_frame
from model import TransferLoss, VGG19_FeatureExtractor

def NST_frame(content_img, style_features, extractor, transfer_loss_fn, steps=100, lr=0.01):
    target_img = content_img.clone().requires_grad_(True).to(DEVICE)
    # optimizer  = torch.optim.LBFGS([target_img], lr=lr)
    optimizer = torch.optim.AdamW([target_img], lr=lr)

    content_features = extractor(content_img)

    # def closure():
    #     optimizer.zero_grad()
    #     target_features = extractor(target_img)
    #     transfer_loss   = transfer_loss_fn(content_features, style_features, target_features)
    #     transfer_loss.backward()
    #     return transfer_loss

    for i in range(steps):
        # optimizer.step(closure)
        optimizer.zero_grad()
        target_features = extractor(target_img)
        transfer_loss   = transfer_loss_fn(content_features, style_features, target_features)
        transfer_loss.backward()
        optimizer.step()

    return target_img

def NST_video(video_path, style_img_path, output_path, extractor, transfer_loss_fn, target_size='same', target_fps=10, steps_per_frame=100, lr=0.01):
    cap = cv2.VideoCapture(video_path)
    
    # Set size
    if target_size == 'same':
        target_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                       int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    elif isinstance(target_size, tuple):
        target_size = target_size
    else:
        print('Wrong size!')
        return

    # Downsample fps (optional)
    fps         = int(cap.get(cv2.CAP_PROP_FPS))
    frame_skip  = max(1, fps // target_fps)
    total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Writer for saving ouput video  
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec
    out    = cv2.VideoWriter(output_path, fourcc, target_fps, target_size)

    # Get features
    style_img      = load_image(style_img_path, size=(target_size[1], target_size[0]))
    style_features = extractor(style_img)

    # Start style transfer
    with tqdm(total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT) // frame_skip), desc='Processing Video', unit='frame') as pbar:
        frame_cnt = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_cnt % frame_skip == 0:
                # Process
                content_img = preprocess_frame(frame, size=(target_size[1], target_size[0]))
                
                target_img = NST_frame(
                    content_img, style_features,
                    extractor, transfer_loss_fn,
                    steps=steps_per_frame, lr=lr
                )
                
                output_frame = postprocess_frame(target_img)
                out.write(output_frame)
    
                # Update pbar
                pbar.update(1)

            frame_cnt += 1
        
    # Release
    cap.release()
    out.release()
    print('Done!')
    
if __name__ == '__main__':
    os.makedirs('results', exist_ok=True)
    
    # Extractor and Loss Funcntion
    extractor        = VGG19_FeatureExtractor()
    transfer_loss_fn = TransferLoss(content_weight=1, style_weight=1e5)
    transfer_loss_fn.to(DEVICE)

    # NST
    NST_video(
        video_path='resources/videos/content_vid_2s.mp4',
        style_img_path='resources/styles/style1.png',
        output_path='results/transfered_vid.mp4',
        extractor=extractor,
        transfer_loss_fn=transfer_loss_fn,
        target_size=(1280,720), # W, H
        target_fps=10,
        steps_per_frame=50,
        lr=0.02
    )