import os
import json
import base64
import uuid
from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import requests

# 语音识别功能使用百度智能云API，不需要本地语音识别库

# --- 1. 初始化与配置 ---

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 确保数据目录存在
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 数据文件路径配置
DATA_FILES = {
    'recipes': os.path.join(DATA_DIR, 'recipes.json'),
    'pantry_items': os.path.join(DATA_DIR, 'pantry_items.json'),
    'tip_items': os.path.join(DATA_DIR, 'tip_items.json'),
    'user_locations': os.path.join(DATA_DIR, 'user_locations.json'),
    'knowledge_items': os.path.join(DATA_DIR, 'knowledge_items.json'),
    'hometown_recipes': os.path.join(DATA_DIR, 'hometown_recipes.json'),
    'user_ingredients': os.path.join(DATA_DIR, 'user_ingredients.json'),
    'recipe_filters': os.path.join(DATA_DIR, 'recipe_filters.json')
}

# --- 数据操作工具函数 ---

def load_data(file_key):
    """加载JSON数据"""
    file_path = DATA_FILES[file_key]
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        app.logger.error(f"JSON解码错误: {file_path}")
        return []
    except Exception as e:
        app.logger.error(f"加载数据失败: {str(e)}")
        return []

def save_data(file_key, data):
    """保存数据到JSON文件"""
    file_path = DATA_FILES[file_key]
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"保存数据失败: {str(e)}")
        return False

def get_next_id(file_key):
    """获取下一个ID"""
    data = load_data(file_key)
    if not data:
        return 1
    return max(item['id'] for item in data) + 1


# --- 云服务客户端配置 ---
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"  # 豆包API实际地址可能需要调整

# 百度语音识别配置
BAIDU_ASR_API_KEY = os.getenv("BAIDU_ASR_API_KEY")
BAIDU_ASR_SECRET_KEY = os.getenv("BAIDU_ASR_SECRET_KEY")
BAIDU_ASR_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
BAIDU_ASR_URL = "https://vop.baidu.com/server_api"

# --- 2. 数据库模型定义 ---

# 原SQLAlchemy模型已转换为JSON数据结构，通过工具函数进行操作


# --- 3. 百度语音识别工具函数 ---

def get_baidu_access_token():
    """获取百度API访问令牌"""
    try:
        params = {
            "grant_type": "client_credentials",
            "client_id": BAIDU_ASR_API_KEY,
            "client_secret": BAIDU_ASR_SECRET_KEY
        }
        response = requests.post(BAIDU_ASR_TOKEN_URL, params=params)
        response.raise_for_status()
        return json.loads(response.text)["access_token"]
    except Exception as e:
        app.logger.error(f"获取百度访问令牌失败: {e}")
        raise Exception(f"获取访问令牌失败: {str(e)}")

