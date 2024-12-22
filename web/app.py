from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os

# 初始化 Flask 应用
app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# 加载图片数据
IMGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'imgs')
print(f"\n图片目录: {IMGS_DIR}")

try:
    # 修正：从 imgs 目录加载 web_image_tags.json
    with open(os.path.join(IMGS_DIR, 'web_image_tags.json'), 'r', encoding='utf-8') as f:
        image_data = json.load(f)
    print(f"成功加载图片数据，共 {len(image_data)} 条记录")
    # 打印前三条记录的路径示例
    paths = list(image_data.keys())[:3]
    print("示例图片路径:")
    for path in paths:
        print(f"- {path}")
        print(f"  完整路径: {os.path.join(IMGS_DIR, path)}")
        print(f"  文件存在: {os.path.exists(os.path.join(IMGS_DIR, path))}")
except Exception as e:
    print(f"加载图片数据时出错: {str(e)}")
    image_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/images')
def get_images():
    # 获取查询参数
    category = request.args.get('category', '')
    search = request.args.get('search', '').lower()
    
    print(f"\n获取图片请求 - 类别: {category}, 搜索: {search}")
    print(f"图片数据库中的记录数: {len(image_data)}")
    
    # 过滤图片
    filtered_images = []
    for path, info in image_data.items():
        try:
            # 检查文件是否存在
            full_path = os.path.join(IMGS_DIR, path)
            print(f"\n处理图片: {path}")
            print(f"完整路径: {full_path}")
            
            if not os.path.exists(full_path):
                print(f"警告：文件不存在 {full_path}")
                continue
                
            # 检查类别
            folder_categories = info.get('folder_categories', [])
            print(f"图片类别: {folder_categories}")
            
            if category and category not in folder_categories:
                print(f"类别不匹配，跳过")
                continue
                
            # 检查搜索词（同时搜索路径和 AI 标签）
            if search:
                path_match = search in path.lower()
                ai_tags = [tag['label'].lower() for tag in info.get('ai_tags', [])]
                tags_match = any(search in tag for tag in ai_tags)
                if not (path_match or tags_match):
                    print(f"搜索词不匹配，跳过")
                    continue
            
            # 构建图片信息
            image_info = {
                'path': path.replace('\\', '/'),  # 确保使用正斜杠
                'categories': folder_categories,
                'technical': info.get('technical', {}),
                'ai_tags': info.get('ai_tags', []),
                'composition': info.get('composition', {}),
                'color': info.get('color', [])
            }
            print(f"添加图片: {image_info['path']}")
            filtered_images.append(image_info)
            
        except Exception as e:
            print(f"处理图片 {path} 时出错: {str(e)}")
            continue
    
    print(f"\n返回 {len(filtered_images)} 张图片")
    if filtered_images:
        print(f"示例图片信息:\n{json.dumps(filtered_images[0], indent=2, ensure_ascii=False)}")
    
    return jsonify(filtered_images)

@app.route('/api/categories')
def get_categories():
    # 收集所有唯一的类别
    categories = set()
    for info in image_data.values():
        categories.update(info.get('folder_categories', []))
    return jsonify(list(categories))

@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        # 将 URL 路径分隔符统一转换为操作系统路径分隔符
        filename = filename.replace('/', os.path.sep).replace('\\', os.path.sep)
        
        # 构建完整路径
        full_path = os.path.join(IMGS_DIR, filename)
        directory = os.path.dirname(full_path)
        basename = os.path.basename(full_path)
        
        print(f"\n请求图片: {filename}")
        print(f"完整路径: {full_path}")
        print(f"目录: {directory}")
        print(f"文件名: {basename}")
        print(f"文件是否存在: {os.path.exists(full_path)}")
        
        if not os.path.exists(full_path):
            print(f"错误：图片不存在 {full_path}")
            # 返回占位图片
            return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'placeholder.png')
            
        print(f"提供图片服务: {directory} -> {basename}")
        return send_from_directory(directory, basename)
    except Exception as e:
        print(f"服务图片时出错: {str(e)}")
        # 发生错误时也返回占位图片
        return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'placeholder.png')

if __name__ == '__main__':
    app.run(debug=True)
