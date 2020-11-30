import numpy as np

import torch
import torch.nn as nn
from torchvision import models
from torchvision import transforms

import PIL
import cv2

import os
MODELS_DIR = os.path.dirname(__file__)

class BeheadedDenseNet121(nn.Module):
    def __init__(self):
        super().__init__()
        network = models.densenet121(pretrained=True)
        self.model = nn.Sequential(network.features,nn.AvgPool2d(7,stride=1))

        normalize = transforms.Normalize(
           mean=[0.485, 0.456, 0.406],
           std=[0.229, 0.224, 0.225]
        )
        self.prepare = transforms.Compose([
           transforms.Resize(256),
           transforms.CenterCrop(224),
           transforms.ToTensor(),
           normalize
        ])

    def forward(self, x : PIL.Image):
        '''
            x - single image
        '''
        with torch.no_grad():
            e = self.model(self.prepare(x).unsqueeze(0)).squeeze(-1).squeeze(-1)  #  [B, C, 1, 1] -> [B, C]
            return e

    @staticmethod
    def output_embeddings_shape():
        return 1024


class PretrainedHeadOnTLLV1DenseNet121(nn.Module):
    # model pretrained for https://sites.google.com/view/totally-looks-like-dataset
    PRETRAINED_HEAD_ON_TLL_V1_DENSE_NET_121_FILE = 'PretrainedHeadOnTLLV1DenseNet121.weights'
    def __init__(self):
        super().__init__()
        self.head = torch.nn.Sequential(
            torch.nn.Linear(BeheadedDenseNet121.output_embeddings_shape(), 256),
            torch.nn.LeakyReLU(),
            torch.nn.Linear(256, 256),
            torch.nn.LayerNorm(256,elementwise_affine=False)
        )
        self.head.load_state_dict(torch.load(os.path.join(MODELS_DIR, self.PRETRAINED_HEAD_ON_TLL_V1_DENSE_NET_121_FILE)))
        self.model = nn.Sequential(BeheadedDenseNet121(), self.head)

    def forward(self, x : PIL.Image):
        '''
            x - single image
        '''
        with torch.no_grad():
            return self.model(x)

    @staticmethod
    def output_embeddings_shape():
        return 256


def upload_model(model_name : str):
    if model_name == 'BeheadedDenseNet121':
        return BeheadedDenseNet121()
    if model_name == 'PretrainedHeadOnTLL3LayersV1DenseNet121':
        return PretrainedHeadOnTLLV1DenseNet121()
    assert False, 'Set bad model name {}'.format(model_name)


def fix_PIL_img_shape(image: PIL.Image):
    image_arr = np.array(image)
    if len(image_arr.shape) == 2:
        image_arr = np.expand_dims(image_arr, -1)
    if image_arr.shape[-1] == 1:
        image = PIL.Image.fromarray(cv2.cvtColor(image_arr,cv2.COLOR_GRAY2RGB))
    elif image_arr.shape[-1] == 4:
        image = PIL.Image.fromarray(image_arr[:, :, :3])
    elif image_arr.shape[-1] != 3:
        assert False, "Bad image shape: {}".format(image_arr.shape)
    return image


def calc_embed(model : nn.Module, file : str):
    image = PIL.Image.open(file)
    image = fix_PIL_img_shape(image)
    e = model(image).squeeze(0)  # remove batch dim
    return np.array(e.detach())