def baidu_speech_recognition(audio_data, sample_rate=16000):
    """
    使用百度语音识别API识别音频
    audio_data: 音频二进制数据
    sample_rate: 采样率，百度推荐16000
    """
    try:
        # 获取访问令牌
        token = get_baidu_access_token()
        app.logger.info("成功获取百度访问令牌")
        
        # 对音频数据进行Base64编码
        speech = base64.b64encode(audio_data).decode("utf-8")
        length = len(audio_data)
        
        app.logger.info(f"音频数据长度: {length} 字节")
        
        # 构造请求参数
        params = {
            "format": "pcm",  # PCM格式
            "rate": sample_rate,  # 采样率
            "channel": 1,  # 单声道
            "cuid": "cooking_app",  # 设备唯一标识，可自定义
            "token": token,
            "speech": speech,
            "len": length,
            "dev_pid": 1537  # 普通话识别模型，提高识别准确率
        }
        
        app.logger.info(f"发送请求到百度API，参数: {list(params.keys())}")
        
        # 发送识别请求
        response = requests.post(BAIDU_ASR_URL, json=params, timeout=30)
        response.raise_for_status()
        result = json.loads(response.text)
        
        app.logger.info(f"百度API响应: {result}")
        
        # 处理识别结果
        if result.get("err_no") == 0 and "result" in result:
            recognized_text = result["result"][0]
            app.logger.info(f"识别成功: {recognized_text}")
            return recognized_text
        else:
            error_msg = result.get("err_msg", "未知错误")
            error_no = result.get("err_no", "未知")
            app.logger.error(f"百度语音识别失败: {error_msg} (错误码: {error_no})")
            raise Exception(f"识别失败: {error_msg} (错误码: {error_no})")
            
    except requests.exceptions.Timeout:
        app.logger.error("百度API请求超时")
        raise Exception("请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"网络请求失败: {e}")
        raise Exception(f"网络请求失败: {str(e)}")
    except Exception as e:
        app.logger.error(f"百度语音识别过程出错: {e}")
        raise


# --- 4. API 接口实现 ---

# === “做饭”模块 ===
@app.route('/api/recipe/manual', methods=['POST'])
def create_manual_recipe():
    data = request.get_json()
    if not all(k in data for k in ['name', 'ingredients', 'steps']):
        return jsonify({'error': '缺少必要字段'}), 400
    recipes = load_data('recipes')
    new_recipe = {
        'id': get_next_id('recipes'),
        'name': data['name'],
        'ingredients': data['ingredients'],
        'steps': data['steps'],
        'source': 'manual',
        'created_at': datetime.utcnow().isoformat()
    }
    
    recipes.append(new_recipe)
    if save_data('recipes', recipes):
        return jsonify({'message': '菜谱创建成功!', 'recipe': new_recipe}), 201
    else:
        return jsonify({'error': '保存菜谱失败'}), 500

@app.route('/api/recipe/ai_generate', methods=['POST'])
def generate_ai_recipe():
    data = request.get_json()
    if not data or not data.get('ingredients'):
        return jsonify({'error': '食材列表不能为空'}), 400
    
    ingredients_text = ", ".join(data['ingredients'])
    messages = [
        {"role": "system", "content": "你是一位富有创意但又注重安全的美食家。你的任务是根据用户提供的食材，创作一个“能吃且略带荒诞感”的创意菜谱。你的回答必须是一个结构完整的 JSON 对象，包含 `name`, `ingredients`, `steps` 三个字段，不要在 JSON 对象之外添加任何说明、注释或 Markdown 标记。"},
        {"role": "user", "content": f"请根据以下食材：[{ingredients_text}]，创作一个菜谱。"}
    ]
    
    try:
        response = requests.post(
            DOUBAO_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DOUBAO_API_KEY}"
            },
            json={
                "model": "doubao-seed-1-6-flash-250715",
                "messages": messages,
                "stream": False
            }
        )
        response.raise_for_status()
        recipe_data = json.loads(response.json()['choices'][0]['message']['content'])
                
        # 保存生成的菜谱
        recipes = load_data('recipes')
        recipe_data['id'] = get_next_id('recipes')
        recipe_data['source'] = 'ai'
        recipe_data['created_at'] = datetime.utcnow().isoformat()
        recipes.append(recipe_data)
        save_data('recipes', recipes)

        return jsonify(recipe_data), 200
    except Exception as e:
        app.logger.error(f"豆包模型调用失败: {e}")
        return jsonify({'error': '大模型调用失败'}), 500

@app.route('/api/recipe/recommend', methods=['POST'])
def recommend_recipe():
    data = request.get_json()
    user_ingredients = data.get('ingredients', [])
    if not user_ingredients: return jsonify([]), 200

    # 从JSON文件加载所有菜谱
    all_recipes = load_data('recipes')
    matched_recipes = []

    # 筛选包含任一用户食材的菜谱
    for recipe in all_recipes:
        recipe_ingredients = recipe.get('ingredients', [])
        # 检查是否有交集
        if any(ingredient in recipe_ingredients for ingredient in user_ingredients):
            matched_recipes.append(recipe)
            # 限制最多10个结果
            if len(matched_recipes) >= 10:
                break

    return jsonify(matched_recipes), 200

# === 百度API代理模块 ===
@app.route('/api/baidu/token', methods=['GET'])
def get_baidu_token_proxy():
    """代理获取百度API访问令牌"""
    try:
        token = get_baidu_access_token()
        return jsonify({'access_token': token}), 200
    except Exception as e:
        app.logger.error(f"百度令牌代理失败: {e}")
        return jsonify({'error': str(e)}), 500

# === 配置模块 ===
@app.route('/api/config/keys', methods=['GET'])
def get_api_keys():
    """获取API密钥配置"""
    # 实际生产环境中应该添加适当的身份验证和授权
    return jsonify({
        'BAIDU_ASR_API_KEY': BAIDU_ASR_API_KEY,
        'BAIDU_ASR_SECRET_KEY': BAIDU_ASR_SECRET_KEY
    }), 200


