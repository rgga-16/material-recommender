import os , torch 

CWD = os.getcwd()
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
