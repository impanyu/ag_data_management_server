const random = d3.randomNormal(0, 0.2);
const sqrt3 = Math.sqrt(3);
data = [].concat(
    Array.from({length: 300}, () => [random() + sqrt3, random() + 1, 0]),
    Array.from({length: 300}, () => [random() - sqrt3, random() + 1, 1]),
    Array.from({length: 300}, () => [random(), random() - 1, 2])
  );
var Tooltip;
function draw_2d_points(data){
   x_min = 10000;
   x_max = -10000;
   y_min = x_min;
   y_max = x_max;
   for(i in data){
      x_min = Math.min(x_min,data[i]["2d"][0]);
      y_min = Math.min(y_min,data[i]["2d"][1]);
      x_max = Math.max(x_max,data[i]["2d"][0]);
      y_max = Math.max(y_max,data[i]["2d"][1]);


   }


    height = d3.select("#map_main").node().getBoundingClientRect().height;
    width = d3.select("#map_main").node().getBoundingClientRect().width;
    k = height / width;


    x = d3.scaleLinear()
        .domain([x_min, x_max])
        .range([0, width])

    y = d3.scaleLinear()
        .domain([y_min, y_max])
        .range([height, 0])



    z = d3.scaleOrdinal()
        .domain(data.map(d => d["2d"][2]))
        .range(d3.schemeCategory10)

    xAxis = (g, x) => g
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisTop(x).ticks(12))
        .call(g => g.select(".domain").attr("display", "none"))

    yAxis = (g, y) => g
        .call(d3.axisRight(y).ticks(12 * k))
        .call(g => g.select(".domain").attr("display", "none"))


    grid = (g, x, y) => g
        .attr("stroke", "currentColor")
        .attr("stroke-opacity", 0.1)
        .call(g => g
          .selectAll(".x")
          .data(x.ticks(12))
          .join(
            enter => enter.append("line").attr("class", "x").attr("y2", height),
            update => update,
            exit => exit.remove()
          )
            .attr("x1", d => 0.5 + x(d))
            .attr("x2", d => 0.5 + x(d)))
        .call(g => g
          .selectAll(".y")
          .data(y.ticks(12 * k))
          .join(
            enter => enter.append("line").attr("class", "y").attr("x2", width),
            update => update,
            exit => exit.remove()
          )
            .attr("y1", d => 0.5 + y(d))
            .attr("y2", d => 0.5 + y(d)));

    const zoom = d3.zoom()
          .scaleExtent([0.5, 32])
          .on("zoom", zoomed);

    svg = d3.select("#files_plot")
        .append("svg")
         .attr("viewBox", [0, 0, width, height]);

      const gGrid = svg.append("g");

    /*
      const gDot = svg.append("g")
          .attr("fill", "none")
          .attr("stroke-linecap", "round");


      gDot.selectAll("path")
        .data(data)
        .join("path")
          .attr("d", d => `M${x(d[0])},${y(d[1])}h0`)
          .attr("stroke", d => z(d[2]))
          .attr("stroke-width", 20);
    */
          Tooltip = d3.select("#tooltip")
    .append("div")
    .style("opacity", 0)
    .attr("class", "tooltip")
    .style("background-color", "white")
    .style("border", "solid")
    .style("border-width", "2px")
    .style("border-radius", "5px")
    .style("padding", "5px");


      var mouseover = function(this,d) {
    Tooltip
      .style("opacity", 1)
    d3.select(this)
      .style("opacity", 1)
  };
  var mousemove = function(e,d) {
    Tooltip
      .html("name: "+d["name"]+"<br>"+"category: "+d["category"]+"<br>"+"label: "+d["label"]+"<br>"+"mode: "+d["mode"]+"<br>"+"format: "+d["format"])
      .style("left", (d3.pointer(e)[0]+50) + "px")
      .style("top", (d3.pointer(e)[1]) + "px")
  };
  var mouseleave = function(d) {
    Tooltip
      .style("opacity", 0)

  };

        // Add dots
        const gDot = svg.append('g')
        .selectAll("dot")
        .data(data)
        .join("circle")
            .attr("cx", function (d) {  return x(d["2d"][0]); } )
            .attr("cy", function (d) { return y(d["2d"][1]); } )
            .attr("r", 20)
            .attr("stroke","black")
            .attr("stroke-width",2)
            .style("fill", d => z(d["2d"][2]))
            .on("mouseover",function(){d3.select(this).attr("r",50);mouseover();})
            .on("mouseout",function(){d3.select(this).attr("r",20);mouseleave();})
            .on("mousemove",mousemove);



      const gx = svg.append("g");

      const gy = svg.append("g");

      svg.call(zoom).call(zoom.transform, d3.zoomIdentity);


        function zoomed({transform}) {
    const zx = transform.rescaleX(x).interpolate(d3.interpolateRound);
    const zy = transform.rescaleY(y).interpolate(d3.interpolateRound);
    gDot.attr("transform", transform).attr("stroke-width", 5 / transform.k);
    gx.call(xAxis, zx);
    gy.call(yAxis, zy);
    gGrid.call(grid, zx, zy);
  }
}



//draw_2d_points(data);