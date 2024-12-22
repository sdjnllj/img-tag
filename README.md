# AI 建筑图片标注系统

## 1. 系统概述

这是一个基于 AI 视觉技术的建筑图片智能标注系统。系统使用 CLIP 模型自动分析建筑图片，识别建筑特征、场景类型和建筑元素，并提供 Web 界面用于浏览和搜索图片。

### 主要特点

- 使用 CLIP AI 模型进行图片分析
- 支持中英文双语标签
- 智能增量更新，只处理新图片
- 提供 Web 界面浏览和搜索
- 支持多维度标签搜索

## 2. 安装和依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- transformers (CLIP 模型)
- torch (深度学习框架)
- PIL (图片处理)
- flask (Web 服务器)

## 3. 使用方法

系统分为两个主要部分：图片标注程序和 Web 展示服务。

### 3.1 图片标注

1. 增量更新（只处理新图片）：
```bash
# 使用默认的imgs目录
python run_tagger.py

# 或指定其他目录
python run_tagger.py --dir D:/我的图片/建筑图片
```

2. 强制重新标注所有图片：
```bash
# 使用默认的imgs目录
python run_tagger.py --force

# 或指定其他目录
python run_tagger.py --dir D:/我的图片/建筑图片 --force
```

命令行参数说明：
- `--dir` 或 `-d`: 指定要处理的图片目录路径（默认为项目下的imgs文件夹）
- `--force` 或 `-f`: 强制重新处理所有图片（默认只处理新图片）

### 3.2 Web 展示服务

启动 Web 服务器：
```bash
cd web
python -m flask run
```

然后访问 http://localhost:5000 即可浏览图片。

## 4. 标签系统

系统使用三类标签对图片进行描述，每个标签都包含中英文对照，方便不同语言的用户使用。CLIP模型会同时分析这三类标签，并给出置信度最高的组合：

### 4.1 建筑特征标签
主要描述建筑的整体特征：
- 建筑外观 exterior
- 建筑立面 facade
- 建筑细节 architectural detail
- 室内空间 interior space
- 办公空间 office space
- 居住空间 living space
- 景观设计 landscape design
- 建筑风格（现代、古典、工业等）
- 设计特点（绿色建筑、可持续设计等）

### 4.2 场景描述标签
描述建筑所处的环境和用途：
- 城市景观 urban landscape
- 自然环境 natural environment
- 商业空间 commercial space
- 文化场所 cultural space
- 教育设施 educational facility
- 交通枢纽 transportation hub
- 休闲场所 leisure space
- 运动场馆 sports venue
- 医疗设施 healthcare facility
- 住宅区 residential area

### 4.3 建筑元素标签
识别建筑中的具体构件和材料：
- 玻璃幕墙 glass curtain wall
- 钢结构 steel structure
- 混凝土 concrete
- 木材 wood
- 石材 stone
- 金属饰面 metal finish
- 绿植 plants
- 水景 water feature
- 采光顶 skylight
- 露台 terrace
- 庭院 courtyard
- 栏杆 railing
- 楼梯 staircase
- 门窗 windows and doors

### 4.4 标签使用说明

1. **多维度描述**
   - 每张图片会同时获得多个类别的标签
   - 比如一张图片可能同时标注为"现代建筑"、"商业空间"和"玻璃幕墙"

2. **标签置信度**
   - 每个标签都有相应的置信度分数
   - 系统会优先展示置信度高的标签
   - 默认展示前20个最相关的标签

3. **搜索功能**
   - 可以使用任意标签进行搜索
   - 支持组合搜索，如"现代建筑+商业空间"
   - 支持中英文搜索

4. **标签更新**
   - 新增图片时自动增量更新标签
   - 使用 --force 参数可重新分析所有图片
   - 标签数据保存在 web_image_tags.json 中

## 5. 系统工作流程

1. **图片标注流程**
   - 扫描图片目录
   - 检查是否有新图片需要处理
   - 使用 CLIP 模型分析新图片
   - 保存标签到 web_image_tags.json

2. **Web 展示流程**
   - 读取 web_image_tags.json
   - 提供图片浏览界面
   - 支持按标签搜索
   - 展示图片详细信息

## 6. 注意事项

1. **图片要求**
   - 支持格式：jpg, jpeg, png, gif, bmp
   - 建议使用清晰的建筑图片
   - 图片名称不要包含特殊字符

2. **标签数据库**
   - 标签信息存储在 web_image_tags.json
   - 请勿手动修改该文件
   - 需要重新标注时使用 --force 参数

3. **性能考虑**
   - 首次运行会下载 CLIP 模型
   - 增量更新只处理新图片，速度较快
   - 强制更新会重新处理所有图片，耗时较长

## 7. 常见问题

1. **Q: 如何添加新图片？**
   A: 直接将新图片复制到图片目录，然后运行 `python run_tagger.py`

2. **Q: 标签不准确怎么办？**
   A: 使用 `python run_tagger.py --force` 重新标注所有图片

3. **Q: 如何自定义标签？**
   A: 修改 image_tagger.py 中的标签列表，然后使用 --force 重新标注

## 8. 未来改进方向

1. 支持更多建筑专业标签
2. 添加标签权重和置信度显示
3. 优化 Web 界面交互体验
4. 支持手动调整标签
