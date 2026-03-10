// Internationalization (i18n) module
const i18n = {
  currentLang: 'zh', // 默认中文

  translations: {
    zh: {
      // Header
      loading: '加载中...',
      noPapers: '当日无论文',
      loadingPaper: '正在加载论文...',
      noPapersForThisDate: '该日期无论文',

      // Categories
      all: '全部',
      category: '分类',
      filter: '筛选',

      // Search
      searchPlaceholder: '搜索论文标题、作者...',
      noResults: '未找到匹配的论文',

      // Paper Card
      details: '详情',
      relevance: '相关性',

      // Modal
      paperDetails: '论文详情',
      abstract: '摘要',
      tldr: 'TL;DR',
      motivation: '研究动机',
      method: '方法',
      result: '结果',
      conclusion: '结论',
      authors: '作者',
      categories: '分类',
      submitDate: '提交日期',
      comments: '评论',
      pdf: 'PDF',
      html: 'HTML',
      website: '网站',

      // Navigation
      prev: '上一条',
      next: '下一条',
      random: '随机',
      navigateHint: '← → 切换 • 空格随机',

      // Stats
      stats: '统计',

      // Settings
      settings: '设置',
      keywords: '关键词',
      authors_filter: '作者',
      save: '保存',
      clear: '清除',

      // Auth
      password: '密码',
      login: '登录',
      logout: '退出',

      // Date
      dateFormat: 'YYYY年M月D日',

      // Match reasons
      matched: '匹配',
      keywordMatch: '关键词',
      authorMatch: '作者',
      relevanceScore: '相关性分数',

      // Empty states
      noPapersForDate: '该日期无论文',
      noPapersFound: '未找到论文',

      // Tooltips
      calendar: '选择日期',
      statistics: '统计',
      settingsTooltip: '设置',
      language: '语言',

      // Date range
      loadingPapersFromTo: '正在加载从 {start} 到 {end} 的论文...',
    },
    en: {
      // Header
      loading: 'Loading...',
      noPapers: 'No papers for this date',
      loadingPaper: 'Loading paper...',
      noPapersForThisDate: 'No papers for this date',

      // Categories
      all: 'All',
      category: 'Category',
      filter: 'Filter',

      // Search
      searchPlaceholder: 'Search papers by title, author...',
      noResults: 'No matching papers found',

      // Paper Card
      details: 'Details',
      relevance: 'Relevance',

      // Modal
      paperDetails: 'Paper Details',
      abstract: 'Abstract',
      tldr: 'TL;DR',
      motivation: 'Motivation',
      method: 'Method',
      result: 'Result',
      conclusion: 'Conclusion',
      authors: 'Authors',
      categories: 'Categories',
      submitDate: 'Submit Date',
      comments: 'Comments',
      pdf: 'PDF',
      html: 'HTML',
      website: 'Website',

      // Navigation
      prev: 'Previous',
      next: 'Next',
      random: 'Random',
      navigateHint: '← → to navigate • space for random',

      // Stats
      stats: 'Statistics',

      // Settings
      settings: 'Settings',
      keywords: 'Keywords',
      authors_filter: 'Authors',
      save: 'Save',
      clear: 'Clear',

      // Auth
      password: 'Password',
      login: 'Login',
      logout: 'Logout',

      // Date
      dateFormat: 'MMMM D, YYYY',

      // Match reasons
      matched: 'Matched',
      keywordMatch: 'Keyword',
      authorMatch: 'Author',
      relevanceScore: 'Relevance Score',

      // Empty states
      noPapersForDate: 'No papers for this date',
      noPapersFound: 'No papers found',

      // Tooltips
      calendar: 'Select date',
      statistics: 'Statistics',
      settingsTooltip: 'Settings',
      language: 'Language',

      // Date range
      loadingPapersFromTo: 'Loading papers from {start} to {end}...',
    }
  },

  // 初始化语言设置
  init() {
    const savedLang = localStorage.getItem('preferredLanguage');
    if (savedLang) {
      this.currentLang = savedLang;
    } else {
      // 检测浏览器语言
      const browserLang = navigator.language.toLowerCase();
      if (browserLang.startsWith('zh')) {
        this.currentLang = 'zh';
      } else {
        this.currentLang = 'en';
      }
    }
    this.updateUI();
  },

  // 切换语言
  toggle() {
    this.currentLang = this.currentLang === 'zh' ? 'en' : 'zh';
    localStorage.setItem('preferredLanguage', this.currentLang);
    this.updateUI();
    this.updatePageTranslations();

    // 触发自定义事件，让其他组件可以响应语言变化
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang: this.currentLang } }));
  },

  // 获取翻译
  t(key, params = {}) {
    let text = this.translations[this.currentLang][key] || key;
    // 替换参数，如 {start}, {end}
    Object.keys(params).forEach(param => {
      text = text.replace(`{${param}}`, params[param]);
    });
    return text;
  },

  // 更新页面中所有标记了 data-i18n 属性的元素
  updatePageTranslations() {
    // 更新所有带 data-i18n 属性的元素
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      el.textContent = this.t(key);
    });

    // 更新所有带 data-i18n-placeholder 属性的元素
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      el.placeholder = this.t(key);
    });

    // 更新所有带 data-i18n-title 属性的元素
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      el.title = this.t(key);
    });
  },

  // 更新UI中的翻译文本
  updateUI() {
    // 更新语言切换按钮的 title
    const langBtn = document.getElementById('languageToggle');
    if (langBtn) {
      langBtn.title = this.t('language');
    }
  },

  // 获取当前语言
  getLang() {
    return this.currentLang;
  }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
  i18n.init();

  // 暴露到 window 对象，供其他脚本使用
  window.i18n = i18n;

  // 语言切换按钮点击事件
  const langBtn = document.getElementById('languageToggle');
  if (langBtn) {
    langBtn.addEventListener('click', () => {
      i18n.toggle();

      // 重新加载当前日期的论文数据
      if (typeof loadPapersByDate === 'function' && currentDate) {
        loadPapersByDate(currentDate);
      }
    });
  }
});
