/**
 * 主要 JavaScript 文件
 * 提供通用函式與工具
 */

// API 基礎 URL
const API_BASE_URL = '';

/**
 * 顯示 Toast 通知
 * @param {string} message - 訊息內容
 * @param {string} type - 類型 (success/danger/warning/info)
 */
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');

    if (!toastContainer) {
        console.error('Toast container not found');
        return;
    }

    const toastId = `toast-${Date.now()}`;
    const bgColor = {
        'success': 'bg-success',
        'danger': 'bg-danger',
        'warning': 'bg-warning',
        'info': 'bg-info'
    }[type] || 'bg-primary';

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white ${bgColor} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHtml);

    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 3000
    });

    toast.show();

    // 自動移除 DOM 元素
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

/**
 * 格式化數字
 * @param {number} num - 數字
 * @param {number} decimals - 小數位數
 * @returns {string} 格式化的數字字符串
 */
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined || isNaN(num)) {
        return '-';
    }
    return parseFloat(num).toLocaleString('zh-TW', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

/**
 * 格式化日期
 * @param {string|Date} dateInput - 日期
 * @returns {string} 格式化的日期字符串
 */
function formatDate(dateInput) {
    if (!dateInput) return '-';

    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;

    if (isNaN(date.getTime())) {
        return '-';
    }

    return date.toLocaleDateString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * 格式化日期時間
 * @param {string|Date} dateInput - 日期時間
 * @returns {string} 格式化的日期時間字符串
 */
function formatDateTime(dateInput) {
    if (!dateInput) return '-';

    const date = typeof dateInput === 'string' ? new Date(dateInput) : dateInput;

    if (isNaN(date.getTime())) {
        return '-';
    }

    return date.toLocaleString('zh-TW', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 處理 API 錯誤
 * @param {Error} error - 錯誤對象
 * @returns {string} 錯誤訊息
 */
function handleApiError(error) {
    console.error('API Error:', error);

    if (error.response) {
        // 服務器響應錯誤
        if (error.response.data && error.response.data.error) {
            return error.response.data.error.message;
        }
        return `錯誤 ${error.response.status}: ${error.response.statusText}`;
    } else if (error.request) {
        // 請求發送但無響應
        return '無法連接到服務器，請檢查網路連接';
    } else {
        // 其他錯誤
        return error.message || '發生未知錯誤';
    }
}

/**
 * 防抖函數
 * @param {Function} func - 要執行的函數
 * @param {number} wait - 等待時間（毫秒）
 * @returns {Function} 防抖後的函數
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 節流函數
 * @param {Function} func - 要執行的函數
 * @param {number} limit - 限制時間（毫秒）
 * @returns {Function} 節流後的函數
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 複製文字到剪貼板
 * @param {string} text - 要複製的文字
 * @returns {Promise<boolean>} 是否成功
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('已複製到剪貼板', 'success');
        return true;
    } catch (err) {
        console.error('複製失敗:', err);
        showToast('複製失敗', 'danger');
        return false;
    }
}

/**
 * 驗證股票代號格式
 * @param {string} ticker - 股票代號
 * @returns {boolean} 是否有效
 */
function validateTicker(ticker) {
    if (!ticker) return false;
    ticker = ticker.trim();
    return /^[0-9]{4,6}$/.test(ticker);
}

/**
 * 顯示確認對話框
 * @param {string} message - 訊息
 * @returns {boolean} 使用者選擇
 */
function confirmDialog(message) {
    return confirm(message);
}

/**
 * 滾動到頁面頂部
 */
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * 滾動到元素
 * @param {string} elementId - 元素 ID
 */
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * 顯示/隱藏元素
 * @param {string} elementId - 元素 ID
 * @param {boolean} show - 是否顯示
 */
function toggleElement(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

/**
 * 啟用/禁用按鈕
 * @param {string} buttonId - 按鈕 ID
 * @param {boolean} enable - 是否啟用
 */
function toggleButton(buttonId, enable) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = !enable;
    }
}

// 全域錯誤處理
window.addEventListener('error', function(event) {
    console.error('全域錯誤:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('未處理的 Promise 拒絕:', event.reason);
});

// 頁面載入完成事件
document.addEventListener('DOMContentLoaded', function() {
    console.log('Buy Tracer Web - 頁面載入完成');

    // 初始化所有 tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 初始化所有 popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Plotly 圖表響應式處理
window.addEventListener('resize', debounce(function() {
    // 重新調整所有 Plotly 圖表大小
    const chartIds = ['candlestickChart', 'volumeChart', 'macdChart'];
    chartIds.forEach(function(chartId) {
        const element = document.getElementById(chartId);
        if (element && typeof Plotly !== 'undefined') {
            Plotly.Plots.resize(element);
        }
    });
}, 250));

// 導出函式（如果使用模組化）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        formatNumber,
        formatDate,
        formatDateTime,
        handleApiError,
        debounce,
        throttle,
        copyToClipboard,
        validateTicker,
        confirmDialog,
        scrollToTop,
        scrollToElement,
        toggleElement,
        toggleButton
    };
}
