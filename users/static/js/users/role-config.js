

function revealElementsByGroup(userData) {

    const GROUP_ELEMENT_MAP = {
         'DEVELOPER': ['btnSubmitReport', 'btnAPI', 'btnUsers'],
         'ADMINISTRATOR' : ['btnUsers'],
    };
    if (!userData?.groups || !Array.isArray(userData.groups)) {
        console.warn('⚠️ Invalid or missing userData.groups');
        return;
    }

    const normalizedGroups = userData.groups.map(g => g.trim());
    const isDeveloper = normalizedGroups.includes('Developer');

    const elementIdsToReveal = new Set();

    if (isDeveloper) {
        Object.values(GROUP_ELEMENT_MAP).flat().forEach(id => elementIdsToReveal.add(id));
        console.log('👨‍💻 Developer detected — revealing all mapped elements.');
    } else {
        normalizedGroups.forEach(group => {
          (GROUP_ELEMENT_MAP[group] || []).forEach(id => elementIdsToReveal.add(id));
    });
    }

    elementIdsToReveal.forEach(selector => {
        const isClass = selector.startsWith('.');
        const $el = isClass ? $(selector) : $('#' + selector);
        if ($el.length) {
            // Check if parent element is visible
            $el.each(function () {
                $(this).removeClass('d-none').css('display', ''); // 🔁 force display if needed
            });
            console.log(`✅ Revealed ${isClass ? selector : '#' + selector}`);
        }
    });

}