# === “加料”模块 ===
@app.route('/api/pantry/items', methods=['POST'])
def add_pantry_items():
    data = request.get_json()
    items_to_add = data.get('items', [])
    if not items_to_add: return jsonify({'error': '物品列表为空'}), 400

    # 加载现有 pantry 数据
    pantry_items = load_data('pantry_items')
    updated = False

    for item_data in items_to_add:
        exists = any(
            item.get('user_id') == 1 and
            item.get('name') == item_data['name'] and
            item.get('item_type') == item_data['item_type']
            for item in pantry_items
        )
        
        if not exists:
            new_item = {
                'id': get_next_id('pantry_items'),
                'user_id': 1,
                'name': item_data['name'],
                'item_type': item_data['item_type'],
                'quantity': item_data.get('quantity'),
                'created_at': datetime.utcnow().isoformat()
            }
            pantry_items.append(new_item)
            updated = True

    if updated and save_data('pantry_items', pantry_items):
        return jsonify({'message': '物品已保存'}), 201
    return jsonify({'error': '保存失败或无新物品添加'}), 500

@app.route('/api/pantry/items', methods=['GET'])
def get_pantry_items():
    item_type = request.args.get('type')
    all_items = load_data('pantry_items')
    user_items = [item for item in all_items if item.get('user_id') == 1]

    # 按类型筛选
    if item_type in ['seasoning', 'ingredient']:
        user_items = [item for item in user_items if item.get('item_type') == item_type]

    return jsonify(user_items)

@app.route('/api/pantry/voice_recognize', methods=['POST'])
def voice_recognize():
    """使用百度语音识别API进行语音识别"""
    if 'audio' not in request.files:
        return jsonify({'error': '缺少音频文件'}), 400
    
    audio_file = request.files['audio']
    
    try:
        # 检查API密钥配置
        if not BAIDU_ASR_API_KEY or not BAIDU_ASR_SECRET_KEY:
            return jsonify({'error': '百度API密钥未配置，请在.env文件中配置BAIDU_ASR_API_KEY和BAIDU_ASR_SECRET_KEY'}), 500
        
        # 读取音频文件内容
        audio_data = audio_file.read()
        app.logger.info(f"接收到音频文件，大小: {len(audio_data)} 字节")
        
        # 调用百度语音识别
        result_text = baidu_speech_recognition(audio_data)
        
        app.logger.info(f"语音识别成功，结果: {result_text}")
        return jsonify({'text': result_text})
    except Exception as e:
        app.logger.error(f"语音识别失败: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/pantry/storage_tips', methods=['POST'])
def get_storage_tips():
    data = request.get_json()
    ingredients = data.get('ingredients', [])
    if not ingredients: return jsonify({}), 200
    
    tips = {}
    for ingredient in ingredients:
        prompt = f"请为“{ingredient}”提供科学的存储建议，包括存储方法和大致的保存期限。返回一个JSON对象，包含 'method' 和 'duration' 两个字段。"
        messages = [{"role": "system", "content": "你是一位专业的食品保鲜专家。请严格按照用户要求的JSON格式返回。"}, {"role": "user", "content": prompt}]
        
        try:
            response = requests.post(
                DOUBAO_API_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DOUBAO_API_KEY}"
                },
                json={
                    "model": "doubao-seed-1-6-flash-250715",
                    "messages": messages
                }
            )
            response.raise_for_status()
            tips[ingredient] = json.loads(response.json()['choices'][0]['message']['content'])
        except Exception:
            tips[ingredient] = {"method": "暂无建议", "duration": "N/A"}
    return jsonify(tips)

