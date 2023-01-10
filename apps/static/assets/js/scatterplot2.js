const random = d3.randomNormal(0, 0.2);
const sqrt3 = Math.sqrt(3);
data = [].concat(
    Array.from({length: 300}, () => [random() + sqrt3, random() + 1, 0]),
    Array.from({length: 300}, () => [random() - sqrt3, random() + 1, 1]),
    Array.from({length: 300}, () => [random(), random() - 1, 2])
  );

function draw_2d_points(data){
   x_min = 10000;
   x_max = -10000;
   y_min = x_min;
   y_max = x_max;
   for(i in data){
      x_min = Math.min(x_min,data[i][0]);
      y_min = Math.min(y_min,data[i][1]);
      x_max = Math.max(x_max,data[i][0]);
      y_max = Math.max(y_max,data[i][1]);


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

    color_scale_map = {"CSV/Spreadsheet":1, "Image":2, "Other":3}

    z = d3.scaleOrdinal()
        .domain(data.map(d => {if(d["format"].length==0) return 0; else return color_scale_map[d["format"][0]];}))
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
        // Add dots
        const gDot = svg.append('g')
        .selectAll("dot")
        .data(data)
        .join("circle")
            .attr("cx", function (d) { console.info(d); return x(d["2d"][0]); } )
            .attr("cy", function (d) {console.info(d);  return y(d["2d"][1]); } )
            .attr("r", 10)
            .attr("stroke","black")
            .attr("stroke-width",2)
            .style("fill", d => z(d[2]));

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