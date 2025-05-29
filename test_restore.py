import torch
from torchvision import transforms
from PIL import Image
import os
from model.Model import SimpleAutoencoder 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SimpleAutoencoder().to(device)
model.load_state_dict(torch.load("model2a.pth", map_location=device))
model.eval()

img_path = "./data/testimg/22332.jpg" #Сюда подгрузить изображение, которое загрузили в gui_app.py вместо єтого пути
img = Image.open(img_path).convert("RGB")
transform = transforms.ToTensor()
input_tensor = transform(img).unsqueeze(0).to(device) 


with torch.no_grad():
    output = model(input_tensor)


output_img = transforms.ToPILImage()(output.squeeze(0).cpu())
output_img.save("restored/restored4a.jpg") #вместо єтой команді тоже надо віполнять сохранение через gui_app.py 
print("saved as restored4a.jpg")

