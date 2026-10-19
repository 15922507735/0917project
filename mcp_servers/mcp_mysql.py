"""
MySQL MCP Server（mcp 2.x）

基于 pymysql 提供对 MySQL 数据库的常见操作。
工具：
- connect / disconnect
- list_databases / list_tables / describe_table / show_create_table
- execute_query（SELECT，返回结果集）
- execute_update（INSERT/UPDATE/DELETE，返回受影响行数）

依赖：
    pip install "mcp>=2.0" pymysql

运行：
    python demo_test/mcp_mysql.py

接入 .mcp.json（与同级 mcp_sever.py / mcp_demo.py 一致，stdio 传输）：
    {
      "mcpServers": {
        "weather-time": {
          "type": "stdio",
          "command": "python",
          "args": ["C:/Users/Administrator/Documents/trae_projects/demo/demo_test/mcp_sever.py"],
          "env": {}
        },
        "file-ops": {
          "type": "stdio",
          "command": "python",
          "args": ["C:/Users/Administrator/Documents/trae_projects/demo/demo_test/mcp_demo.py"],
          "env": {}
        },
        "mysql": {
          "type": "stdio",
          "command": "python",
          "args": ["C:/Users/Administrator/Documents/trae_projects/demo/demo_test/mcp_mysql.py"],
          "env": {}
        }
      }
    }
"""

from mcp.server.mcpserver import MCPServer
import pymysql
from pymysql.cursors import DictCursor
import os

# .mcp.json 注册配置（与同级 mcp_sever.py / mcp_demo.py 一致，stdio 传输）。
# 客户端可直接读取此字段拿到 stdio 启动参数；脚本路径为绝对路径，
# 复制到项目根的 .mcp.json 中即可被 Claude / IDE 加载。
_SCRIPT_PATH = os.path.abspath(__file__)
MCP_SERVER_CONFIG = {
    "type": "stdio",
    "command": "python",
    "args": [_SCRIPT_PATH],
    "env": {},
}

# 创建 MCP Server
mcp = MCPServer("MySQL MCP Server")

# 默认连接参数（敏感字段从环境变量读取，避免密码写入源码）
# 支持的环境变量（缺一即视为未配置）：
#   MYSQL_HOST       主机地址，默认 qiyuan-test.mysql.polardb.rds.aliyuncs.com
#   MYSQL_PORT       端口，默认 3306
#   MYSQL_USER       用户名，默认 qiyuan_test
#   MYSQL_PASSWORD   密码（必填，未设置时报错）
#   MYSQL_DATABASE   默认数据库，默认 qiyuan
#   MYSQL_CHARSET    字符集，默认 utf8mb4
DEFAULT_MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "qiyuan-test.mysql.polardb.rds.aliyuncs.com"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "qiyuan_test"),
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": os.getenv("MYSQL_DATABASE", "qiyuan"),
    "charset": os.getenv("MYSQL_CHARSET", "utf8mb4"),
}

# 全局连接对象：单连接复用，避免每次工具调用都重新握手
_connection: pymysql.connections.Connection | None = None


def _auto_connect() -> str | None:
    """若尚未连接，使用默认配置自动建立连接；返回 None 表示成功，否则返回错误信息。"""
    global _connection
    if _connection is not None and _connection.open:
        return None
    if not DEFAULT_MYSQL_CONFIG.get("password"):
        return "MYSQL_PASSWORD 环境变量未设置，无法自动连接。可通过 env 注入或在 connect 工具中显式传入 password。"
    try:
        _connection = pymysql.connect(cursorclass=DictCursor, autocommit=False, connect_timeout=10, **DEFAULT_MYSQL_CONFIG)
        return None
    except Exception as e:
        _connection = None
        return f"自动连接失败：{type(e).__name__}: {e}"


def _get_conn() -> pymysql.connections.Connection:
    """获取当前连接；若未连接则先用默认配置重连。"""
    if _connection is None or not _connection.open:
        err = _auto_connect()
        if err:
            raise RuntimeError(err)
    return _connection


