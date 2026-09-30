(function () {
    function initWatermark() {
        // 防止重复添加
        if (document.getElementById('wm_div_id')) return;

        // 1. 安全获取配置
        var currentScript = document.currentScript;
        
        // 获取 data-text，如果获取不到则使用默认值
        var textAttr = (currentScript && currentScript.getAttribute('data-text')) || "知识星球：Adobe of Amazon\n专享内容";
        var color = (currentScript && currentScript.getAttribute('data-color')) || "#000000";
        var alpha = 0.1; // 稍微调高一点透明度确保可见 (0.1 -> 0.15)
        var angle = -20;
        var fontSize = 18; 

        // --- 核心修复：更强的换行处理逻辑 ---
        // 1. .replace(/\\n/g, '\n'): 将用户输入的字符串 "\n" 替换为真实的换行符
        // 2. .split('\n'): 统一按照真实的换行符进行切割
        var lines = textAttr.replace(/\\n/g, '\n').split('\n');

        // 创建画板
        var canvas = document.createElement('canvas');
        canvas.width = 400; 
        canvas.height = 400; 
        var ctx = canvas.getContext('2d');

        // 样式
        ctx.font = fontSize + "px Microsoft Yahei";
        ctx.fillStyle = color;
        ctx.globalAlpha = alpha;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        // 移动中心点并旋转
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(angle * Math.PI / 180);

        // --- 绘制多行文字 ---
        var lineHeight = fontSize * 1.5; // 行高
        // 计算起始 Y 坐标，确保多行文字整体垂直居中
        var startY = -((lines.length - 1) * lineHeight) / 2;

        lines.forEach(function(line, index) {
            ctx.fillText(line, 0, startY + (index * lineHeight));
        });

        // 生成图片
        var base64Url = canvas.toDataURL();

        // 创建遮罩层
        var watermarkDiv = document.createElement('div');
        watermarkDiv.id = 'wm_div_id';
        var styleStr = "position:fixed;top:0;left:0;right:0;bottom:0;" +
                       "z-index:999999;" +
                       "pointer-events:none;" +
                       "background-repeat:repeat;" +
                       "background-image:url('" + base64Url + "');";
        
        watermarkDiv.setAttribute('style', styleStr);
        document.body.appendChild(watermarkDiv);
    }

    // 兼容多种加载状态
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initWatermark);
    } else {
        initWatermark();
    }
})();
