import torch
import torch.nn as nn
from torchvision.models import vgg19, VGG19_Weights

from setting import DEVICE

class TransferLoss(nn.Module):
    def __init__(self, content_weight=1, style_weight=1e6):
        super().__init__()

        self.content_weight = content_weight
        self.style_weight   = style_weight

        self.content_layer = 'conv2_1'
        self.style_layers  = ['conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1']

        self.loss_fn = nn.MSELoss()

    def _gram_matrix(self, tensor): # Case: batch_size=1
        B, C, H, W = tensor.size()
        tensor     = tensor.view(B * C, H * W)
        G          = torch.mm(tensor, tensor.t())
        return G.div(B * C * H * W)

    def forward(self, content_features, style_features, target_features):
        self.content_loss = self.loss_fn(content_features[self.content_layer],
                                         target_features[self.content_layer])
        
        self.style_loss = sum(
            self.loss_fn(self._gram_matrix(style_features[layer]),
                         self._gram_matrix(target_features[layer]))
            for layer in self.style_layers
        )

        self.total_loss = self.content_weight * self.content_loss + self.style_weight * self.style_loss
        return self.total_loss

    def get_loss(self):
        return self.content_loss, self.style_loss, self.total_loss
    
    
class VGG19_FeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()

        self.model = vgg19(weights=VGG19_Weights.DEFAULT).features.eval()
        self.model.to(DEVICE)
        for param in self.model.parameters():
            param.requires_grad_(False)

        # self.layers = {'0': 'conv1_1', '5': 'conv2_1', '10': 'conv3_1', '19': 'conv4_1', '21': 'conv4_2', '28': 'conv5_1'}
        self.layers = {'0': 'conv1_1', '5': 'conv2_1', '10': 'conv3_1', '19': 'conv4_1', '28': 'conv5_1'}
        
    def forward(self, x):
        features = {}
        for idx, layer in self.model._modules.items():
            x = layer(x.to(DEVICE))
            if idx in self.layers:
                features[self.layers[idx]] = x
        return features