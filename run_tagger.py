from image_tagger import WebImageTagger
import os
import argparse

def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='图片标注和管理工具')
    parser.add_argument('--force', '-f', action='store_true', 
                      help='强制重新处理所有图片')
    parser.add_argument('--dir', '-d', type=str,
                      help='指定要处理的图片目录路径（默认为当前目录下的imgs文件夹）')
    
    args = parser.parse_args()
    
    # 如果指定了目录，使用指定的目录，否则使用默认的imgs目录
    if args.dir:
        imgs_dir = os.path.abspath(args.dir)
    else:
        imgs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'imgs')
    
    # 确保目录存在
    if not os.path.exists(imgs_dir):
        os.makedirs(imgs_dir)
        print(f"创建目录: {imgs_dir}")
    
    print(f"开始处理图片目录: {imgs_dir}")
    
    # 初始化标注器
    tagger = WebImageTagger(imgs_dir)
    
    # 处理所有图片
    print("开始标注图片...")
    tagger.tag_all_images(force_update=args.force)
    
    print("标注完成！")
    
    # 显示一些统计信息
    stats = tagger.get_folder_structure()
    print("\n文件夹统计信息:")
    for folder, count in stats.items():
        print(f"{folder}: {count} 张图片")
    
    print("\n提示：如果要查看图片，请进入web目录并运行 'python -m flask run'")

if __name__ == "__main__":
    main()
