from torch.utils import data
import torch
import numpy as np

import PIL

import glob
from random import sample

class Cloud_Data(data.Dataset):

    def __init__(self, class_names, root, image_type='voc', image_set='train', backbone='resnet', transform=False):
        self.image_type = image_type
        self.class_names = class_names
        self._transform = transform
        self.backbone = backbone
        self.image_set = image_set

        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])


        ## images  labels
        image = glob.glob(root+'images/*')
        lbl = glob.glob(root+'labels/*')

        tnum = [i for i in range(len(image))]
        tdata = int(len(image)*0.8)
        tsample = sample(tnum, tdata)


        train = []
        val = []
        for i in tnum:
            if i in tsample:
                train.append(image[i])
            else:
                val.append(image[i])


        self.files = {'train': train, 'val': val, 'lbl':lbl}

    def __len__(self):
        return len(self.files[self.image_set])

    def __getitem__(self, index):
        data_file = self.files[self.image_set][index]
        #load image
        img_file = data_file
        img = PIL.Image.open(img_file)
        img = np.array(img, dtype=np.float64)

        #img = img.transpose(2, 0, 1)
        #load label
        key = img_file.split('/')[-1].split('.')[0]

        def find_lbl():
            for item in self.files['lbl']:
                if key in item:
                   return item

        lbl_file = find_lbl()
        lbl = PIL.Image.open(lbl_file).convert('P')
        lbl = np.array(lbl, dtype=np.int32)


        if self.image_type == 'waggle_cloud':
            lbl[lbl <= 175] = 0
            lbl[lbl > 175] = 1
        elif self.image_type == 'voc' or self.image_type == 'cityscape':
            lbl[lbl == 255] = -1
        else:
            raise Exception('data_loader for this image type is not ready')

        #lbl[lbl == 255] = 2
        #lbl[lbl == 255] = 254

        if self._transform:
            return self.transform(img,lbl)
        else:
            return img, lbl


    def transform(self, img, lbl):
        img = np.array(img, dtype=np.float64)
        img /= 255.
        lbl = np.array(lbl, dtype=np.float64)
        lbl[lbl == 255] = -1  # Ignore contour
        img -= self.mean
        img /= self.std
        img = img.transpose(2, 0, 1)
        img = torch.from_numpy(img).float()
        lbl = torch.from_numpy(lbl).long()
        return img, lbl

    def untransform(self, img, lbl):
        img = img.numpy()
        img = img.transpose(1, 2, 0)
        img *= self.std
        img += self.mean

        img *= 255
        img = img.astype(np.uint8)
        lbl = lbl.numpy()

        return img, lbl

