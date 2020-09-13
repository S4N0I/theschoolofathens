// if both d3v3 and d3v4 are loaded, we'll assume
// that d3v4 is called d3v4, otherwise we'll assume
// that d3v4 is the default (d3)
if (typeof d3v4 == 'undefined')
    d3v4 = d3;

var link = null;
var node = null;
var yAxisG = null;
var simulation = null;
var selectedNode = null;
var clippingToTimeline = true;

function createV4SelectableForceDirectedGraph(graph, parentWidth, parentHeight) {

    var svg = d3v4.select('svg')
    .attr('width', parentWidth)
    .attr('height', parentHeight)

    // remove any previous graphs
    svg.selectAll('.g-main').remove();

    var gMain = svg.append('g')
    .classed('g-main', true)

    var rect = gMain.append('rect')
    .classed('graph-background', true)
    .attr('width', parentWidth)
    .attr('height', parentHeight)

    var initYScale = 0.12
    var initXTransform = parentWidth / 2 - 100; // best guess for now
    var initYTransform = parentHeight / 3;
    var gDraw = gMain.append('g')
    .attr("transform","translate("+ initXTransform + ", " + initYTransform + ") scale(" + initYScale + ")");

    // Add Y axis
    var yScale = d3v4.scaleLinear()
    .domain([parentHeight - 96, 96])
    .range([parentHeight - 96, 96]);

    var yAxis = d3v4.axisLeft(yScale)
    .ticks(10)
    .tickFormat(function(d) {
        var yearsAd = Math.floor(2000 - d);
        if(yearsAd > 0) {
            return yearsAd + "";
        } else {
            return yearsAd + " BC"
        }
    });
    
    yAxisG = gMain.append("g")
    .classed('y-axis', true)
    .call(yAxis)
    .attr("transform",
    "translate(" + 128 + "," + 0 + ")");

    var zoom = d3v4.zoom()
    .on('zoom', zoomed);

    gMain.call(zoom).call(zoom.transform, d3v4.zoomIdentity.translate(initXTransform, initYTransform).scale(initYScale));


    function zoomed() {
        gDraw.attr('transform', d3v4.event.transform);

        // recover the new scale
        var newY = d3v4.event.transform.rescaleY(yScale);
        // update axes with these new boundaries
        yAxisG.call(d3v4.axisLeft(newY)
        .ticks(10)
        .tickFormat(function(d) {
            var yearsAd = Math.floor(2000 - d);
            if(yearsAd >= 0) {
                return yearsAd + "";
            } else {
                return Math.abs(yearsAd) + " BC"
            }
        }))
    }

    var nodes = {};
    for (var i = 0; i < graph.nodes.length; i++) {
        nodes[graph.nodes[i].id] = graph.nodes[i];
    }

    link = gDraw.append("g")
        .attr("class", "link")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", function(d) { return Math.sqrt(d.value); })
        .attr("stroke", function(d){ return "#dff4f5";});

    node = gDraw.append("g")
        .attr("class", "node")
        .selectAll("circle")
        .data(graph.nodes)
        .enter().append("circle")
        .attr("r", function(d) { 
                return Math.sqrt(d.score*3.14);
        })
        .attr("fill", function(d) { return "#1f77b4";})
        .call(d3v4.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

      
    // add titles for mouseover blurbs
    node.append("title")
        .text(function(d) { 
            if ('name' in d)
                return d.name;
            else
                return d.id; 
        });

    simulation = d3v4.forceSimulation()
        .force("link", d3v4.forceLink()
                .id(function(d) { return d.id; })
                .distance(function(d) { 
                    return 100;
                })
              )
        .force("charge", d3v4.forceManyBody().distanceMin(100).strength(-2000))
        .force("center", d3v4.forceCenter(parentWidth / 2, parentHeight / 2))
        .force("x", d3v4.forceX(parentWidth/2))
        .force("y", d3v4.forceY(parentHeight/2));

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);

    function ticked() {
        // update node and line positions at every step of 
        // the force simulation
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });

        node.attr("cx", function(d) { return d.x; })
            .attr("cy", function(d) { return d.y; });
    }

    rect.on('click', () => {
        resetSelectedNode(node, link);
    });


    function dragstarted(d) {
        if (!d3v4.event.active) simulation.alphaTarget(0.9).restart();

        setSelectedNode(d, node, link);

        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(d) {
        d.fx += d3v4.event.dx;
        d.fy += d3v4.event.dy;
    }

    function dragended(d) {
        if (!d3v4.event.active) simulation.alphaTarget(0);
        d.fx = null;
        if(clippingToTimeline) {
            d.fy = d.savedFy;
        } else {
            d.fy = null;
        }
    }

    return graph;
};

function setSelectedNode(node, allNodes, allLinks) {
    if(selectedNode === node) return;
    if(selectedNode != null) {
        allLinks.classed("influences", false);
        allLinks.classed("influenced-by", false);
    }
    allNodes.classed("selected", function(n){ return n.id == node.id});
    allLinks.classed("influenced-by", function(l){ return l.source.id == node.id})
    allLinks.classed("influences", function(l){ return l.target.id == node.id})
    showPhilosopherInfo(node);
    selectedNode = node;
}

function resetSelectedNode(allNodes, allLinks) {
    selectedNode = null;
    allNodes.classed("selected", false);
    allLinks.classed("influences", false);
    allLinks.classed("influenced-by", false);
}

function showPhilosopherInfo(node) {
    $('.modal').modal('open');
    $('#philosopherImg').attr("src", node.img);
    $('#philosopherName').attr("href", "https://en.wikipedia.org/?curid=" + node.id);
    $('#philosopherName').text(node.name);
    $('#philosopherDescription').text("")
    var summaryUrl = "https://en.wikipedia.org/w/api.php?format=json&origin=*&action=query&prop=extracts&exintro&explaintext&redirects=1&pageids=" + node.id;
    fetch(summaryUrl)
    .then(response => response.json())
    .then(json => $('#philosopherDescription').text(json.query.pages[node.id].extract));
}

function clipNodesToTimeline(shouldClip) {
    if(shouldClip) {
        clippingToTimeline = true;
        yAxisG.attr("opacity", 1)
        simulation.stop();
        node.each(function(d) {
            d.fy = d.savedFy;
        })
        simulation.alpha(1).restart();
    } else {
        clippingToTimeline = false;
        yAxisG.attr("opacity", 0)
        simulation.stop();
        node.each(function(d) { 
            d.fy = null;
        })
        simulation.alpha(1).restart();
    }
}

function onClickClipToTimeline() {
    var checkBox = document.getElementById("clipToTimelineCheckbox");
    clipNodesToTimeline(checkBox.checked);
}

function searchByName() {
    var searchTerm = document.getElementById("search").value;
    if(searchTerm.length == 0) {
        node.classed("search-match", false);
        return;
    };
    node.classed("search-match", function(n){
        return n.name.toLowerCase().includes(searchTerm.toLowerCase());
    });
}