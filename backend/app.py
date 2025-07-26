import os
import json
import base64
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import requests

# 语音识别功能使用百度智能云API，不需要本地语音识别库

# --- 1. 初始化与配置 ---

load_dotenv()
app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cooking_app_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 云服务客户端配置 ---
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY")
DOUBAO_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"  # 豆包API实际地址可能需要调整

# 百度语音识别配置
BAIDU_ASR_API_KEY = os.getenv("BAIDU_ASR_API_KEY")
BAIDU_ASR_SECRET_KEY = os.getenv("BAIDU_ASR_SECRET_KEY")
BAIDU_ASR_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
BAIDU_ASR_URL = "https://vop.baidu.com/server_api"

# --- 2. 数据库模型定义 ---

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.Text, nullable=False) 
    steps = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(20), default='manual', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {'id': self.id, 'name': self.name, 'ingredients': json.loads(self.ingredients), 'steps': self.steps, 'source': self.source}

class PantryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.String(50), nullable=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {'id': self.id, 'name': self.name, 'item_type': self.item_type, 'quantity': self.quantity}

class TipItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tip_type = db.Column(db.String(20), nullable=False)
    context = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=False)
    def to_dict(self): return {'id': self.id, 'tip_type': self.tip_type, 'context': self.context, 'data': json.loads(self.data)}

# 新增数据库模型
class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    location = db.Column(db.String(50), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def to_dict(self): return {'id': self.id, 'location': self.location, 'updated_at': self.updated_at.isoformat()}

class KnowledgeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=True)  # base64编码的图片
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {
        'id': self.id, 
        'title': self.title, 
        'content': self.content, 
        'image': self.image,
        'date': self.date.isoformat() if self.date else None
    }

class HometownRecipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)  # JSON格式存储
    steps = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {
        'id': self.id, 
        'name': self.name, 
        'ingredients': json.loads(self.ingredients), 
        'steps': self.steps
    }

class UserIngredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {'id': self.id, 'name': self.name}

class RecipeFilter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    is_packable = db.Column(db.Boolean, nullable=False)
    is_induction = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self): return {
        'id': self.id, 
        'cooking_time': self.cooking_time, 
        'is_packable': self.is_packable, 
        'is_induction': self.is_induction
    }


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
    new_recipe = Recipe(
        name=data['name'],
        ingredients=json.dumps(data['ingredients']),
        steps=data['steps'],
        source='manual'
    )
    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({'message': '菜谱创建成功!', 'recipe': new_recipe.to_dict()}), 201

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
        return jsonify(recipe_data), 200
    except Exception as e:
        app.logger.error(f"豆包模型调用失败: {e}")
        return jsonify({'error': '大模型调用失败'}), 500

@app.route('/api/recipe/recommend', methods=['POST'])
def recommend_recipe():
    data = request.get_json()
    user_ingredients = data.get('ingredients', [])
    if not user_ingredients: return jsonify([]), 200

    from sqlalchemy import or_
    conditions = [Recipe.ingredients.like(f'%"{ingredient}"%') for ingredient in user_ingredients]
    recipes = Recipe.query.filter(or_(*conditions)).limit(10).all()
    return jsonify([r.to_dict() for r in recipes]), 200

# === “加料”模块 ===
@app.route('/api/pantry/items', methods=['POST'])
def add_pantry_items():
    data = request.get_json()
    items_to_add = data.get('items', [])
    if not items_to_add: return jsonify({'error': '物品列表为空'}), 400

    for item_data in items_to_add:
        exists = PantryItem.query.filter_by(user_id=1, name=item_data['name'], item_type=item_data['item_type']).first()
        if not exists:
            new_item = PantryItem(
                name=item_data['name'],
                item_type=item_data['item_type'],
                quantity=item_data.get('quantity')
            )
            db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': '物品已保存'}), 201

@app.route('/api/pantry/items', methods=['GET'])
def get_pantry_items():
    item_type = request.args.get('type')
    query = PantryItem.query.filter_by(user_id=1)
    if item_type in ['seasoning', 'ingredient']:
        query = query.filter_by(item_type=item_type)
    items = query.all()
    return jsonify([item.to_dict() for item in items])

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

    tips = TipItem.query.filter_by(tip_type=tip_type, context=context).all()
    return jsonify([tip.to_dict() for tip in tips])

