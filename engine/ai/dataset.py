import torch
from torch.utils.data import Dataset

DEVICE=torch.device("cuda" if torch.cuda.is_available() else "cpu")
GOBAN_SIZE=19

class MyDataset(Dataset):
    def __init__(self,datas):
        super(MyDataset,self).__init__()
        self.datas=datas

    def __len__(self):
        return len(self.datas)

    def __getitem__(self,item):
        data=self.datas[item]
        return data