# === “社区”模块 ===
@app.route('/api/community/questions', methods=['GET'])
def get_community_questions():
    country = request.args.get('country', '挪威')
    prompt = f"你是一位美食社区的数据分析师。请分析并返回在“{country}”的华人社区中，关于做菜访问量最高的5-7个问题。返回一个JSON数组，数组中的每个元素都是一个问题字符串。"
    messages = [{"role": "system", "content": "请严格按照用户要求的JSON数组格式返回。"}, {"role": "user", "content": prompt}]
    
    try:
        response = requests.post(
            DOUBAO_API_URL,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {DOUBAO_API_KEY}"
            },
            json={
                "model": "doubao-seed-1-6-flash-250715",
                "messages": messages
            }
        )
        response.raise_for_status()
        questions = json.loads(response.json()['choices'][0]['message']['content'])
        return jsonify(questions)
    except Exception:
        return jsonify(["在挪威三文鱼怎么做好吃？", "哪里可以买到亚洲调料？", "挪威的蔬菜保质期为什么这么短？", "挪威的肉类推荐做法？", "Brunost（棕色奶酪）可以用来做什么菜？"]), 200

# === “tips”模块 ===
@app.route('/api/tips', methods=['GET'])
def get_tips():
    tip_type = request.args.get('type')
    context = request.args.get('context', 'norway')
    if not tip_type: return jsonify({'error': '缺少 type 参数'}), 400

    # 从JSON加载并筛选tips
    all_tips = load_data('tip_items')
    filtered_tips = [
        tip for tip in all_tips
        if tip.get('tip_type') == tip_type and tip.get('context') == context
    ]
    return jsonify(filtered_tips)

# === 用户位置管理 ===
# @app.route('/api/user/location', methods=['GET'])
# def get_user_location():
#     """获取用户位置"""
#     locations = load_data('user_locations')
#     # 查找user_id=1的最新位置
#     user_location = next(
#         (loc for loc in locations if loc.get('user_id') == 1),
#         None
#     )
#     return jsonify({'location': user_location.get('location')} if user_location else {'location': None})

@app.route('/api/user/location', methods=['POST'])
def set_user_location():
    """设置用户位置"""
    data = request.get_json()
    location_value = data.get('location')
    if not location_value:
        return jsonify({'error': '位置信息不能为空'}), 400
    
    locations = load_data('user_locations')
    # 查找现有记录
    user_location = next(
        (loc for loc in locations if loc.get('user_id') == 1),
        None
    )

    if user_location:
        user_location['location'] = location_value
        user_location['updated_at'] = datetime.utcnow().isoformat()
    else:
        new_location = {
            'id': get_next_id('user_locations'),
            'user_id': 1,
            'location': location_value,
            'created_at': datetime.utcnow().isoformat()
        }
        locations.append(new_location)
    
    if save_data('user_locations', locations):
        return jsonify({'message': '位置设置成功', 'location': location_value})
    return jsonify({'error': '保存位置失败'}), 500

# === 知识库管理 ===
@app.route('/api/knowledge/items', methods=['GET'])
def get_knowledge_items():
    """获取知识库项目"""
    items = load_data('knowledge_items')
    # 筛选user_id=1并按创建时间降序
    user_items = [item for item in items if item.get('user_id') == 1]
    user_items.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(user_items)


@app.route('/api/knowledge/items', methods=['POST'])
def create_knowledge_item():
    """创建知识库项目"""
    data = request.get_json()
    if not all(k in data for k in ['title', 'content']):
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 解析日期
    from datetime import datetime
    date_str = data.get('date')
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.now().date()
        date_str = date_obj.isoformat()
    except ValueError:
        date_str = datetime.now().date().isoformat()
    
    # 加载现有数据
    knowledge_items = load_data('knowledge_items')
    new_item = {
        'id': get_next_id('knowledge_items'),
        'user_id': 1,
        'title': data['title'],
        'content': data['content'],
        'image': data.get('image'),
        'date': date_str,
        'created_at': datetime.utcnow().isoformat()
    }
    
    knowledge_items.append(new_item)
    if save_data('knowledge_items', knowledge_items):
        return jsonify({'message': '知识项目创建成功', 'item': new_item}), 201
    return jsonify({'error': '保存知识项目失败'}), 500


@app.route('/api/knowledge/items/<int:item_id>', methods=['DELETE'])
def delete_knowledge_item(item_id):
    """删除知识库项目"""
    items = load_data('knowledge_items')
    # 筛选保留非目标项（user_id=1且id匹配）
    filtered_items = [
        item for item in items
        if not (item.get('id') == item_id and item.get('user_id') == 1)
    ]
    
    if len(filtered_items) < len(items) and save_data('knowledge_items', filtered_items):
        return jsonify({'message': '项目删除成功'})
    return jsonify({'error': '项目不存在或删除失败'}), 404

