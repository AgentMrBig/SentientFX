const margin = { top: 20, right: 60, bottom: 30, left: 60 };
const padding = 10;
let width = window.innerWidth - margin.left - margin.right - padding * 2;
let height = window.innerHeight - margin.top - margin.bottom - padding * 2;

const svgEl = d3.select("#chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right + padding * 2)
  .attr("height", height + margin.top + margin.bottom + padding * 2)
  .style("margin", padding + "px");

const svg = svgEl.append("g")
  .attr("transform", `translate(${margin.left + padding},${margin.top + padding})`);

let chartArea = svg.append("g");

fetch("../data/market_snapshot_history.json")
  .then(res => res.json())
  .then(data => {
    data.forEach(d => {
      d.timestamp = new Date(d.timestamp);
      d.open = +d.open;
      d.high = +d.high;
      d.low = +d.low;
      d.close = +d.close;
      d.ma10 = +d.ma10;
      d.bb_upper = +d.bb_upper;
      d.bb_lower = +d.bb_lower;
    });

    const last = data[data.length - 1];

    let xDomain = d3.extent(data, d => d.timestamp);
    let yDomain = [
      d3.min(data, d => d.bb_lower),
      d3.max(data, d => d.bb_upper)
    ];

    const fullX = d3.scaleTime().domain(xDomain).range([0, width]);
    const fullY = d3.scaleLinear().domain(yDomain).range([height, 0]);

    const gx = svg.append("g").attr("transform", `translate(0,${height})`);
    gx.raise();
    const gy = svg.append("g").attr("transform", `translate(${width},0)`);

    svg.append("g")
      .call(d3.axisLeft(fullY).tickSize(-width).tickFormat(""))
      .attr("stroke-opacity", 0.1);

    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(fullX).tickSize(-height).tickFormat(""))
      .attr("stroke-opacity", 0.1);

    const overlay = svg.append("g");
    const crosshair = overlay.append("g").style("display", "none");
    const crossV = crosshair.append("line").attr("class", "crosshair-line").attr("y1", 0).attr("y2", height);
    const crossH = crosshair.append("line").attr("class", "crosshair-line").attr("x1", 0).attr("x2", width);

    const priceBox = overlay.append("g").style("display", "none");
    priceBox.append("rect").attr("class", "tooltip-box").attr("width", 60).attr("height", 16);
    const priceText = priceBox.append("text").attr("class", "tooltip-text").attr("x", 30).attr("y", 12).attr("dy", "0.35em");

    const timeBox = overlay.append("g").style("display", "none");
    timeBox.append("rect").attr("class", "tooltip-box").attr("width", 90).attr("height", 16);
    timeBox.raise();
    const timeText = timeBox.append("text").attr("class", "tooltip-text").attr("x", 45).attr("y", 12).attr("dy", "0.35em");

    svg.append("text")
      .attr("x", 0)
      .attr("y", 60)
      .attr("fill", "#888")
      .attr("font-size", "12px")
      .text("Indicators: MA(10), BB(20)");

    function redraw(xDomainNew, yDomainNew) {
      chartArea.selectAll("*").remove();

      const x = d3.scaleTime().domain(xDomainNew).range([0, width]);
      const y = d3.scaleLinear().domain(yDomainNew).range([height, 0]);

      gx.call(d3.axisBottom(x));
      gy.call(d3.axisRight(y));

      const visibleData = data.filter(d =>
        d.timestamp >= x.domain()[0] && d.timestamp <= x.domain()[1]
      );

      const candleWidth = (width) / visibleData.length * 0.7;

      chartArea.selectAll("line.stem")
        .data(visibleData)
        .enter().append("line")
        .attr("class", "candle stem")
        .attr("x1", d => x(d.timestamp))
        .attr("x2", d => x(d.timestamp))
        .attr("y1", d => y(d.high))
        .attr("y2", d => y(d.low))
        .classed("up", d => d.close >= d.open)
        .classed("down", d => d.close < d.open);

      chartArea.selectAll("rect.body")
        .data(visibleData)
        .enter().append("rect")
        .attr("x", d => x(d.timestamp) - candleWidth / 2)
        .attr("y", d => y(Math.max(d.open, d.close)))
        .attr("width", candleWidth)
        .attr("height", d => Math.abs(y(d.open) - y(d.close)))
        .attr("class", "candle body")
        .classed("up", d => d.close >= d.open)
        .classed("down", d => d.close < d.open);

      chartArea.append("path")
        .datum(visibleData)
        .attr("class", "ma-line")
        .attr("d", d3.line()
          .x(d => x(d.timestamp))
          .y(d => y(d.ma10))
          .curve(d3.curveCatmullRom.alpha(0.5)));

      chartArea.append("path")
        .datum(visibleData)
        .attr("class", "bb-upper")
        .attr("d", d3.line().x(d => x(d.timestamp)).y(d => y(d.bb_upper)));

      chartArea.append("path")
        .datum(visibleData)
        .attr("class", "bb-lower")
        .attr("d", d3.line().x(d => x(d.timestamp)).y(d => y(d.bb_lower)));

      chartArea.append("line")
        .attr("class", "crosshair-line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", y(last.close))
        .attr("y2", y(last.close));

      chartArea.append("rect")
        .attr("x", width)
        .attr("y", y(last.close) - 8)
        .attr("width", 60)
        .attr("height", 16)
        .attr("class", "current-price-box");

      chartArea.append("text")
        .attr("x", width + 30)
        .attr("y", y(last.close) + 4)
        .attr("class", "current-price-text")
        .text(last.close.toFixed(3));
    }

    let currentXDomain = fullX.domain();
    let currentYDomain = fullY.domain();
    redraw(currentXDomain, currentYDomain);

    svg.append("rect")
      .attr("width", width)
      .attr("height", height)
      .style("fill", "none")
      .style("pointer-events", "all")
      .on("mouseover", () => {
        crosshair.style("display", null);
        priceBox.style("display", null);
        timeBox.style("display", null);
      })
      .on("mouseout", () => {
        crosshair.style("display", "none");
        priceBox.style("display", "none");
        timeBox.style("display", null);
      })
      .on("mousemove", function (event) {
        const [mx, my] = d3.pointer(event);
        const x = d3.scaleTime().domain(currentXDomain).range([0, width]);
        const y = d3.scaleLinear().domain(currentYDomain).range([height, 0]);
        const xVal = x.invert(mx);
        const yVal = y.invert(my);

        crossV.attr("x1", mx).attr("x2", mx);
        crossH.attr("y1", my).attr("y2", my);

        priceBox.attr("transform", `translate(${width},${my - 8})`);
        priceText.text(yVal.toFixed(3));

        timeBox.attr("transform", `translate(${mx - 45},${height})`);
        timeText.text(d3.timeFormat("%H:%M:%S")(xVal));
      });

    svgEl.call(
      d3.zoom()
        .scaleExtent([1, 40])
        .on("zoom", function (event) {
          const t = event.transform;
          currentXDomain = t.rescaleX(fullX).domain();
          currentYDomain = t.rescaleY(fullY).domain();
          redraw(currentXDomain, currentYDomain);
        })
    );
  });
