function initNode(node, parentWidth, parentHeight) {
    var bornScale = normalizeBorn(node.born)
    applyScale(node, bornScale)
    fixY(node, bornScale, parentWidth, parentHeight)
}

function applyScale(node, bornScale) {
    node.score = node.score * 10000
}

function normalizeBorn(born) {
    var now = Date.now()
    var delta = (now / 1000) - born
    return delta / (3600 * 24 * 365)
}

function fixY(node, bornScale, parentWidth, parentHeight) {
    node.fy = bornScale
}

/*
graph.nodes.forEach(function(node) {
    if(node.born >= -62167219200 && node.born <= -61157376000) {
        console.log(node)
    }
    node.score = node.score/10000
})
*/