# === 家乡菜谱管理 ===
@app.route('/api/hometown/recipes', methods=['GET'])
def get_hometown_recipes():
    """获取家乡菜谱"""
    recipes = load_data('hometown_recipes')
    # 筛选user_id=1并按创建时间降序
    user_recipes = [r for r in recipes if r.get('user_id') == 1]
    user_recipes.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(user_recipes)


@app.route('/api/hometown/recipes', methods=['POST'])
def create_hometown_recipe():
    """创建家乡菜谱"""
    data = request.get_json()
    if not all(k in data for k in ['name', 'ingredients', 'steps']):
        return jsonify({'error': '菜谱名称、食材和步骤不能为空'}), 400
    
    recipes = load_data('hometown_recipes')
    new_recipe = {
        'id': get_next_id('hometown_recipes'),
        'user_id': 1,
        'name': data['name'],
        'ingredients': data['ingredients'],  # 直接存储列表（原代码用json.dumps，这里简化为列表）
        'steps': data['steps'],
        'created_at': datetime.utcnow().isoformat()
    }
    
    recipes.append(new_recipe)
    if save_data('hometown_recipes', recipes):
        return jsonify({'message': '菜谱创建成功', 'recipe': new_recipe}), 201
    return jsonify({'error': '保存菜谱失败'}), 500


