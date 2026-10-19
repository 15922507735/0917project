# MCP Servers 目录

本目录存放**独立运行的 MCP Server 脚本**，通过 stdio 与 IDE（Claude / Trae 等）对接，不依赖项目代码。

## 文件清单

| 脚本 | 服务名 | 工具 |
|------|--------|------|
| `mcp_mysql.py` | MySQL MCP Server | `connect / disconnect / list_databases / list_tables / describe_table / show_create_table / execute_query / execute_update` |
| `mcp_file_ops.py` | File Operations MCP Server | `read_file / write_file / list_directory / search_files` |
| `mcp_weather.py` | WeatherServer（示例） | `get_weather(city) / get_current_time()` |

## 接入 IDE（.mcp.json）

复制项目根 `.mcp.json` 模板到 IDE 配置目录即可。已注册的服务：

```json
{
  "mcpServers": {
    "mysql":       { "command": "python", "args": ["<项目绝对路径>/mcp_servers/mcp_mysql.py"] },
    "file-ops":    { "command": "python", "args": ["<项目绝对路径>/mcp_servers/mcp_file_ops.py"] },
    "weather":     { "command": "python", "args": ["<项目绝对路径>/mcp_servers/mcp_weather.py"] }
  }
}
```

`<项目绝对路径>` 替换为 `d:\git_project\demo_qiyuan_bac\mcp_servers\`。

## MySQL MCP 配置（环境变量）

`mcp_mysql.py` 默认从环境变量连接 MySQL，**敏感字段不写死到源码**：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `MYSQL_HOST` | `qiyuan-test.mysql.polardb.rds.aliyuncs.com` | 主机地址 |
| `MYSQL_PORT` | `3306` | 端口 |
| `MYSQL_USER` | `qiyuan_test` | 用户名 |
| `MYSQL_PASSWORD` | （空） | **必填**，否则 `connect` 报错 |
| `MYSQL_DATABASE` | `qiyuan` | 默认数据库 |
| `MYSQL_CHARSET` | `utf8mb4` | 字符集 |

> ⚠️ **注意**：`MYSQL_PASSWORD` 必须通过 IDE 的 `.mcp.json` 的 `env` 字段注入，**不要提交到仓库**。

## 依赖

```bash
pip install "mcp>=2.0" pymysql
```

## 直接运行测试

```bash
cd d:\git_project\demo_qiyuan_bac
python mcp_servers\mcp_mysql.py        # 启动 MySQL MCP
python mcp_servers\mcp_file_ops.py     # 启动文件操作 MCP
python mcp_servers\mcp_weather.py      # 启动天气示例 MCP
```

启动后客户端（IDE）会通过 stdio 与之通信。