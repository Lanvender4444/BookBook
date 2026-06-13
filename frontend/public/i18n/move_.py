import os

# 获取当前目录下的所有文件和文件夹
for item in os.listdir('.'):
    # 检查是否以"_"开头
    if item.startswith('_'):
        # 构造新文件名（去掉开头的"_"）
        new_name = item[1:]
        
        # 检查目标文件名是否已存在，避免覆盖
        if os.path.exists(new_name):
            print(f"跳过: '{item}' -> 目标文件名 '{new_name}' 已存在")
            continue
        
        # 重命名文件/文件夹
        os.rename(item, new_name)
        print(f"重命名: '{item}' -> '{new_name}'")