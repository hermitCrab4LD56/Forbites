// API工具类 - 用于与后端通信，替换localStorage操作
class APIUtils {
    constructor() {
        this.baseURL = 'http://localhost:5001/api';
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
    async getUserLocation() {
        try {
            const result = await this.request('/user/location');
            return result.location;
        } catch (error) {
            console.error('获取用户位置失败:', error);
            return null;
        }
    }

    async setUserLocation(location) {
        try {
            const result = await this.request('/user/location', {
                method: 'POST',
                body: JSON.stringify({ location })
            });
            return result;
        } catch (error) {
            console.error('设置用户位置失败:', error);
            throw error;
        }
    }

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

    // 用户食材管理
    async getUserIngredients() {
        try {
            const result = await this.request('/user/ingredients');
            return result;
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

    // 菜谱筛选条件管理
    async getRecipeFilters() {
        try {
            const result = await this.request('/recipe/filters');
            return result;
        } catch (error) {
            console.error('获取菜谱筛选条件失败:', error);
            return {};
        }
    }

    async setRecipeFilters(filters) {
        try {
            const result = await this.request('/recipe/filters', {
                method: 'POST',
                body: JSON.stringify(filters)
            });
            return result;
        } catch (error) {
            console.error('设置菜谱筛选条件失败:', error);
            throw error;
        }
    }

    // 语音识别
    async recognizeVoice(audioBlob) {
        try {
            const formData = new FormData();
            formData.append('audio', audioBlob);
            
            const response = await fetch(`${this.baseURL}/pantry/voice_recognize`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
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
        if (key === 'userLocation') {
            return await api.getUserLocation();
        }
        // 其他localStorage操作保持原样
        return localStorage.getItem(key);
    },

    async setItem(key, value) {
        if (key === 'userLocation') {
            await api.setUserLocation(value);
        } else {
            localStorage.setItem(key, value);
        }
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