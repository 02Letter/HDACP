# HDACP 真实独立访客统计

目标域名：`https://www.xcfqms.com`，服务器：`140.143.87.118`。
现有域名已运行 Nginx 和 HTTPS；实验室网站仍发布在 GitHub Pages。

## 统计方式

- 浏览器在本地保存一个随机 UUID，POST 到 `/hdacp-visits/api/visits`。
- 服务将 IP 与浏览器 UUID 合并后计算 HMAC，数据库只保存摘要及首次访问时间。
- 相同 IP 和相同浏览器 UUID 只计一次；不同浏览器、清除本地数据或更换 IP 会被视为新访客。
- 数据保存在 SQLite 中，服务重启后保留；数据库与 `counter.secret` 必须一起备份，不能在重启或更新代码时重建密钥。
- 本地存储受限制的浏览器只读取总数，不生成每次刷新的临时标识以反复计数。
- 这是独立访客数量，不是页面浏览次数，也不能严格识别现实中的自然人。

## 接口

- GET `/hdacp-visits/api/visits`：读取 `{ "count": 整数 }`。
- POST 同一路径：JSON 请求体 `{ "browserId": "浏览器 UUID v4" }`，返回去重后的总数。
- OPTIONS：允许 `https://02letter.github.io` 的跨域请求。

## 已部署配置（2026-10-11）

通过用户已登录的宝塔终端部署。系统为 OpenCloudOS 9，Python 为 `/usr/bin/python3`（3.11.6），无需第三方库。

- 程序：`/opt/hdacp-visits/visits.py`。
- 服务：`/etc/systemd/system/hdacp-visits.service`，已启用；使用 `DynamicUser=yes` 自动分配非 root 服务身份。
- 持久数据：`/var/lib/hdacp-visits/`（systemd 的 StateDirectory），文件为 `visitors.sqlite3` 和 `counter.secret`，目录模式 0700。
- 监听：仅 `127.0.0.1:8787`，无需在防火墙开放新端口。
- Nginx：`/www/server/panel/vhost/nginx/fqms.example.com.conf` 中添加准确匹配的接口 location，代理保留完整路径，以 `$remote_addr` 覆盖 `X-Real-IP`。接口关闭 access_log，避免额外保存访客原始 IP。其他民宿站点路由保留。
- 修改前备份：`/opt/hdacp-visits/nginx-site-20261011-162219.conf.bak`。修改前后均通过 `/www/server/nginx/sbin/nginx -t`，随后重载。
- GitHub 发布环境设置 `VITE_VISITOR_API_URL=https://www.xcfqms.com/hdacp-visits/api/visits`；每日流程不再调用随机增长脚本。

外网 HTTPS 返回 200，跨域预检允许 GitHub Pages，其他 Origin 返回 403；相同标识重复访问人数保持 1。重启服务后人数仍为 1，且服务为 enabled/active。测试访问计入真实数据库，未导入历史随机数。

## 维护与备份

在宝塔终端查看 `systemctl status hdacp-visits --no-pager`；更新程序后运行 `systemctl restart hdacp-visits`。Nginx 配置修改后必须先验证再重载。

备份时短暂停止 `hdacp-visits`，将整个数据目录复制到非公开备份位置，再启动服务。SQLite 数据库和 `counter.secret` 必须一起保存；不能单独重建密钥。服务停止时会合并 WAL；若备份时仍有 `-wal` / `-shm` 文件，也一并保留。systemd 的 DynamicUser 会管理数据目录权限，恢复时沿用 StateDirectory，不改为全员可写。

后台服务和前端独立部署：以后推送 GitHub 只更新前端与论文，不会自动覆盖服务器数据库或程序。若迁移域名或改用代理/CDN，先重新核实 HTTPS、CORS 和真实 IP 规则，再改构建环境变量。接口不可用时前端显示“—”，不回退为随机数。

## 本地验证

```text
python -m unittest discover -s scripts -p "test_visits_server.py"
node --test scripts/test_visit_counter.mjs
```
