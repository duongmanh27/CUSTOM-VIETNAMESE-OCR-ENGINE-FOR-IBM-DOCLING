import cv2
import torch
import numpy as np
import os
from PIL import Image
from torchvision import transforms

from ocr_text.model_ocr import CRNN_ResNet
from config import *
from utils import StrLabelConverter, VIETNAMESE_ALPHABET


class OCRPredictor(object):
    def __init__(self):
        self.checkpoint_path = os.path.join(folder_weight, "weight_ocr_text/weight_ocr_text.pth")

        self.imgH = 32
        self.n_hidden = 256
        self.alphabets = VIETNAMESE_ALPHABET
        self.nclass = len(self.alphabets) + 1
        self.converter = StrLabelConverter(self.alphabets)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = CRNN_ResNet(nc=1, nclass=self.nclass, nh=self.n_hidden)
        self.model.to(self.device)

        self.checkpoint = torch.load(self.checkpoint_path, map_location=self.device)

        if isinstance(self.checkpoint, dict) and 'model' in self.checkpoint:
            self.state_dict = self.checkpoint['model']
        else:
            self.state_dict = self.checkpoint

        self.model.load_state_dict(self.state_dict)
        self.model.eval()

    def predict_crnn(self, image_input):
        if isinstance(image_input, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB)).convert('L')
        else:
            raise ValueError("Hàm này trong pipeline nhận đầu vào là numpy array (crop từ cv2)")

        image = self.transform_image(image)
        image = image.unsqueeze(0).to(self.device)

        with torch.no_grad():
            preds = self.model(image)

        _, preds_index = preds.max(2)
        preds_index = preds_index.transpose(1, 0).contiguous()

        pred_str = self.converter.decode(preds_index.view(-1), torch.IntTensor([preds_index.size(1)]), raw=False)

        if isinstance(pred_str, list):
            pred_str = pred_str[0]

        pred_str = pred_str.replace("#", "/")

        return pred_str if pred_str else ""

    def transform_image(self, img, interpolation=Image.BILINEAR):
        w, h = img.size
        new_w = max(64, int(w * (self.imgH / h)))
        img = img.resize((new_w, self.imgH), interpolation)
        img = transforms.ToTensor()(img)
        img = img.sub_(0.5).div_(0.5)
        return img