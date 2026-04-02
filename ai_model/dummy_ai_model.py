
# dummy_ai_model.py
# Simple PyTorch model to classify images into 3 dummy classes

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
import torchvision.transforms as transforms

class DummyAIModel(nn.Module):
    def __init__(self):
        super(DummyAIModel, self).__init__()
        self.fc = nn.Linear(64*64*3, 3)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return F.softmax(x, dim=1)

# function to simulate prediction
def predict(image_path):
    transform = transforms.Compose([transforms.Resize((64,64)),
                                    transforms.ToTensor()])
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)
    model = DummyAIModel()
    with torch.no_grad():
        output = model(image)
    prob, label_idx = torch.max(output, 1)
    labels = ["Product A", "Product B", "Product C"]
    return labels[label_idx.item()], float(prob.item())