@mcp.tool()
def connect(
    host: str = "qiyuan-test.mysql.polardb.rds.aliyuncs.com",
    port: int = 3306,
    user: str = "qiyuan_test",
    password: str | None = None,
    database: str | None = "qiyuan",
    charset: str = "utf8mb4",
) -> str:
    """连接到 MySQL 数据库（若已连接会自动断开旧的）

    Args:
        host: 主机地址，默认 127.0.0.1
        port: 端口，默认 3306
        user: 用户名，默认 root
        password: 密码（默认从环境变量 MYSQL_PASSWORD 读取；显式传空字符串表示用空密码连接）
        database: 默认数据库，可为空（连接后再选库）
        charset: 字符集，默认 utf8mb4

    Returns:
        连接信息摘要
    """
    # 密码默认从环境变量读取，避免硬编码到源码中
    if password is None:
        password = os.getenv("MYSQL_PASSWORD", "")
    global _connection
    try:
        # 已存在连接则先关闭
        if _connection is not None and _connection.open:
            try:
                _connection.close()
            except Exception:
                pass

        _connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset=charset,
            cursorclass=DictCursor,
            autocommit=False,
            connect_timeout=10,
        )
        target = database if database else "(未选库)"
        return f"已连接到 MySQL：{user}@{host}:{port}/{target}（charset={charset}）"
    except Exception as e:
        _connection = None
        return f"连接失败：{type(e).__name__}: {e}"


@mcp.tool()
def disconnect() -> str:
    """断开当前 MySQL 连接"""
    global _connection
    if _connection is None or not _connection.open:
        return "当前没有活跃的 MySQL 连接"
    try:
        _connection.close()
        _connection = None
        return "已断开 MySQL 连接"
    except Exception as e:
        return f"断开失败：{type(e).__name__}: {e}"


@mcp.tool()
def list_databases() -> str:
    """列出 MySQL 实例上的所有数据库

    Returns:
        数据库列表（每行一个）
    """
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute("SHOW DATABASES")
            rows = cur.fetchall()
        names = [list(r.values())[0] for r in rows]
        return f"共 {len(names)} 个数据库：\n\n" + "\n".join(names)
    except Exception as e:
        return f"列出数据库失败：{type(e).__name__}: {e}"


@mcp.tool()
def list_tables(database: str | None = None) -> str:
    """列出指定数据库中的所有表（不传则使用当前连接的默认库）

    Args:
        database: 数据库名，可空

    Returns:
        表名列表
    """
    try:
        conn = _get_conn()
        sql = "SHOW TABLES"
        args: tuple = ()
        if database:
            # 限定到指定库
            sql = f"SHOW TABLES FROM `{database}`"
        with conn.cursor() as cur:
            cur.execute(sql, args)
            rows = cur.fetchall()
        names = [list(r.values())[0] for r in rows]
        target = database if database else conn.db.decode() if conn.db else "(当前库)"
        return f"数据库 `{target}` 中共 {len(names)} 张表：\n\n" + "\n".join(names)
    except Exception as e:
        return f"列出表失败：{type(e).__name__}: {e}"


@mcp.tool()
def describe_table(table_name: str, database: str | None = None) -> str:
    """查看表的字段结构（等价于 DESCRIBE table）

    Args:
        table_name: 表名
        database: 数据库名，可空（使用当前连接默认库）

    Returns:
        表结构描述
    """
    try:
        # 校验表名，避免简单的 SQL 注入
        if not table_name or not table_name.replace("_", "").isalnum():
            return "表名仅允许字母、数字、下划线"
        conn = _get_conn()
        db = database or (conn.db.decode() if conn.db else None)
        full_name = f"`{db}`.`{table_name}`" if db else f"`{table_name}`"
        with conn.cursor() as cur:
            cur.execute(f"DESCRIBE {full_name}")
            rows = cur.fetchall()
        if not rows:
            return f"表 {full_name} 不存在或无字段"
        # 整理为可读表格
        header = f"{'Field':<24} {'Type':<20} {'Null':<6} {'Key':<6} {'Default':<12} Extra"
        sep = "-" * len(header)
        lines = [header, sep]
        for r in rows:
            lines.append(
                f"{str(r.get('Field', '')):<24} "
                f"{str(r.get('Type', '')):<20} "
                f"{str(r.get('Null', '')):<6} "
                f"{str(r.get('Key', '')):<6} "
                f"{str(r.get('Default', '')) if r.get('Default') is not None else '':<12} "
                f"{str(r.get('Extra', ''))}"
            )
        return f"{full_name} 表结构（共 {len(rows)} 列）：\n\n" + "\n".join(lines)
    except Exception as e:
        return f"查看表结构失败：{type(e).__name__}: {e}"