@app.route('/api/hometown/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_hometown_recipe(recipe_id):
    """删除家乡菜谱"""
    recipes = load_data('hometown_recipes')
    filtered_recipes = [
        r for r in recipes
        if not (r.get('id') == recipe_id and r.get('user_id') == 1)
    ]
    
    if len(filtered_recipes) < len(recipes) and save_data('hometown_recipes', filtered_recipes):
        return jsonify({'message': '菜谱删除成功'})
    return jsonify({'error': '菜谱不存在或删除失败'}), 404

# === 用户食材管理 ===
@app.route('/api/user/ingredients', methods=['GET'])
def get_user_ingredients():
    """获取用户选择的食材"""
    ingredients = load_data('user_ingredients')
    user_ingredients = [i for i in ingredients if i.get('user_id') == 1]
    user_ingredients.sort(key=lambda x: x.get('added_at', ''), reverse=True)
    return jsonify(user_ingredients)


@app.route('/api/user/ingredients', methods=['POST'])
def add_user_ingredients():
    """添加用户食材"""
    data = request.get_json()
    ingredients_list = data.get('ingredients', [])
    if not ingredients_list:
        return jsonify({'error': '食材列表不能为空'}), 400
    
    # 加载现有食材并去重
    user_ingredients = load_data('user_ingredients')
    existing_names = {
        item['name'] for item in user_ingredients
        if item.get('user_id') == 1
    }
    
    added_count = 0
    for name in ingredients_list:
        if name not in existing_names:
            new_ingredient = {
                'id': get_next_id('user_ingredients'),
                'user_id': 1,
                'name': name,
                'added_at': datetime.utcnow().isoformat()
            }
            user_ingredients.append(new_ingredient)
            existing_names.add(name)
            added_count += 1
    
    if added_count > 0 and save_data('user_ingredients', user_ingredients):
        return jsonify({'message': f'成功添加 {added_count} 种食材'})
    return jsonify({'error': '无新食材添加或保存失败'}), 500

@app.route('/api/user/ingredients/<int:ingredient_id>', methods=['DELETE'])
def delete_user_ingredient(ingredient_id):
    """删除用户食材"""
    ingredients = load_data('user_ingredients')
    filtered = [
        i for i in ingredients
        if not (i.get('id') == ingredient_id and i.get('user_id') == 1)
    ]
    
    if len(filtered) < len(ingredients) and save_data('user_ingredients', filtered):
        return jsonify({'message': '食材删除成功'})
    return jsonify({'error': '食材不存在或删除失败'}), 404


@app.route('/api/user/ingredients/clear', methods=['DELETE'])
def clear_all_user_ingredients():
    """清除用户所有食材"""
    ingredients = load_data('user_ingredients')
    # 保留非当前用户的食材
    filtered = [i for i in ingredients if i.get('user_id') != 1]
    deleted_count = len(ingredients) - len(filtered)
    
    if save_data('user_ingredients', filtered):
        return jsonify({'message': f'成功清除 {deleted_count} 个食材'})
    return jsonify({'error': '清除食材失败'}), 500

# === 菜谱筛选条件管理 ===
@app.route('/api/recipe/filters', methods=['GET'])
def get_recipe_filters():
    """获取菜谱筛选条件"""
    filters = load_data('recipe_filters')
    # 获取user_id=1的最新筛选条件
    user_filters = [f for f in filters if f.get('user_id') == 1]
    # 按创建时间降序取最新
    user_filters.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    return jsonify(user_filters[0] if user_filters else {})


@app.route('/api/recipe/filters', methods=['POST'])
def set_recipe_filters():
    """设置菜谱筛选条件"""
    data = request.get_json()
    if not all(k in data for k in ['cooking_time', 'is_packable', 'is_induction']):
        return jsonify({'error': '筛选条件不完整'}), 400
    
    filters = load_data('recipe_filters')
    # 删除用户旧筛选条件
    filters = [f for f in filters if f.get('user_id') != 1]
    
    # 添加新筛选条件
    new_filter = {
        'id': get_next_id('recipe_filters'),
        'user_id': 1,
        'cooking_time': data['cooking_time'],
        'is_packable': data['is_packable'],
        'is_induction': data['is_induction'],
        'created_at': datetime.utcnow().isoformat()
    }
    filters.append(new_filter)
    
    if save_data('recipe_filters', filters):
        return jsonify({'message': '筛选条件设置成功', 'filters': new_filter})
    return jsonify({'error': '保存筛选条件失败'}), 500


# --- 数据库初始化与应用启动 ---
def seed_database():
    """初始化tip_items数据（如果为空）"""
    tips = load_data('tip_items')
    if tips:  # 已有数据则跳过
        print("tip_items已有数据，跳过初始化")
        return
    
    print("初始化tip_items数据...")
    from datetime import datetime
    current_time = datetime.utcnow().isoformat()
    initial_tips = [
        {
            'id': 1,
            'tip_type': 'translation',
            'context': 'norway',
            'data': {'category': 'ingredient', 'cn': '三文鱼', 'no': 'Laks'},
            'created_at': current_time
        },
        {
            'id': 2,
            'tip_type': 'translation',
            'context': 'norway',
            'data': {'category': 'ingredient', 'cn': '鳕鱼', 'no': 'Torsk'},
            'created_at': current_time
        },
        {
            'id': 3,
            'tip_type': 'translation',
            'context': 'norway',
            'data': {'category': 'ingredient', 'cn': '土豆', 'no': 'Potet'},
            'created_at': current_time
        },
        {
            'id': 4,
            'tip_type': 'translation',
            'context': 'norway',
            'data': {'category': 'seasoning', 'cn': '酱油', 'no': 'Soyasaus'},
            'created_at': current_time
        },
        {
            'id': 5,
            'tip_type': 'translation',
            'context': 'norway',
            'data': {'category': 'seasoning', 'cn': '盐', 'no': 'Salt'},
            'created_at': current_time
        },
        {
            'id': 6,
            'tip_type': 'cookware',
            'context': 'norway',
            'data': {'name': '不粘锅 (Stekepanne)', 'size': '28cm', 'material': '铝制带涂层', 'pros': '不易粘，易清洗', 'cons': '涂层易磨损'},
            'created_at': current_time
        },
        {
            'id': 7,
            'tip_type': 'cookware',
            'context': 'norway',
            'data': {'name': '铸铁锅 (Støpejernsgryte)', 'size': '24cm / 4L', 'material': '铸铁', 'pros': '受热均匀，保温性好', 'cons': '重，需养锅'},
            'created_at': current_time
        },
        {
            'id': 8,
            'tip_type': 'oil',
            'context': 'norway',
            'data': {'name': '菜籽油 (Rapsolje)', 'usage': '通用，适合炒菜、烘焙', 'nutrition': '富含不饱和脂肪酸'},
            'created_at': current_time
        },
        {
            'id': 9,
            'tip_type': 'oil',
            'context': 'norway',
            'data': {'name': '黄油 (Smør)', 'usage': '煎牛排、烘焙、涂面包', 'nutrition': '风味浓郁'},
            'created_at': current_time
        }
    ]
    
    if save_data('tip_items', initial_tips):
        print("tip_items初始化完成")
    else:
        print("tip_items初始化失败")


if __name__ == '__main__':
    seed_database()  # 初始化数据
    app.run(debug=True, port=5001)