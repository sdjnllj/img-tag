// 全局状态
let state = {
    currentCategory: '',
    currentSearch: '',
    isLoading: false,
    images: [],
    categories: []
};

// DOM 元素
const elements = {
    imageGrid: document.getElementById('imageGrid'),
    categoriesContainer: document.getElementById('categories'),
    searchInput: document.getElementById('searchInput'),
    loadingTemplate: `
        <div class="loading">
            <div class="loading-spinner"></div>
        </div>
    `,
    errorTemplate: message => `
        <div class="error-message">
            ${message}
        </div>
    `
};

// 工具函数
const utils = {
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    processImagePath: (path) => {
        if (!path) return '';
        return path.replace(/^[/\\]+/, '').replace(/\\/g, '/');
    },

    showLoading: () => {
        state.isLoading = true;
        elements.imageGrid.innerHTML = elements.loadingTemplate;
    },

    showError: (message) => {
        elements.imageGrid.innerHTML = elements.errorTemplate(message);
    }
};

// API 请求函数
const api = {
    async fetchCategories() {
        try {
            const response = await fetch('/api/categories');
            if (!response.ok) throw new Error('Failed to fetch categories');
            return await response.json();
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    },

    async fetchImages() {
        const params = new URLSearchParams({
            category: state.currentCategory,
            search: state.currentSearch
        });
        try {
            const response = await fetch(`/api/images?${params}`);
            if (!response.ok) throw new Error('Failed to fetch images');
            return await response.json();
        } catch (error) {
            console.error('Error fetching images:', error);
            throw error;
        }
    }
};

// UI 渲染函数
const ui = {
    renderCategories() {
        const buttons = [
            `<button class="category-btn ${state.currentCategory === '' ? 'active' : ''}"
                     onclick="app.filterByCategory('')">
                全部
            </button>`
        ];

        state.categories.forEach(category => {
            buttons.push(`
                <button class="category-btn ${state.currentCategory === category ? 'active' : ''}"
                        onclick="app.filterByCategory('${category}')">
                    ${category}
                </button>
            `);
        });

        elements.categoriesContainer.innerHTML = buttons.join('');
    },

    renderImages() {
        if (!state.images.length) {
            elements.imageGrid.innerHTML = elements.errorTemplate('没有找到匹配的图片');
            return;
        }

        const cards = state.images.map(image => {
            const imagePath = utils.processImagePath(image.path);
            const imageUrl = `/images/${imagePath}`;
            const categories = image.categories || [];
            const aiTags = image.ai_tags || [];
            const technical = image.technical || {};

            return `
                <div class="image-card">
                    <div class="image-container">
                        <a href="${imageUrl}" data-fancybox="gallery" data-caption="${categories.join(', ')}">
                            <img src="${imageUrl}" 
                                 alt="${imagePath}"
                                 loading="lazy"
                                 onerror="this.onerror=null; this.src='/static/placeholder.png';">
                        </a>
                    </div>
                    <div class="image-info">
                        <div class="categories">
                            ${categories.map(cat => `
                                <span class="tag">${cat}</span>
                            `).join('')}
                        </div>
                        ${aiTags.length ? `
                            <div class="ai-tags">
                                ${aiTags.map(tag => `
                                    <span class="tag ai-tag" title="置信度: ${Math.round((tag.probability || 0) * 100)}%">
                                        ${tag.label}
                                    </span>
                                `).join('')}
                            </div>
                        ` : ''}
                        <div class="technical-info">
                            <small>${technical.width || 0} × ${technical.height || 0}</small>
                        </div>
                    </div>
                </div>
            `;
        });

        elements.imageGrid.innerHTML = cards.join('');
        
        // 初始化 Fancybox
        Fancybox.bind("[data-fancybox]", {
            Toolbar: {
                display: [
                    { id: "prev", position: "center" },
                    { id: "counter", position: "center" },
                    { id: "next", position: "center" },
                    "zoom",
                    "slideshow",
                    "fullscreen",
                    "download",
                    "close",
                ],
            },
        });
    }
};

// 应用主逻辑
const app = {
    async init() {
        try {
            utils.showLoading();
            state.categories = await api.fetchCategories();
            ui.renderCategories();
            await this.loadImages();
        } catch (error) {
            utils.showError('初始化失败，请刷新页面重试');
        }
    },

    async loadImages() {
        try {
            utils.showLoading();
            state.images = await api.fetchImages();
            ui.renderImages();
        } catch (error) {
            utils.showError('加载图片失败，请重试');
        } finally {
            state.isLoading = false;
        }
    },

    filterByCategory(category) {
        state.currentCategory = category;
        ui.renderCategories();
        this.loadImages();
    },

    handleSearch: utils.debounce(function(value) {
        state.currentSearch = value.trim();
        app.loadImages();
    }, 300)
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    // 设置搜索输入框事件监听
    elements.searchInput.addEventListener('input', (e) => {
        app.handleSearch(e.target.value);
    });

    // 初始化应用
    app.init();
});