@mcp.tool()
def show_create_table(table_name: str, database: str | None = None) -> str:
    """查看建表语句（SHOW CREATE TABLE）

    Args:
        table_name: 表名
        database: 数据库名，可空

    Returns:
        建表 DDL
    """
    try:
        if not table_name or not table_name.replace("_", "").isalnum():
            return "表名仅允许字母、数字、下划线"
        conn = _get_conn()
        db = database or (conn.db.decode() if conn.db else None)
        full_name = f"`{db}`.`{table_name}`" if db else f"`{table_name}`"
        with conn.cursor() as cur:
            cur.execute(f"SHOW CREATE TABLE {full_name}")
            row = cur.fetchone()
        if not row:
            return f"表 {full_name} 不存在"
        # SHOW CREATE TABLE 返回的字段名可能是 'Create Table' 或 'Create View'
        ddl = next((v for v in row.values() if isinstance(v, str)), str(row))
        return f"{full_name} 建表语句：\n\n{ddl}"
    except Exception as e:
        return f"查看建表语句失败：{type(e).__name__}: {e}"


@mcp.tool()
def execute_query(sql: str, params: list | None = None, max_rows: int = 1000) -> str:
    """执行查询 SQL（SELECT / SHOW / EXPLAIN 等），返回结果集

    Args:
        sql: 查询 SQL 语句
        params: 绑定参数列表（按顺序用 %s 占位），可空
        max_rows: 最多返回行数，防止一次拉太多，默认 1000

    Returns:
        格式化的结果集（Markdown 风格表格）
    """
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params) if params else None)
            rows = cur.fetchall()
        if not rows:
            return "查询成功，无返回行"
        rows = rows[:max_rows]
        # 第一行 keys 视为列名
        cols = list(rows[0].keys())
        header = "| " + " | ".join(cols) + " |"
        sep = "| " + " | ".join(["---"] * len(cols)) + " |"
        body_lines = []
        for r in rows:
            cells = ["" if r.get(c) is None else str(r.get(c)) for c in cols]
            # 简单转义防止破坏表格
            cells = [c.replace("|", "\\|").replace("\n", " ") for c in cells]
            body_lines.append("| " + " | ".join(cells) + " |")
        truncated = f"\n\n> 已截断，仅返回前 {max_rows} 行（共 {len(rows)} 行）" if len(rows) == max_rows else ""
        return f"查询返回 {len(rows)} 行{('，已截断' if len(rows) == max_rows else '')}：\n\n" + "\n".join([header, sep, *body_lines]) + truncated
    except Exception as e:
        return f"查询失败：{type(e).__name__}: {e}"


@mcp.tool()
def execute_update(sql: str, params: list | None = None, commit: bool = True) -> str:
    """执行写操作 SQL（INSERT / UPDATE / DELETE / CREATE / DROP 等）

    Args:
        sql: 写操作 SQL
        params: 绑定参数列表（按顺序用 %s 占位），可空
        commit: 是否自动提交，默认 True

    Returns:
        受影响行数 / lastrowid 摘要
    """
    try:
        conn = _get_conn()
        with conn.cursor() as cur:
            affected = cur.execute(sql, tuple(params) if params else None)
            last_id = cur.lastrowid
        if commit:
            conn.commit()
            return f"执行成功：受影响 {affected} 行，lastrowid={last_id}（已提交）"
        else:
            conn.rollback()
            return f"执行成功：受影响 {affected} 行，lastrowid={last_id}（未提交，已 rollback）"
    except Exception as e:
        # 出错时回滚，保持连接干净
        try:
            conn.rollback()
        except Exception:
            pass
        return f"执行失败：{type(e).__name__}: {e}"


@mcp.resource("config://app")
def get_config() -> str:
    """获取当前 MCP Server 配置信息"""
    status = "已连接" if (_connection is not None and _connection.open) else "未连接"
    target = _connection.db.decode() if (_connection and _connection.db) else "(未选库)"
    return f"""
    应用名称：MySQL MCP Server
    版本：1.0.0
    连接状态：{status}
    当前库：{target}
    功能：
    - connect / disconnect
    - list_databases / list_tables / describe_table / show_create_table
    - execute_query（SELECT）
    - execute_update（INSERT / UPDATE / DELETE）
    """


if __name__ == "__main__":
    mcp.run()
