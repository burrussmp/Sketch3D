import numpy as np
import cv2
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import TensorDataset, Dataset, DataLoader
import math
import torchvision.models as models
from torchvision import transforms
from matplotlib import pyplot as plt
from skimage import color
import torch.nn.functional as F
from torch.autograd import Variable
import scipy.ndimage as ndimage
from scipy import stats
from collections import Counter

__acceptable_codes__ = ['U','R','G','B','S','H','C']
threshold = 75 # we need more than 15 pixels to consider valid 
def process_mask(mask):
    valid_masks = []
    predictions = []
    non_zero_values = mask[mask!=0].flatten()
    for code in __acceptable_codes__:
        total_occurrences = np.sum(non_zero_values == ord(code)-64)
        if total_occurrences > threshold:
            new_mask = np.copy(mask)
            new_mask[mask!=ord(code)-64] = 0
            new_mask[mask==ord(code)-64] = 1
            valid_masks.append(new_mask)
            predictions.append(code)
    return valid_masks,predictions

class DoubleConv2D(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool2d(2),
            DoubleConv2D(in_channels, out_channels)
        )

    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels, out_channels, bilinear=True):
        super().__init__()

        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_channels // 2, in_channels // 2, kernel_size=2, stride=2)

        self.conv = DoubleConv2D(in_channels, out_channels)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # input is CHW
        diffY = torch.tensor([x2.size()[2] - x1.size()[2]])
        diffX = torch.tensor([x2.size()[3] - x1.size()[3]])

        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2])
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)

class UNet2D(nn.Module):
  def __init__(self, n_channels=1, n_classes=27, bilinear=True):
    super(UNet2D, self).__init__()
    self.n_channels = n_channels
    self.n_classes = n_classes
    self.bilinear = bilinear
    self.inc = DoubleConv2D(n_channels, 64)
    self.down1 = Down(64, 128)
    self.down2 = Down(128, 256)
    self.down3 = Down(256, 512)
    self.down4 = Down(512, 512)
    self.up1 = Up(1024, 256, bilinear)
    self.up2 = Up(512, 128, bilinear)
    self.up3 = Up(256, 64, bilinear)
    self.up4 = Up(128, 64, bilinear)
    self.outc = OutConv(64, n_classes)
    self.final = nn.Sigmoid()

  def forward(self, x):
      x1 = self.inc(x)
      x2 = self.down1(x1)
      x3 = self.down2(x2)
      x4 = self.down3(x3)
      x5 = self.down4(x4)
      x = self.up1(x5, x4)
      x = self.up2(x, x3)
      x = self.up3(x, x2)
      x = self.up4(x, x1)
      x = self.outc(x)
      logits = self.final(x)
      return logits

def generate_model(pathToModel='./'):
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    model = UNet2D()
    if use_cuda:
        model.cuda()
    model.load_state_dict(torch.load(pathToModel,'cpu'))
    model.eval()
    return model
    
def predict_segmentation(model,img,typeOfImage):
    use_cuda = torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")
    with torch.no_grad():
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_resized = cv2.resize(gray,(128,128),interpolation=cv2.INTER_AREA)/ 255.
        gray_expanded = np.expand_dims(gray_resized,axis=0)
        data = torch.unsqueeze(torch.tensor(gray_expanded),axis=0).to(device)
        output = model(data.float())
        if use_cuda:
            prediction = np.squeeze(output.max(1)[1].type(torch.int32).cpu().data.numpy())
        else:
            prediction = np.squeeze(output.max(1)[1].type(torch.int32).data.numpy())
        valid_masks,predictions = process_mask(prediction)
        isAcceptable = False
        pop_me = []
        for i in range(len(valid_masks)):
            plt.imshow(valid_masks[i],cmap='gray')
            plt.title('Predicted Letter:' + predictions[i])
            plt.show(block = False)
            isAcceptable = input('Enter Y if the segmentation is correct for the '+typeOfImage+'?\t\t').lower() == 'y'
            plt.close()
            if not isAcceptable:
                pop_me.append(i)
        valid_masks = np.delete(np.array(valid_masks),pop_me,axis=0)
        predictions = np.delete(np.array(predictions),pop_me,axis=0)
        return valid_masks,predictions


# PLAYGROUND TO TEST SEGMENTATION
"""
typeOfImage= 'Side'
model = generate_model(pathToModel='./weights2.pt')
img = cv2.imread('./ExampleSketches/test1.jpg')
use_cuda = torch.cuda.is_available()
device = torch.device("cuda" if use_cuda else "cpu")
with torch.no_grad():
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_resized = cv2.resize(gray,(128,128),interpolation=cv2.INTER_AREA)/ 255.
    #gray_resized = change_brightness(gray_resized,100)
    #gray_resized[gray_resized<0.3] = 0
    gray_expanded = np.expand_dims(gray_resized,axis=0)
    data = torch.unsqueeze(torch.tensor(gray_expanded),axis=0).to(device)
    output = model(data.float())
    if use_cuda:
        prediction = np.squeeze(output.max(1)[1].type(torch.int32).cpu().data.numpy())
    else:
        prediction = np.squeeze(output.max(1)[1].type(torch.int32).data.numpy())
    valid_masks,predictions = process_mask(prediction)
    isAcceptable = False
    for i in range(len(valid_masks)):
        plt.imshow(valid_masks[i],cmap='gray')
        plt.title('Predicted Letter:' + predictions[i])
        plt.show(block = False)
        isAcceptable = input('Enter Y if the segmentation is correct for the '+typeOfImage+'?\t\t').lower() == 'y'
        plt.close()
        if not isAcceptable:
            break 
"""

# PLAYGROUND TO TEST CORNER FINDER
"""
import numpy as np
import cv2
import matplotlib.pyplot as plt

def calculate_hull(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    # gray = (gray*255).astype(np.uint8)
    # canny_edge = cv2.Canny(gray,75,200)
    # plt.imshow(canny_edge)
    # plt.show()
    corners = cv2.goodFeaturesToTrack(gray, 5, 0.1, 5)
    corners = np.int0(corners)
    hull = cv2.convexHull(corners)
    return hull


img = cv2.imread('./Front.png')
img = cv2.resize(img,(128,128),interpolation=cv2.INTER_AREA)
hull = calculate_hull(img)
cpy_img = np.copy(img)
for i in range(hull.shape[0]):
    radius = 2
    x = hull[i,0,0]
    y = hull[i,0,1]
    cv2.circle(cpy_img,(x,y), radius, (0,255,0), -1)

plt.imshow(cpy_img)
plt.show()
"""