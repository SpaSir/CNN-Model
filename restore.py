import torch
from torchvision import transforms
from PIL import Image
import sys
from model.Model import SimpleAutoencoder # Імпортуємо нашу модель автокодера

# Визначаємо пристрій для обчислень (GPU, якщо доступно, інакше CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Використовується пристрій: {device}")

# Ініціалізуємо модель автокодера
model = SimpleAutoencoder().to(device)
# Завантажуємо попередньо навчені ваги моделі
# map_location=device гарантує, що модель завантажиться на правильний пристрій
model.load_state_dict(torch.load("model2a.pth", map_location=device))
# Переводимо модель у режим оцінки (відключаємо розрахунок градієнтів, dropout тощо)
model.eval()

# Отримання шляхів до вхідного та вихідного файлів з аргументів командного рядка
# sys.argv[0] - це ім'я скрипта, sys.argv[1] - перший аргумент, sys.argv[2] - другий
img_path = sys.argv[1]  # Шлях до зображення, яке потрібно відновити (від GUI)
output_path = sys.argv[2] # Шлях, куди зберегти відновлене зображення

# Відкриваємо вхідне зображення, конвертуємо його в RGB та змінюємо розмір до 64x64 пікселів
img = Image.open(img_path).convert("RGB").resize((64, 64))  # Фіксований розмір для моделі
# Визначаємо трансформацію для перетворення зображення у тензор PyTorch
transform = transforms.ToTensor()
# Перетворюємо зображення на тензор, додаємо вимір для пакету (unsqueeze(0))
# та переміщуємо його на обраний пристрій
input_tensor = transform(img).unsqueeze(0).to(device)

# Виконуємо інференс (прогноз) без обчислення градієнтів
# torch.no_grad() зменшує споживання пам'яті та прискорює обчислення
with torch.no_grad():
    # Пропускаємо вхідний тензор через модель для отримання відновленого зображення
    output = model(input_tensor)

# Перетворюємо вихідний тензор моделі назад у зображення PIL
# Squeeze(0) видаляє вимір пакету, cpu() переміщує тензор на CPU для обробки PIL
output_img = transforms.ToPILImage()(output.squeeze(0).cpu())
# Зберігаємо відновлене зображення за вказаним шляхом
output_img.save(output_path)
print(f"Збережено до: {output_path}")