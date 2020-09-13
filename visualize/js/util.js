function initNode(node, parentWidth, parentHeight) {
    var bornScale = normalizeBorn(node.born)
    applyScale(node, bornScale)
    fixY(node, bornScale, parentWidth, parentHeight)
}

function applyScale(node, bornScale) {
    node.score = node.score * 50000
}

var now = Date.now()
var deltaTo2k = now / (1000 * 3600 * 24 * 365) + 1970 - 2000;

function normalizeBorn(born) {
    // todo make less hacky
    var delta = (now / 1000) - born
    return delta / (3600 * 24 * 365) - deltaTo2k
}

function fixY(node, bornScale, parentWidth, parentHeight) {
    // todo maybe move to dragstarted for better intuition
    node.savedFy = bornScale
    node.fy = bornScale
}