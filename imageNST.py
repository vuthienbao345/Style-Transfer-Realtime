import torch
from PIL import Image
from tqdm import tqdm

from setting import DEVICE
from utils import load_image, plot_image
from model import TransferLoss, VGG19_FeatureExtractor

def NST_image(content_img_path, style_img_path, output_path, extractor, transfer_loss_fn, target_size='same', steps=500, lr=0.05):
    
    if target_size == 'same':
        target_shape = Image.open(content_img_path).size # W x H
        content_img  = load_image(content_img_path, size=(target_shape[1], target_shape[0])) # H x W
        style_img    = load_image(style_img_path  , size=(target_shape[1], target_shape[0]))
    elif isinstance(target_size, tuple): 
        content_img = load_image(content_img_path, size=target_size)
        style_img   = load_image(style_img_path, size=target_size)
    else:
        print('Wrong size!')
        return
    
    content_features = extractor(content_img)
    style_features   = extractor(style_img)
    
    target_img = content_img.clone().requires_grad_(True).to(DEVICE)
    # optimizer  = torch.optim.AdamW([target_img], lr=lr)
    optimizer  = torch.optim.LBFGS([target_img], lr=lr)
    
    # Start style transfer
    with tqdm(total=steps, desc='Processing Image', unit='step') as pbar:
        
        def closure():
            optimizer.zero_grad()
            target_features = extractor(target_img)
            transfer_loss   = transfer_loss_fn(content_features, style_features, target_features)
            transfer_loss.backward()
            return transfer_loss
        
        for step in range(1, steps + 1):
            optimizer.step(closure)
            
            # Print log
            # C, S, T = transfer_loss_fn.get_loss()
            # print(f"STEP [{step}/{steps}] \t| Content Loss: {C:.6f} \t| Style Loss {S:.6f} \t| Total loss: {T:.8f}")

            # Plot image
            if step == 1 or step % 20 == 0:
                if step == steps:
                    plot_image(target_img, f"Target Image", save=True, save_path=output_path)
                    print('Target Image saved!')
                else:
                    plot_image(target_img, f"Target Image at step {step}")

            # Update pbar
            pbar.update(1)
    print('Done!')
            
if __name__ == '__main__':
    # Extractor and Loss Funcntion
    extractor        = VGG19_FeatureExtractor()
    transfer_loss_fn = TransferLoss(content_weight=1, style_weight=1e5)
    transfer_loss_fn.to(DEVICE)

    # NST
    NST_image(
        content_img_path='resources/images/content_img.png', 
        style_img_path='resources/styles/style1.png', 
        output_path='results/transfered_img.png', 
        extractor=extractor, 
        transfer_loss_fn=transfer_loss_fn, 
        target_size=(256,256),
        steps=50, 
        lr=0.02
    )