# === 新增API接口 ===

# 用户位置管理
@app.route('/api/user/location', methods=['GET'])
def get_user_location():
    """获取用户位置"""
    location = UserLocation.query.filter_by(user_id=1).first()
    if location:
        return jsonify({'location': location.location})
    return jsonify({'location': None})

@app.route('/api/user/location', methods=['POST'])
def set_user_location():
    """设置用户位置"""
    data = request.get_json()
    location_value = data.get('location')
    if not location_value:
        return jsonify({'error': '位置信息不能为空'}), 400
    
    # 查找现有记录或创建新记录
    location = UserLocation.query.filter_by(user_id=1).first()
    if location:
        location.location = location_value
    else:
        location = UserLocation(user_id=1, location=location_value)
        db.session.add(location)
    
    db.session.commit()
    return jsonify({'message': '位置设置成功', 'location': location_value})

# 知识库管理
@app.route('/api/knowledge/items', methods=['GET'])
def get_knowledge_items():
    """获取知识库项目"""
    items = KnowledgeItem.query.filter_by(user_id=1).order_by(KnowledgeItem.created_at.desc()).all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/knowledge/items', methods=['POST'])
def create_knowledge_item():
    """创建知识库项目"""
    data = request.get_json()
    if not all(k in data for k in ['title', 'content']):
        return jsonify({'error': '标题和内容不能为空'}), 400
    
    # 解析日期
    from datetime import datetime
    date_str = data.get('date')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date_obj = datetime.now().date()
    else:
        date_obj = datetime.now().date()
    
    new_item = KnowledgeItem(
        user_id=1,
        title=data['title'],
        content=data['content'],
        image=data.get('image'),
        date=date_obj
    )
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'message': '知识项目创建成功', 'item': new_item.to_dict()}), 201

@app.route('/api/knowledge/items/<int:item_id>', methods=['DELETE'])
def delete_knowledge_item(item_id):
    """删除知识库项目"""
    item = KnowledgeItem.query.filter_by(id=item_id, user_id=1).first()
    if not item:
        return jsonify({'error': '项目不存在'}), 404
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': '项目删除成功'})

# 家乡菜谱管理
@app.route('/api/hometown/recipes', methods=['GET'])
def get_hometown_recipes():
    """获取家乡菜谱"""
    recipes = HometownRecipe.query.filter_by(user_id=1).order_by(HometownRecipe.created_at.desc()).all()
    return jsonify([recipe.to_dict() for recipe in recipes])

@app.route('/api/hometown/recipes', methods=['POST'])
def create_hometown_recipe():
    """创建家乡菜谱"""
    data = request.get_json()
    if not all(k in data for k in ['name', 'ingredients', 'steps']):
        return jsonify({'error': '菜谱名称、食材和步骤不能为空'}), 400
    
    new_recipe = HometownRecipe(
        user_id=1,
        name=data['name'],
        ingredients=json.dumps(data['ingredients']),
        steps=data['steps']
    )
    db.session.add(new_recipe)
    db.session.commit()
    
    return jsonify({'message': '菜谱创建成功', 'recipe': new_recipe.to_dict()}), 201

