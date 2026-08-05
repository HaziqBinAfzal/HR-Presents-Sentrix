(() => {
    "use strict";

    const legacyNames = [
        ["CodeSentinel AI", "Sentrix"],
        ["CodeSentinelAI", "Sentrix"],
        ["Code Sentinel AI", "Sentrix"],
        ["CodeSentinel", "Sentrix"],
    ];

    document.title = legacyNames.reduce(
        (title, [legacy, current]) => title.replaceAll(legacy, current),
        document.title,
    );

    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
    );

    const textNodes = [];
    while (walker.nextNode()) {
        textNodes.push(walker.currentNode);
    }

    for (const node of textNodes) {
        let value = node.nodeValue;
        for (const [legacy, current] of legacyNames) {
            value = value.replaceAll(legacy, current);
        }
        node.nodeValue = value;
    }

    const providerHeadings = [...document.querySelectorAll("h1, h2, h3, h4, h5, h6")];
    for (const heading of providerHeadings) {
        if (heading.textContent.trim().toLowerCase().includes("ai provider (byok)")) {
            const column = heading.closest(".col-lg-6, .col-md-6, .card");
            if (column) {
                column.remove();
            }
        }
    }
})();
