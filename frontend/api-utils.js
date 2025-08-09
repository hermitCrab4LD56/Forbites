// API工具类 - 用于与后端通信，替换localStorage操作
class APIUtils {
    constructor() {
        this.baseURL = '/api';
    }

    // 通用请求方法
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    // 用户位置管理
    // async getUserLocation() {
    //     try {
    //         const result = await this.request('/user/location');
    //         return result.location;
    //     } catch (error) {
    //         console.error('获取用户位置失败:', error);
    //         return null;
    //     }
    // }

    // async setUserLocation(location) {
    //     try {
    //         const result = await this.request('/user/location', {
    //             method: 'POST',
    //             body: JSON.stringify({ location })
    //         });
    //         return result;
    //     } catch (error) {
    //         console.error('设置用户位置失败:', error);
    //         throw error;
    //     }
    // }

    // 知识库管理
    async getKnowledgeItems() {
        try {
            const result = await this.request('/knowledge/items');
            return result;
        } catch (error) {
            console.error('获取知识库项目失败:', error);
            return [];
        }
    }

    async createKnowledgeItem(item) {
        try {
            const result = await this.request('/knowledge/items', {
                method: 'POST',
                body: JSON.stringify(item)
            });
            return result;
        } catch (error) {
            console.error('创建知识库项目失败:', error);
            throw error;
        }
    }

    async deleteKnowledgeItem(itemId) {
        try {
            const result = await this.request(`/knowledge/items/${itemId}`, {
                method: 'DELETE'
            });
            return result;
        } catch (error) {
            console.error('删除知识库项目失败:', error);
            throw error;
        }
    }

    // 家乡菜谱管理
    async getHometownRecipes() {
        try {
            const result = await this.request('/hometown/recipes');
            return result;
        } catch (error) {
            console.error('获取家乡菜谱失败:', error);
            return [];
        }
    }

    async createHometownRecipe(recipe) {
        try {
            const result = await this.request('/hometown/recipes', {
                method: 'POST',
                body: JSON.stringify(recipe)
            });
            return result;
        } catch (error) {
            console.error('创建家乡菜谱失败:', error);
            throw error;
        }
    }

    async deleteHometownRecipe(recipeId) {
        try {
            const result = await this.request(`/hometown/recipes/${recipeId}`, {
                method: 'DELETE'
            });
            return result;
        } catch (error) {
            console.error('删除家乡菜谱失败:', error);
            throw error;
        }
    }

    // 用户食材管理 - 使用localStorage代替API
    async getUserIngredients() {
        try {
            const ingredients = localStorage.getItem('userIngredients');
            return ingredients ? JSON.parse(ingredients) : [];
        } catch (error) {
            console.error('获取用户食材失败:', error);
            return [];
        }
    }

    async addUserIngredients(ingredients) {
        try {
            const result = await this.request('/user/ingredients', {
                method: 'POST',
                body: JSON.stringify({ ingredients })
            });
            return result;
        } catch (error) {
            console.error('添加用户食材失败:', error);
            throw error;
        }
    }

    async deleteUserIngredient(ingredientId) {
        try {
            const result = await this.request(`/user/ingredients/${ingredientId}`, {
                method: 'DELETE'
            });
            return result;
        } catch (error) {
            console.error('删除用户食材失败:', error);
            throw error;
        }
    }

    async clearAllUserIngredients() {
        try {
            const result = await this.request('/user/ingredients/clear', {
                method: 'DELETE'
            });
            return result;
        } catch (error) {
            console.error('清空用户食材失败:', error);
            throw error;
        }
    }

    // 菜谱筛选条件管理 - 使用localStorage代替API
    async getRecipeFilters() {
        try {
            const filters = localStorage.getItem('recipeFilters');
            return filters ? JSON.parse(filters) : {};
        } catch (error) {
            console.error('获取菜谱筛选条件失败:', error);
            return {};
        }
    }

    async setRecipeFilters(filters) {
        try {
            const validFilters = {
                cooking_time: filters.cooking_time || 1,
                is_packable: filters.is_packable || false,
                is_induction: filters.is_induction || false
            };
            localStorage.setItem('recipeFilters', JSON.stringify(validFilters));
            return validFilters;
        } catch (error) {
            console.error('设置菜谱筛选条件失败:', error);
            throw error;
        }
    }


    // 菜谱推荐 - 使用localStorage代替API
    async recommendRecipes(ingredients) {
        try {
            // 从localStorage获取菜谱数据
            const recipes = localStorage.getItem('recipes');
            if (!recipes) return [];
            
            const parsedRecipes = JSON.parse(recipes);
            const filters = await this.getRecipeFilters();
            
            // 简单的筛选逻辑（根据实际需求调整）
            return parsedRecipes.filter(recipe => {
                // 检查烹饪时间
                if (filters.cooking_time === 1 && recipe.cooking_time > 30) return false;
                if (filters.cooking_time === 2 && recipe.cooking_time > 60) return false;
                if (filters.cooking_time === 3 && recipe.cooking_time > 120) return false;
                
                // 检查打包选项
                if (filters.is_packable && !recipe.is_packable) return false;
                
                // 检查电磁炉选项
                if (filters.is_induction && !recipe.is_induction) return false;
                
                // 检查食材匹配（简单匹配）
                if (ingredients.length > 0) {
                    const recipeIngredients = recipe.ingredients.map(ing => ing.name.toLowerCase());
                    return ingredients.some(ing => recipeIngredients.includes(ing.toLowerCase()));
                }
                
                return true;
            });
        } catch (error) {
            console.error('获取菜谱推荐失败:', error);
            return [];
        }
    }

