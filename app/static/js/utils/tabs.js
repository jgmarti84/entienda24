function toggleProfileTabs() {
    const tabs = $(".tabs li")
    const tabContentBoxes = $("#tab-settings-content > div")
    $(tabs).each(function(tabIndex0, tabElement0) {
        $(tabElement0).click(function() {
            $(tabs).each(function(tabIndex1, tabElement1) {
                $(tabElement1).removeClass("is-active");
            })
            $(tabElement0).addClass("is-active");
            const target = $(tabElement0).data('target');
            $(tabContentBoxes).each(function(contentIndex, contentElement) {
                if ($(contentElement).attr('id') === target) {
                    $(contentElement).removeClass("is-hidden")
                } else {
                    $(contentElement).addClass("is-hidden")
                }
            })
        })
    })
}