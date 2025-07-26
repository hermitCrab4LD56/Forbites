# 四时 - 中式生活美学应用

## 项目概述

"四时"是一个基于留学生定制化做饭的支持平台，融合了传统中式美学与现代技术。应用支持用户位置管理、智能菜谱推荐、食材管理、语音识别、知识库等功能，为海外留学生提供家乡味道的数字化体验。

## 核心特性

### 🎨 中式美学设计
- 采用传统中式色彩搭配
- 自定义字体带来的古典氛围
- 像素风格图标设计，传统复古游戏美学
- 响应式布局，适配多种设备

### 🍳 智能烹饪功能
- **菜谱选择**：根据时间、厨具类型智能筛选菜谱
- **AI推荐**：基于现有食材的智能菜品推荐
- **家乡味道**：经典家常菜谱收藏与分享
- **语音识别**：支持中文语音输入食材信息

### 📱 用户交互体验
- **食材管理**：智能食材识别与数量统计
- **知识库**：烹饪技巧与厨具科普
- **社区功能**：用户交流与经验分享

## 技术架构

### 后端技术栈
- **Flask**: Web框架
- **SQLAlchemy**: ORM数据库操作
- **SQLite**: 轻量级数据库
- **百度语音识别API**: 中文语音转文字
- **豆包AI API**: 智能菜谱生成

### 前端技术栈
- **HTML5 + CSS3**: 页面结构与样式
- **JavaScript ES6+**: 交互逻辑
- **Fetch API**: 前后端通信
- **Web Audio API**: 音频处理

### 数据库设计
```sql
-- 核心数据表
Recipe              -- 菜谱信息
PantryItem          -- 食材库存
UserLocation        -- 用户位置
KnowledgeItem       -- 知识库
HometownRecipe      -- 家乡菜谱
UserIngredient      -- 用户食材
RecipeFilter        -- 菜谱筛选
TipItem             -- 提示信息
```

## 项目结构

```
Codes - Copy/
├── index.html                 # 主页面
├── assets/                    # 静态资源
│   ├── ShuQingGuKaiTi-2.ttf   # 自定义字体
│   ├── 0.png ~ 12.png         # 像素风格图标
│   └── ...
├── backend/                   # 后端服务
│   ├── app.py                # Flask应用主文件
│   ├── requirements.txt      # Python依赖
│   ├── install_dependencies.py # 依赖安装脚本
│   └── instance/
│       └── cooking_app_final.db # SQLite数据库
└── frontend/                  # 前端页面
    ├── api-utils.js          # API工具类
    ├── cooking.html          # 做饭页面
    ├── ingredients.html      # 加料页面
    ├── recipes-select.html   # 菜谱选择
    ├── recipe-result.html    # 菜谱结果
    ├── hometown.html         # 家乡菜单
    ├── community.html        # 社区页面
    ├── knowledge.html        # 知识库
    ├── dictionary.html       # 词典
    ├── cookware.html         # 厨具科普
    ├── oils.html             # 油类科普
    ├── ai-fortune.html       # AI占卜
    └── ...
```

## 核心功能模块

### 1. 主页面 (index.html)
- 四大功能模块入口（青团、粽子、月饼、饺子）
- 用户位置选择器
- 中式美学设计展示

### 2. 做饭模块 (cooking.html)
- 根据已有菜谱做饭
- AI智能推荐
- 家乡味道回顾

### 3. 加料模块 (ingredients.html)
- 根据常见调料选择
- 语音识别输入
- 食材仓库智能标准化管理

### 4. 菜谱系统
- 时间、厨具筛选
- 菜谱详情展示
- 支持手动创建和AI生成

### 5. 知识库系统
- 个人知识库
- 烹饪词典
- 厨具科普
- 油类知识

### 6. 社区功能
- 用户交流
- 社区更新
- AI美食占卜


## 特色功能详解

### 智能食材识别
- 支持中文数字识别（一、二、三...）
- 同义词标准化（番茄/西红柿）
- 多食材语音输入解析
- 数量单位智能识别

### 语音交互
- 16kHz音频重采样
- PCM格式转换
- 百度语音识别集成
- 实时语音状态反馈

### 数据持久化
- SQLite数据库存储
- 用户数据本地化
- 跨会话数据保持
- 数据备份与恢复


---

**四时** - 让中式生活美学在数字时代焕发新光彩 🌸