    // 获取百度语音识别Access Token
    async getBaiduAccessToken() {
        try {
            // 调用后端代理接口获取百度Access Token
            const tokenResponse = await fetch('/api/baidu/token', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json; charset=UTF-8'
                }
            });
            
            if (!tokenResponse.ok) {
                throw new Error(`获取百度Access Token失败: HTTP状态码 ${tokenResponse.status}`);
            }
            
            const { access_token } = await tokenResponse.json();
            
            if (!access_token) {
                throw new Error('未获取到百度Access Token');
            }
            
            return access_token;
        } catch (error) {
            console.error('获取百度Access Token失败:', error);
            throw error;
        }
    }

    // 语音识别 - 调用百度云API
    async recognizeVoice(audioBlob) {
        try {
            // 获取Access Token
            const accessToken = await this.getBaiduAccessToken();
            
            // 语音识别API地址
            const apiUrl = `https://vop.baidu.com/server_api?dev_pid=1537&cuid=forbites&token=${accessToken}`;
            
            // 读取音频文件并转换为Base64
            const reader = new FileReader();
            const audioData = await new Promise((resolve, reject) => {
                reader.onloadend = () => resolve(reader.result.split(',')[1]);
                reader.onerror = reject;
                reader.readAsDataURL(audioBlob);
            });
            
            // 发送请求到百度语音识别API
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    format: 'wav',
                    rate: 16000,
                    channel: 1,
                    cuid: 'forbites',
                    token: accessToken,
                    speech: audioData,
                    len: audioBlob.size
                })
            });
            
            const result = await response.json();
            
            if (result.err_no !== 0) {
                throw new Error(`百度语音识别失败: ${result.err_msg}`);
            }
            
            return {
                text: result.result[0]
            };
        } catch (error) {
            console.error('语音识别失败:', error);
            throw error;
        }
    }

    // 存储建议
    async getStorageTips(ingredients) {
        try {
            const result = await this.request('/pantry/storage_tips', {
                method: 'POST',
                body: JSON.stringify({ ingredients })
            });
            return result;
        } catch (error) {
            console.error('获取存储建议失败:', error);
            return {};
        }
    }

    // 社区问题
    async getCommunityQuestions(country = '挪威') {
        try {
            const result = await this.request(`/community/questions?country=${encodeURIComponent(country)}`);
            return result;
        } catch (error) {
            console.error('获取社区问题失败:', error);
            return [];
        }
    }

    // Tips数据
    async getTips(tipType, context = 'norway') {
        try {
            const result = await this.request(`/tips?type=${tipType}&context=${context}`);
            return result;
        } catch (error) {
            console.error('获取Tips失败:', error);
            return [];
        }
    }
}

// 创建全局实例
const api = new APIUtils();

// 兼容性函数 - 用于平滑迁移
const localStorageCompat = {
    // 用户位置
    async getItem(key) {
        // if (key === 'userLocation') {
        //     return await api.getUserLocation();
        // }
        // 其他localStorage操作保持原样
        return localStorage.getItem(key);
    },

    async setItem(key, value) {
        // if (key === 'userLocation') {
        //     await api.setUserLocation(value);
        // } else {
        //     localStorage.setItem(key, value);
        // }
        localStorage.setItem(key, value);
    },

    // 知识库项目
    async getKnowledgeItems() {
        return await api.getKnowledgeItems();
    },

    async saveKnowledgeItem(item) {
        return await api.createKnowledgeItem(item);
    },

    async deleteKnowledgeItem(itemId) {
        return await api.deleteKnowledgeItem(itemId);
    },

    // 家乡菜谱
    async getHometownRecipes() {
        return await api.getHometownRecipes();
    },

    async saveHometownRecipe(recipe) {
        return await api.createHometownRecipe(recipe);
    },

    async deleteHometownRecipe(recipeId) {
        return await api.deleteHometownRecipe(recipeId);
    },

    // 用户食材
    async getUserIngredients() {
        return await api.getUserIngredients();
    },

    async saveUserIngredients(ingredients) {
        return await api.addUserIngredients(ingredients);
    },

    async deleteUserIngredient(ingredientId) {
        return await api.deleteUserIngredient(ingredientId);
    },

    // 菜谱筛选条件
    async getRecipeFilters() {
        return await api.getRecipeFilters();
    },

    async setRecipeFilters(filters) {
        return await api.setRecipeFilters(filters);
    }
};