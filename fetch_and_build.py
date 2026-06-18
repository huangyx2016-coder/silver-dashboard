"""Fetch silver data from main dashboard, build standalone page."""
import json
from datetime import datetime
import requests

SILVER_DATA_URL = "https://huangyx2016-coder.github.io/lingxing-dashboard/silver_data.json"


def main():
    print("Fetching silver data...")
    resp = requests.get(SILVER_DATA_URL, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # Save local copy
    with open("silver_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    sj = json.dumps(data, ensure_ascii=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    data_time = data.get("pull_time", now)

    html = build_html(sj, now, data_time)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[{now}] Done — {data['total_orders']} orders, {data['shops_count']} stores")


def build_html(sj, now, data_time):
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>银饰订单 - 店铺明细</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'Microsoft YaHei', sans-serif; background:#f0f2f5; color:#333; padding:16px; }
.header { text-align:center; margin-bottom:16px; }
.header h1 { font-size:22px; color:#1a1a2e; }
.header p { color:#666; margin-top:2px; font-size:12px; }
.card { background:#fff; border-radius:10px; padding:14px; box-shadow:0 2px 6px rgba(0,0,0,0.06); margin-bottom:14px; max-width:1100px; margin-left:auto; margin-right:auto; }
.card h2 { font-size:14px; margin-bottom:8px; border-bottom:2px solid #70AD47; padding-bottom:5px; }
.table-wrap { max-height:600px; overflow-y:auto; }
table { width:100%; border-collapse:collapse; font-size:11px; }
th { background:#70AD47; color:#fff; padding:5px 3px; position:sticky; top:0; z-index:1; text-align:center; white-space:nowrap; }
td { padding:3px; text-align:center; border-bottom:1px solid #eee; }
tr:hover td { background:#f5f7fa; }
td:first-child { text-align:left; font-weight:500; }
.num { text-align:right; }
.total-row td { font-weight:bold; background:#FFF2CC; border-top:2px solid #70AD47; }
.chart-wrap { position:relative; height:400px; margin-bottom:14px; max-width:1100px; margin-left:auto; margin-right:auto; }
.summary-bar { display:flex; gap:14px; margin-bottom:14px; max-width:1100px; margin-left:auto; margin-right:auto; }
.summary-item { flex:1; background:#fff; border-radius:10px; padding:12px 14px; box-shadow:0 2px 6px rgba(0,0,0,0.06); text-align:center; }
.summary-item .value { font-size:22px; font-weight:bold; color:#70AD47; }
.summary-item .label { font-size:10px; color:#888; margin-top:1px; }
.footer { text-align:right; color:#aaa; font-size:10px; margin-top:8px; }
</style>
</head>
<body>
<div class="header"><h1>银饰订单 - 店铺明细</h1><p id="dateRange"></p></div>
<div class="summary-bar"><div class="summary-item"><div class="value" id="totalOrders">-</div><div class="label">银饰总订单</div></div><div class="summary-item"><div class="value" id="shopCount">-</div><div class="label">店铺数</div></div></div>
<div class="card"><h2>全部银饰店铺</h2><div class="table-wrap" id="tbl">加载中...</div></div>
<div class="footer">数据更新: """ + data_time + """ | 页面生成: """ + now + """</div>

<script>
var LX = """ + sj + """;

(function(){
  var dates = LX.dates;
  var allStores = Object.entries(LX.orders).sort(function(a,b){ return b[1].total - a[1].total; });

  document.getElementById('dateRange').textContent = dates[0] + ' — ' + dates[dates.length-1] + ' | ' + LX.total_orders.toLocaleString() + ' 单 | ' + LX.shops_count + ' 店铺';
  document.getElementById('totalOrders').textContent = LX.total_orders.toLocaleString();
  document.getElementById('shopCount').textContent = LX.shops_count;

  var h = '<table><thead><tr><th>店铺</th>';
  for (var i = 0; i < dates.length; i++) { h += '<th>' + dates[i] + '</th>'; }
  h += '<th>合计</th></tr></thead><tbody>';
  for (var i = 0; i < allStores.length; i++) {
    var s = allStores[i];
    h += '<tr><td>' + s[0] + '</td>';
    for (var j = 0; j < dates.length; j++) { h += '<td class="num">' + (s[1].daily[dates[j]] || 0) + '</td>'; }
    h += '<td class="num" style="font-weight:bold">' + s[1].total + '</td></tr>';
  }
  h += '<tr class="total-row"><td>合计 (' + allStores.length + '店铺)</td>';
  for (var j = 0; j < dates.length; j++) {
    var dt = 0;
    for (var i = 0; i < allStores.length; i++) { dt += (allStores[i][1].daily[dates[j]] || 0); }
    h += '<td class="num">' + dt + '</td>';
  }
  h += '<td class="num">' + LX.total_orders + '</td></tr></tbody></table>';
  document.getElementById('tbl').innerHTML = h;
})();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
