import os
import json
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import numpy as np
from datetime import datetime

class WebImageTagger:
    def __init__(self, image_dir):
        self.image_dir = image_dir
        self.db_file = os.path.join(image_dir, 'web_image_tags.json')
        
        # 加载CLIP模型
        print("正在加载AI视觉模型...")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # 加载标签数据库
        self.tags_db = self._load_db()
        
        # 定义建筑相关的标签列表（中英文对照）
        self.architecture_tags = [
            "建筑外观 exterior", "建筑立面 facade", "建筑细节 architectural detail",
            "室内空间 interior space", "办公空间 office space", "居住空间 living space",
            "景观设计 landscape design", "公共空间 public space", "展览空间 exhibition space",
            "建筑透视 perspective", "鸟瞰视图 aerial view", "夜景 night view",
            "现代建筑 modern architecture", "古典建筑 classical architecture",
            "工业风格 industrial style", "极简主义 minimalist", "后现代 postmodern",
            "绿色建筑 green building", "可持续设计 sustainable design",
            "采光设计 lighting design", "空间布局 spatial layout"
        ]
        
        # 定义场景描述标签
        self.scene_tags = [
            "城市景观 urban landscape", "自然环境 natural environment",
            "商业空间 commercial space", "文化场所 cultural space",
            "教育设施 educational facility", "交通枢纽 transportation hub",
            "休闲场所 leisure space", "运动场馆 sports venue",
            "医疗设施 healthcare facility", "住宅区 residential area"
        ]
        
        # 定义建筑元素标签
        self.element_tags = [
            "玻璃幕墙 glass curtain wall", "钢结构 steel structure",
            "混凝土 concrete", "木材 wood", "石材 stone",
            "金属饰面 metal finish", "绿植 plants", "水景 water feature",
            "采光顶 skylight", "露台 terrace", "庭院 courtyard",
            "栏杆 railing", "楼梯 staircase", "门窗 windows and doors"
        ]

    def _load_db(self):
        """加载或创建标签数据库"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载数据库出错: {e}")
                return {}
        return {}

    def _save_db(self):
        """保存标签数据库"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.tags_db, f, ensure_ascii=False, indent=2)

    def analyze_image(self, image_path):
        """使用AI模型分析图片内容"""
        try:
            # 加载图片
            image = Image.open(image_path)
            
            # 准备所有标签
            all_tags = self.architecture_tags + self.scene_tags + self.element_tags
            
            # 使用CLIP模型分析图片
            inputs = self.processor(
                images=image,
                text=all_tags,
                return_tensors="pt",
                padding=True
            )
            
            # 获取图片和文本特征
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1).detach().numpy()[0]
            
            # 选择置信度高于阈值的标签
            threshold = 0.1  # 降低阈值，让更多标签被选中
            selected_tags = []
            for tag, prob in zip(all_tags, probs):
                if prob > threshold:
                    selected_tags.append({
                        'label': tag,
                        'probability': float(prob)
                    })
            
            # 按置信度排序
            selected_tags.sort(key=lambda x: x['probability'], reverse=True)
            
            # 返回更多标签（从10个增加到20个）
            return selected_tags[:20]  # 返回前20个最相关的标签
            
        except Exception as e:
            print(f"分析图片时出错: {e}")
            return []

    def get_folder_structure(self):
        """获取文件夹结构统计信息"""
        stats = {}
        for path in self.tags_db:
            folder = os.path.dirname(path)
            if folder in stats:
                stats[folder] += 1
            else:
                stats[folder] = 1
        return stats

    def tag_all_images(self, force_update=False):
        """处理目录下的所有图片"""
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        
        # 遍历目录
        for root, _, files in os.walk(self.image_dir):
            for filename in files:
                # 检查文件扩展名
                if os.path.splitext(filename)[1].lower() in image_extensions:
                    # 获取相对路径
                    rel_path = os.path.relpath(os.path.join(root, filename), self.image_dir)
                    
                    # 检查是否需要处理这个文件
                    if not force_update and rel_path in self.tags_db:
                        continue
                    
                    print(f"正在处理: {rel_path}")
                    
                    try:
                        # 获取图片完整路径
                        image_path = os.path.join(root, filename)
                        
                        # 分析图片
                        ai_tags = self.analyze_image(image_path)
                        
                        # 获取图片基本信息
                        with Image.open(image_path) as img:
                            width, height = img.size
                            
                        # 更新数据库
                        self.tags_db[rel_path] = {
                            'ai_tags': ai_tags,
                            'technical': {
                                'width': width,
                                'height': height,
                                'aspect_ratio': round(width/height, 2)
                            },
                            'folder_categories': [os.path.basename(os.path.dirname(rel_path))],
                            'last_updated': datetime.now().isoformat()
                        }
                        
                    except Exception as e:
                        print(f"处理图片 {rel_path} 时出错: {e}")
                        continue
        
        # 保存数据库
        self._save_db()

    def find_images(self, **criteria):
        """
        根据条件搜索图片
        criteria 可以包含：
        - purpose: 网页用途
        - min_width/max_width: 宽度范围
        - min_height/max_height: 高度范围
        - has_text_space: 是否需要文字空间
        - style: 风格要求
        - theme: 主题要求
        - folder_category: 文件夹类别
        """
        results = []
        for path, info in self.tags_db.items():
            matches = True
            
            # 检查各种条件
            if 'purpose' in criteria:
                if criteria['purpose'] not in info['web_usage']['suitable_for']:
                    matches = False
            
            if 'folder_category' in criteria:
                if criteria['folder_category'] not in info['folder_categories']:
                    matches = False
            
            if 'min_width' in criteria:
                if info['technical']['width'] < criteria['min_width']:
                    matches = False
            
            if 'max_width' in criteria:
                if info['technical']['width'] > criteria['max_width']:
                    matches = False
            
            if 'min_height' in criteria:
                if info['technical']['height'] < criteria['min_height']:
                    matches = False
            
            if 'max_height' in criteria:
                if info['technical']['height'] > criteria['max_height']:
                    matches = False
            
            if 'has_text_space' in criteria:
                if info['design']['text_space']['available'] != criteria['has_text_space']:
                    matches = False
            
            if 'theme' in criteria:
                if criteria['theme'] not in info['content']['themes']:
                    matches = False
            
            if matches:
                results.append({
                    'path': path,
                    'info': info
                })
        
        return results

def main():
    # 使用示例
    image_dir = input("请输入图片目录路径：")
    tagger = WebImageTagger(image_dir)
    
    print("开始处理图片...")
    tagger.tag_all_images()
    print("处理完成！")
    
    # 示例：查找适合作为页面头部的图片
    header_images = tagger.find_images(
        purpose='header',
        min_width=1920,
        has_text_space=True
    )
    print(f"\n找到 {len(header_images)} 张适合作为页面头部的图片")

if __name__ == "__main__":
    main()
