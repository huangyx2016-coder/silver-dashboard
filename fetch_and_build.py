"""Fetch silver data from main dashboard, build standalone page."""
import json
from datetime import datetime
import requests

SILVER_DATA_URL = "https://huangyx2016-coder.github.io/lingxing-dashboard/silver_data.json"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>银饰订单 - 店铺明细</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" onerror="var s=document.createElement('script');s.src='https://unpkg.com/chart.js@4.4.0/dist/chart.umd.min.js';document.head.appendChild(s);"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; background:#f0f2f5; color:#333; padding:16px; }
.header { text-align:center; margin-bottom:16px; }
.header h1 { font-size:22px; color:#1a1a2e; }
.header p { color:#666; margin-top:2px; font-size:12px; }
.card { background:#fff; border-radius:10px; padding:14px; box-shadow:0 2px 6px rgba(0,0,0,0.06); margin-bottom:14px; }
.card h2 { font-size:14px; margin-bottom:8px; border-bottom:2px solid #70AD47; padding-bottom:5px; }
.table-wrap { max-height:600px; overflow-y:auto; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th { background:#70AD47; color:#fff; padding:5px 3px; position:sticky; top:0; z-index:1; text-align:center; white-space:nowrap; }
td { padding:3px; text-align:center; border-bottom:1px solid #eee; }
tr:hover td { background:#f5f7fa; }
td:first-child { text-align:left; font-weight:500; }
.num { text-align:right; }
.total-row td { font-weight:bold; background:#FFF2CC; border-top:2px solid #70AD47; }
.grid { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
.chart-wrap { position:relative; height:350px; }
.summary-bar { display:flex; gap:14px; margin-bottom:14px; }
.summary-item { flex:1; background:#fff; border-radius:10px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.06); text-align:center; }
.summary-item .value { font-size:22px; font-weight:bold; color:#70AD47; }
.summary-item .label { font-size:10px; color:#888; margin-top:1px; }
.footer { text-align:right; color:#aaa; font-size:10px; margin-top:8px; }
</style>
</head>
<body>
<div class="header"><h1>银饰订单 - 店铺明细</h1><p id="dateRange"></p></div>
<div class="summary-bar" id="sm"></div>
<div class="grid">
  <div class="card"><h2>银饰店铺 Top 10</h2><div class="chart-wrap"><canvas id="barChart"></canvas></div></div>
  <div class="card"><h2>店铺订单占比</h2><div class="chart-wrap"><canvas id="pieChart"></canvas></div></div>
</div>
<div class="card"><h2>全部银饰店铺</h2><div class="table-wrap" id="ordersTbl">加载中...</div></div>
<div class="card"><h2>FBA库存</h2><div class="table-wrap" id="stockTbl">加载中...</div></div>
<div class="footer">数据更新: DATA_TIME | 页面生成: NOW</div>

<script>
var LX = __DATA__;

(function(){
  var dates = LX.dates;
  var allStores = Object.entries(LX.orders).sort(function(a,b){ return b[1].total - a[1].total; });
  var totalOrders = LX.total_orders;

  // Header
  document.getElementById('dateRange').textContent = dates[0] + ' — ' + dates[dates.length-1] + ' | ' + totalOrders.toLocaleString() + ' 单 | ' + LX.shops_count + ' 店铺';

  // Summary
  var stockKeys = Object.keys(LX.warehouse_stock || {});
  var stockAvail = 0;
  stockKeys.forEach(function(k){ stockAvail += (LX.warehouse_stock[k].available || 0); });
  document.getElementById('sm').innerHTML =
    '<div class="summary-item"><div class="value">'+totalOrders.toLocaleString()+'</div><div class="label">银饰总订单</div></div>'+
    '<div class="summary-item"><div class="value">'+LX.shops_count+'</div><div class="label">店铺数</div></div>'+
    '<div class="summary-item"><div class="value">'+stockAvail.toLocaleString()+'</div><div class="label">FBA可售库存</div></div>';

  // Bar chart: Top 10
  if(typeof Chart!=='undefined'){
    var top10 = allStores.slice(0,10);
    new Chart(document.getElementById('barChart'),{type:'bar',
      data:{labels:top10.map(function(x){return x[0].length>16?x[0].slice(0,15)+'...':x[0];}),
            datasets:[{data:top10.map(function(x){return x[1].total;}), backgroundColor:'#70AD47', borderRadius:3}]},
      options:{responsive:true, maintainAspectRatio:false, indexAxis:'y', plugins:{legend:{display:false}}, scales:{x:{grid:{display:true}}}}});
  }

  // Pie chart
  if(typeof Chart!=='undefined'){
    var pieLabels=[], pieData=[], otherTotal=0;
    for(var i=0; i<allStores.length; i++){
      if(i<8){ pieLabels.push(allStores[i][0]); pieData.push(allStores[i][1].total); }
      else{ otherTotal += allStores[i][1].total; }
    }
    if(otherTotal>0){ pieLabels.push('其他'); pieData.push(otherTotal); }
    new Chart(document.getElementById('pieChart'),{type:'doughnut',
      data:{labels:pieLabels, datasets:[{data:pieData, backgroundColor:['#4472C4','#ED7D31','#70AD47','#FFC000','#5B9BD5','#A5A5A5','#FF6B6B','#4ECDC4','#96CEB4']}]},
      options:{responsive:true, maintainAspectRatio:false, plugins:{legend:{position:'right',labels:{font:{size:10},padding:4}}}}});
  }

  // Orders table
  var h = '<table><thead><tr><th>店铺</th>';
  for(var i=0; i<dates.length; i++){ h += '<th>'+dates[i]+'</th>'; }
  h += '<th>合计</th></tr></thead><tbody>';
  for(var i=0; i<allStores.length; i++){
    var s=allStores[i];
    h += '<tr><td>'+s[0]+'</td>';
    for(var j=0; j<dates.length; j++){ h += '<td class="num">'+(s[1].daily[dates[j]]||0)+'</td>'; }
    h += '<td class="num" style="font-weight:bold">'+s[1].total+'</td></tr>';
  }
  h += '<tr class="total-row"><td>合计 ('+allStores.length+'店铺)</td>';
  for(var j=0; j<dates.length; j++){
    var dt=0;
    for(var i=0; i<allStores.length; i++){ dt += (allStores[i][1].daily[dates[j]]||0); }
    h += '<td class="num">'+dt+'</td>';
  }
  h += '<td class="num">'+totalOrders+'</td></tr></tbody></table>';
  document.getElementById('ordersTbl').innerHTML = h;

  // FBA stock table
  var ws = LX.warehouse_stock || {};
  var wentries = Object.entries(ws).sort(function(a,b){ return b[1].available - a[1].available; });
  var sh = '<table><thead><tr><th>仓库</th><th>可售</th><th>待发货</th><th>在途</th><th>不可售</th><th>SKU数</th></tr></thead><tbody>';
  var totAvail=0, totPend=0, totInb=0, totUns=0, totSku=0;
  for(var i=0; i<wentries.length; i++){
    var w=wentries[i];
    sh += '<tr><td>'+w[0]+'</td><td class="num">'+w[1].available.toLocaleString()+'</td><td class="num">'+w[1].pending.toLocaleString()+'</td><td class="num">'+w[1].inbound.toLocaleString()+'</td><td class="num">'+w[1].unsellable.toLocaleString()+'</td><td class="num">'+w[1].skus+'</td></tr>';
    totAvail+=w[1].available; totPend+=w[1].pending; totInb+=w[1].inbound; totUns+=w[1].unsellable; totSku+=w[1].skus;
  }
  sh += '<tr class="total-row"><td>合计 ('+wentries.length+'仓库)</td><td class="num">'+totAvail.toLocaleString()+'</td><td class="num">'+totPend.toLocaleString()+'</td><td class="num">'+totInb.toLocaleString()+'</td><td class="num">'+totUns.toLocaleString()+'</td><td class="num">'+totSku+'</td></tr></tbody></table>';
  document.getElementById('stockTbl').innerHTML = wentries.length ? sh : '<p style="color:#999;text-align:center">暂无库存数据</p>';
})();
</script>
</body>
</html>"""


def main():
    print("Fetching silver data...")
    resp = requests.get(SILVER_DATA_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    with open("silver_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    data_time = data.get("pull_time", now)

    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("DATA_TIME", data_time).replace("NOW", now)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    ws = data.get("warehouse_stock", {})
    print(f"[{now}] Done — {data['total_orders']} orders, {data['shops_count']} stores, {len(ws)} warehouses")


if __name__ == "__main__":
    main()
