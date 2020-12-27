
import torch
from thsr_ticket.ml.model import CNN
from torchvision import transforms as T
import numpy as np  
def solve_captcha(image, model_path, use_gpu = False):
    """!!! Useless !!!
    """
    model = CNN()
    model.load(model_path)
    if use_gpu: model.cuda()
    else:
        device = torch.device("cpu")
        model.to(device)
    char_table = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    # 把模型设为验证模式
    
    # transforms = T.Compose([
    #         T.Resize((128,128)),
    #         T.ToTensor(),
    #     ])

    data = transforms(image).unsqueeze(dim=0)
    model.eval()
    with torch.no_grad():
        if use_gpu:
            data = data.cuda()
        else:
            device = torch.device("cpu")
            data = data.to(device)
        score = model(data)
        score = decode(score)
        score = ''.join(map(lambda i: char_table[i], score[0]))
        return score

#處理image資料
def transforms(image):
  print('transforms')
  data = image.convert('L')
  transforms = T.Compose([
    T.Resize((128,128)),
    T.ToTensor(),
  ])
  data = transforms(data)
  return data
def decode(scores):
    """Decode the CNN output.

    Args:
        scores (tensor): CNN output.

    Returns:
        list(int): list include each digit index.
    """
    tmp = np.array(tuple(map(lambda score: score.cpu().numpy(), scores)))
    tmp = np.swapaxes(tmp, 0, 1)
    return (np.argmax(tmp, axis=2))