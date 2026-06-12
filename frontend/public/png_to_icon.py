from PIL import Image

def convert_png_to_ico(source_path, target_path):
    try:
        # 1. 打开原始 PNG 图片
        img = Image.open(source_path)
        
        # 2. 定义你想包含的多尺寸列表
        # ICO 标准通常包含 16, 32, 48, 256 等
        sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
        
        # 3. 保存为 ico 格式
        # icon_sizes 参数会告诉 Pillow 自动缩放并打包这些尺寸
        img.save(target_path, format='ICO', sizes=sizes)
        
        print(f"成功！已将 {source_path} 转换为包含多尺寸的 {target_path}")
        
    except Exception as e:
        print(f"转换失败: {e}")

# --- 使用示例 ---
if __name__ == "__main__":
    # 请确保当前目录下有 icon.png，或者填写绝对路径
    source_file = "icon.png"
    target_file = "icon.ico"
    
    convert_png_to_ico(source_file, target_file)