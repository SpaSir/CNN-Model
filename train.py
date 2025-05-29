import os
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
from model.Model import SimpleAutoencoder # Імпортуємо нашу модель автокодера
from torchvision import transforms

class InpaintingDataset(Dataset):
    """
    Клас для завантаження даних для завдання "зафарбовування" (inpainting).
    Він надає доступ до пар зображень: замасковане (з прогалинами) та оригінальне.
    """
    def __init__(self, masked_dir, original_dir):
        # Отримуємо відсортовані списки файлів з маскованими та оригінальними зображеннями
        self.masked_paths = sorted(os.listdir(masked_dir))
        self.original_paths = sorted(os.listdir(original_dir))
        # Зберігаємо шляхи до директорій
        self.masked_dir = masked_dir
        self.original_dir = original_dir
        # Визначаємо трансформацію для перетворення зображень у тензори PyTorch
        self.transform = transforms.ToTensor()

    def __len__(self):
        """
        Повертає загальну кількість елементів у наборі даних.
        """
        return len(self.masked_paths)

    def __getitem__(self, idx):
        """
        Повертає пару зображень за заданим індексом: замасковане та оригінальне.
        """
        # Відкриваємо замасковане зображення та конвертуємо його в RGB
        masked = Image.open(os.path.join(self.masked_dir, self.masked_paths[idx])).convert("RGB")
        # Відкриваємо оригінальне зображення та конвертуємо його в RGB
        original = Image.open(os.path.join(self.original_dir, self.original_paths[idx])).convert("RGB")
        # Застосовуємо трансформацію та повертаємо тензори
        return self.transform(masked), self.transform(original)

# Визначаємо пристрій, на якому буде працювати модель (GPU, якщо доступно, інакше CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Використовується пристрій: {device}")

# Ініціалізуємо нашу модель автокодера та переміщуємо її на обраний пристрій
model = SimpleAutoencoder().to(device)

# Створюємо екземпляр нашого набору даних
dataset = InpaintingDataset("./data/masked", "./data/images")
# Створюємо DataLoader для ефективної завантаження даних пакетами
# batch_size=64: обробляти 64 зображення за раз
# shuffle=True: перемішувати дані на кожній епосі для кращого навчання
loader = DataLoader(dataset, batch_size=64, shuffle=True)

# Визначаємо оптимізатор Adam для оновлення ваг моделі
# lr=1e-3: швидкість навчання
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
# Визначаємо функцію втрат: Середньоквадратична похибка (MSE)
# Вона вимірює різницю між виходом моделі та оригінальним зображенням
loss_fn = torch.nn.MSELoss()

# Цикл навчання моделі
# Модель буде тренуватися протягом 25 епох
for epoch in range(25):
    total_loss = 0 # Змінна для відстеження сумарних втрат за поточну епоху
    # Ітеруємося по пакетах даних з DataLoader'а
    for masked, original in loader:
        # Переміщуємо дані на обраний пристрій (GPU/CPU)
        masked, original = masked.to(device), original.to(device)
        
        # Виконуємо прямий прохід: отримуємо вихід моделі для замаскованих зображень
        output = model(masked)
        # Обчислюємо втрати між виходом моделі та оригінальними зображеннями
        loss = loss_fn(output, original)

        # Обнуляємо градієнти перед зворотним проходом
        optimizer.zero_grad()
        # Виконуємо зворотний прохід (backpropagation) для обчислення градієнтів
        loss.backward()
        # Оновлюємо ваги моделі на основі обчислених градієнтів
        optimizer.step()
        
        # Додаємо поточні втрати до сумарних втрат епохи
        total_loss += loss.item()

    # Виводимо середні втрати за поточну епоху
    print(f"Epoch {epoch+1} - Loss: {total_loss / len(loader):.4f}")

# Зберігаємо стан моделі (ваги) після завершення навчання
torch.save(model.state_dict(), "model2a.pth")
print("Навчання завершено. Модель збережено як model2a.pth")