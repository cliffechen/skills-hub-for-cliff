document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
    return false;
}, false);

document.addEventListener('keydown', function(e) {
    if(e.keyCode === 123) {
        e.preventDefault();
        return false;
    }
    if(e.ctrlKey && e.shiftKey && e.keyCode === 73) {
        e.preventDefault();
        return false;
    }
    if(e.ctrlKey && e.shiftKey && e.keyCode === 74) {
        e.preventDefault();
        return false;
    }
    if(e.ctrlKey && e.keyCode === 85) {
        e.preventDefault();
        return false;
    }
}, false);

(function detectDevTools() {
    const devtools = { isOpen: false, orientation: undefined };
    const threshold = 160;

    const emitEvent = (isOpen, orientation) => {
        if (devtools.isOpen !== isOpen || devtools.orientation !== orientation) {
            devtools.isOpen = isOpen;
            devtools.orientation = orientation;
        }
    };

    const checkDevTools = () => {
        const widthThreshold = window.outerWidth - window.innerWidth > threshold;
        const heightThreshold = window.outerHeight - window.innerHeight > threshold;
        const orientation = widthThreshold ? 'vertical' : 'horizontal';
        emitEvent(widthThreshold || heightThreshold, widthThreshold || heightThreshold ? orientation : null);
    };

    window.addEventListener('resize', checkDevTools);
    setInterval(checkDevTools, 5000);
})();

document.addEventListener('dragstart', function(e) {
    e.preventDefault();
    return false;
}, false);
