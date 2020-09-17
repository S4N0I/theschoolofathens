function initGraph(graph) {
    for (var i = 0; i < graph.nodes.length; i++) {
        // normalize y coordinate to years born before the year 2000
        const yearsBornBefore2k = calcYearsBornBefore2k(graph.nodes[i].born)
        fixY(graph.nodes[i], yearsBornBefore2k)
    }
}

const yearInSeconds = 3600 * 24 * 365
const yearInMillis = yearInSeconds * 1000
const now = Date.now()
const currentYear = now / yearInMillis + 1970;

function calcYearsBornBefore2k(born) {
    const yearsBornBeforeToday = ((now / 1000) - born) / yearInSeconds
    return yearsBornBeforeToday - (currentYear - 2000)
}

function fixY(node, y) {
    node.savedFy = y
    node.fy = y
}