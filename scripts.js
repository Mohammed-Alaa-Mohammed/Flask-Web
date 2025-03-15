// تبديل الوضع الداكن/الفاتح
const toggleDarkMode = () => {
    const body = document.body;
    body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
};

// تحميل الوضع المفضل من LocalStorage
const loadDarkModePreference = () => {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
    }
};

// تهيئة الأحداث عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', () => {
    // تحميل الوضع الداكن/الفاتح
    loadDarkModePreference();

    // إضافة حدث لزر تبديل الوضع
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }
});