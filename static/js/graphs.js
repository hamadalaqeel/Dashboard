queue()
    .defer(d3.json, "/Loans/SummerTraining")
    .defer(d3.json, "static/geojson/us-states.json")
    .await(makeGraphs);

function makeGraphs(error, LoansJson, statesJson) {
    
    var ndx = crossfilter(LoansJson);

    var loanStatus = ndx.dimension(function(d) { return d["loan_status"]; });
    var paid = ndx.dimension(function(d) { return d.loan_status === "Fully Paid" ? 'Loss' : 'Gain';})
    var intRate = ndx.dimension(function(d) { return d["int_rate"]; });
    var fundedAmnt = ndx.dimension(function(d) { return d["funded_amnt"]; });
    var empLength = ndx.dimension(function(d) { return d["emp_length"]; });
    var annualInc  = ndx.dimension(function(d) { return d["annual_inc"]; });
    var numSats = ndx.dimension(function(d) { return d["num_sats"]; });
    var lastPymntAmnt = ndx.dimension(function(d) { return d["last_pymnt_amnt"]; });
    var avgCurBal = ndx.dimension(function(d) { return d["avg_cur_bal"]; });
    var addrState  = ndx.dimension(function(d) { return d["addr_state"]; });
    
    var all = ndx.groupAll();
    var numLoansByStatus = loanStatus.group(); 
    var numLoansByEmpLength = empLength.group();
    var numLoansByNumSats = numSats.group();
    var totalFundeedAmnt = ndx.groupAll().reduceSum(function(d) {return d["funded_amnt"];});
    var totalInterestRate = ndx.groupAll().reduceSum(function(d) {return d["int_rate"];});
    var countInterestRate = ndx.groupAll().reduceCount(function(d) {return d["int_rate"];});
    var avgInterestRate = totalInterestRate / countInterestRate;
    var loansVolumeByStates = addrState.group();
    var countLoans = numLoansByStatus.reduceCount().all();
    var counts = loansVolumeByStates.reduceCount().all();

    var meaninterestRate = ndx.groupAll().reduce(
        function (p, v) {
            ++p.n;
            p.tot += v.int_rate;
            return p;
        },
        function (p, v) {
            --p.n;
            p.tot -= v.int_rate;
            return p;
        },
        function () { return {n:0,tot:0}; }
    );
    var average = function(d) {
        return d.n ? (d.tot / d.n) : 0;
    };

    var countByState = {}; 
        
    Array.prototype.slice.call(counts).forEach(function(d) { countByState[d.key] = d.value; })
    
    var loansVolumeByStates = loansVolumeByStates.reduceSum(function(d, i) { 
        return d.int_rate / countByState[d.addr_state]; 
    });

    var empLengthD = ndx.dimension(function(d) {
        return d.emp_length;
    });

    var empLengthByStatus = empLengthD.group().reduce( 
        function(p, v) {
            if (isFullyPaid(v)) {
                p.totalFullyPaidE++;
            }
            if (isChargedOff(v)) {
                p.totalChargedOffE++;
            }
            return p;
        },
        function(p, v) {
            if (isFullyPaid(v)) {
                p.totalFullyPaidE--;
            }
            if (isChargedOff(v)) {
                p.totalChargedOffE--;
            }
            return p;
        },
        function() {
            return {
                totalFullyPaidE:0,
                totalChargedOffE:0,
            };
        }
);

    function isFullyPaid(v) {
        return v.loan_status === "Fully Paid" ;
    }
    function isChargedOff(v) {
        return v.loan_status === "Charged Off" ;
    }
    var sats = ndx.dimension(function(d) {
        return d.num_sats;
    });
    

    var crimeIncidentByYear = sats.group().reduce( 
            function(p, v) {
                if (isFullyPaid(v)) {
                    p.totalFullyPaid++;
                }
                if (isChargedOff(v)) {
                    p.totalChargedOff++;
                }
                return p;
            },
            function(p, v) {
                if (isFullyPaid(v)) {
                    p.totalFullyPaid--;
                }
                if (isChargedOff(v)) {
                    p.totalChargedOff--;
                }
                return p;
            },
            function() {
                return {
                    totalFullyPaid:0,
                    totalChargedOff:0,
                };
            }
    );
        
    var incidentChart = dc.barChart('#incident-chart');
    var boxChartEmpLength = dc.barChart('#empLength-chart');
    var loanStatusChart = dc.rowChart('#resource-type-row-chart');
    var usChart = dc.geoChoroplethChart('#us-chart');
    var numberOfLoans = dc.numberDisplay('#number-of-loans');
    var totalFundeedAmntND = dc.numberDisplay('#total-funded-amnt');
    var totalInterestRateND = dc.numberDisplay('#total-int-rate');

    numberOfLoans
        .formatNumber(d3.format(",d"))
        .valueAccessor(function(d){return d; })
        .group(all);

    totalFundeedAmntND
        .formatNumber(d3.format(",d"))
        .valueAccessor(function(d){return d; })
        .group(totalFundeedAmnt)
        .formatNumber(d3.format(".5s"));

    totalInterestRateND
        .group(meaninterestRate)
        .valueAccessor(average)
        .formatNumber(d3.format(".3g"));

    loanStatusChart
        .width(300)
        .height(250)
        .dimension(loanStatus)
        .group(numLoansByStatus)
        .xAxis().ticks(4);
/*
    empLengthChart
        .width(300)
        .height(250)
        .dimension(empLength)
        .group(numLoansByEmpLength)
        .xAxis().ticks(4);
*/
    usChart
        .width(1000)
        .height(500)
        .dimension(addrState)
        .group(loansVolumeByStates)
        .colors(["#E2F2FF", "#C4E4FF", "#9ED2FF", "#6BBAFF",  "#36A2FF"])
        .colorDomain([11, 16])
        .overlayGeoJson(statesJson["features"], "state", function (d) {
            return d.properties.name;
        })
        .projection(d3.geo.albersUsa()
                    .scale(900)
                    .translate([400, 200]))
        .title(function (p) {
            return "State: " + p["key"]
                    + "\n"
                    + "Average Interest Rate: " + p["value"] + " %";
        })

    usChart.legendables = function () {
        var range = usChart.colors().range()
        var domain = usChart.colorDomain()
        var step = 1
        var val = domain[0] 
            return range.map(function (d, i) {
                var legendable = {name: val + ' - ' + (val+step) + " %", chart: usChart};
                legendable.color = usChart.colorCalculator()(val);
                val += step
                return legendable;
            });
        }; 
            
    usChart.legend(
        dc.legend()
            .x(800)
            .y(70)
            .itemHeight(500/30)           
    );

    incidentChart
        .width(550)
        .height(300)
        .margins({top: 10, right: 50, bottom: 40, left: 40})
        .dimension(sats)
        .colors(["#E2F2FF", "#36A2FF"])
        .group(crimeIncidentByYear, "Charged Off")
        .valueAccessor(function(d) {
            return d.value.totalChargedOff;
        })
        .stack(crimeIncidentByYear, "Fully Paid", function(d){return d.value.totalFullyPaid;})
        .x(d3.scale.linear().domain([0,70]))
        .renderHorizontalGridLines(true)
        .centerBar(true)
        .elasticY(true)
        .legend(dc.legend().x(400).y(0))
        .xAxisLabel("Number of Satisfactory Accounts")
        .xAxis().ticks(6).tickFormat(d3.format("d"));



    
    boxChartEmpLength
        .width(550)
        .height(300)
        .margins({top: 40, right: 50, bottom: 40, left: 40})
        .dimension(empLengthD)
        .colors(["#E2F2FF", "#36A2FF"])
        .group(empLengthByStatus, "Charged Off")
        .valueAccessor(function(d) {
            return d.value.totalChargedOffE;
        })
        .stack(empLengthByStatus, "Fully Paid", function(d){return d.value.totalFullyPaidE;})
        .x(d3.scale.linear().domain([0,11]))
        .renderHorizontalGridLines(true)
        .centerBar(true)
        .elasticY(true)
        .legend(dc.legend().x(400).y(0))
        .xAxisLabel("Employment Length")
        .xAxis().ticks(6).tickFormat(d3.format("d"));

    dc.renderAll();

};