@app.route('/api/hometown/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_hometown_recipe(recipe_id):
    """删除家乡菜谱"""
    recipe = HometownRecipe.query.filter_by(id=recipe_id, user_id=1).first()
    if not recipe:
        return jsonify({'error': '菜谱不存在'}), 404
    
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({'message': '菜谱删除成功'})

# 用户食材管理
@app.route('/api/user/ingredients', methods=['GET'])
def get_user_ingredients():
    """获取用户选择的食材"""
    ingredients = UserIngredient.query.filter_by(user_id=1).order_by(UserIngredient.added_at.desc()).all()
    return jsonify([item.to_dict() for item in ingredients])

@app.route('/api/user/ingredients', methods=['POST'])
def add_user_ingredients():
    """添加用户食材"""
    data = request.get_json()
    ingredients_list = data.get('ingredients', [])
    if not ingredients_list:
        return jsonify({'error': '食材列表不能为空'}), 400
    
    # 检查是否已存在，避免重复添加
    existing_ingredients = {item.name for item in UserIngredient.query.filter_by(user_id=1).all()}
    
    for ingredient_name in ingredients_list:
        if ingredient_name not in existing_ingredients:
            new_ingredient = UserIngredient(user_id=1, name=ingredient_name)
            db.session.add(new_ingredient)
    
    db.session.commit()
    return jsonify({'message': '食材添加成功'})

@app.route('/api/user/ingredients/<int:ingredient_id>', methods=['DELETE'])
def delete_user_ingredient(ingredient_id):
    """删除用户食材"""
    ingredient = UserIngredient.query.filter_by(id=ingredient_id, user_id=1).first()
    if not ingredient:
        return jsonify({'error': '食材不存在'}), 404
    
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({'message': '食材删除成功'})

@app.route('/api/user/ingredients/clear', methods=['DELETE'])
def clear_all_user_ingredients():
    """清除用户所有食材"""
    try:
        # 删除用户的所有食材
        deleted_count = UserIngredient.query.filter_by(user_id=1).delete()
        db.session.commit()
        return jsonify({'message': f'成功清除 {deleted_count} 个食材'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': '清除食材失败'}), 500

# 菜谱筛选条件管理
@app.route('/api/recipe/filters', methods=['GET'])
def get_recipe_filters():
    """获取菜谱筛选条件"""
    filters = RecipeFilter.query.filter_by(user_id=1).order_by(RecipeFilter.created_at.desc()).first()
    if filters:
        return jsonify(filters.to_dict())
    return jsonify({})

@app.route('/api/recipe/filters', methods=['POST'])
def set_recipe_filters():
    """设置菜谱筛选条件"""
    data = request.get_json()
    if not all(k in data for k in ['cooking_time', 'is_packable', 'is_induction']):
        return jsonify({'error': '筛选条件不完整'}), 400
    
    # 删除旧的筛选条件
    RecipeFilter.query.filter_by(user_id=1).delete()
    
    new_filter = RecipeFilter(
        user_id=1,
        cooking_time=data['cooking_time'],
        is_packable=data['is_packable'],
        is_induction=data['is_induction']
    )
    db.session.add(new_filter)
    db.session.commit()
    
    return jsonify({'message': '筛选条件设置成功', 'filters': new_filter.to_dict()})

# --- 数据库初始化与应用启动 ---
def seed_database():
    if TipItem.query.first():
        print("数据库已有数据，跳过填充。")
        return
    print("正在为'tips'模块填充初始数据...")
    tips_data = [
        TipItem(tip_type='translation', context='norway', data=json.dumps({'category': 'ingredient', 'cn': '三文鱼', 'no': 'Laks'})),
        TipItem(tip_type='translation', context='norway', data=json.dumps({'category': 'ingredient', 'cn': '鳕鱼', 'no': 'Torsk'})),
        TipItem(tip_type='translation', context='norway', data=json.dumps({'category': 'ingredient', 'cn': '土豆', 'no': 'Potet'})),
        TipItem(tip_type='translation', context='norway', data=json.dumps({'category': 'seasoning', 'cn': '酱油', 'no': 'Soyasaus'})),
        TipItem(tip_type='translation', context='norway', data=json.dumps({'category': 'seasoning', 'cn': '盐', 'no': 'Salt'})),
        TipItem(tip_type='cookware', context='norway', data=json.dumps({'name': '不粘锅 (Stekepanne)', 'size': '28cm', 'material': '铝制带涂层', 'pros': '不易粘，易清洗', 'cons': '涂层易磨损'})),
        TipItem(tip_type='cookware', context='norway', data=json.dumps({'name': '铸铁锅 (Støpejernsgryte)', 'size': '24cm / 4L', 'material': '铸铁', 'pros': '受热均匀，保温性好', 'cons': '重，需养锅'})),
        TipItem(tip_type='oil', context='norway', data=json.dumps({'name': '菜籽油 (Rapsolje)', 'usage': '通用，适合炒菜、烘焙', 'nutrition': '富含不饱和脂肪酸'})),
        TipItem(tip_type='oil', context='norway', data=json.dumps({'name': '黄油 (Smør)', 'usage': '煎牛排、烘焙、涂面包', 'nutrition': '风味浓郁'}))
    ]
    db.session.bulk_save_objects(tips_data)
    db.session.commit()
    print("初始数据填充完毕。")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5001)
