document.addEventListener("DOMContentLoaded", function () {
    let pageGroup = document.body.getAttribute("data-page-group");
    let savedLang = localStorage.getItem("language_" + pageGroup) || "ar";

    fetch(`/get_translations/${savedLang}`)
        .then(response => response.json())
        .then(data => {
            updateTranslations(data.translations);
        });
});

function changeLanguage(lang, group) {
    localStorage.setItem("language_" + group, lang);

    fetch(`/change_language/${lang}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateTranslations(data.translations);
                reloadGroupPages(group);
            }
        });
}

function updateTranslations(translations) {
    document.querySelectorAll("[data-translate]").forEach(element => {
        let key = element.getAttribute("data-translate");
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });
}

function reloadGroupPages(group) {
    let pagesToReload = {
        "group1": ["/student", "/buttons", "/manual_input"],
        "group2": ["/Login_tudent_space", "/lessonss", "/announcement_list"]
    };

    if (pagesToReload[group]) {
        pagesToReload[group].forEach(page => {
            fetch(page)
                .then(response => response.text())
                .then(html => {
                    let parser = new DOMParser();
                    let doc = parser.parseFromString(html, "text/html");
                    updateTranslations(doc);
                });
        });
    }
}
