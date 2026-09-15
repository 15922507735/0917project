"""
一次性脚本：把全局 email-ext 的 defaultBody 内联进 qiyuan_uitest 的两个触发器 <body>，
不再依赖 $PROJECT_DEFAULT_CONTENT / $DEFAULT_CONTENT token 链，避免 Jelly 解析异常导致正文为空。

运行：
    python demo_project/scripts/inline_email_body.py

输入：
    D:/jenkins/data/hudson.plugins.emailext.ExtendedEmailPublisher.xml
    D:/jenkins/data/jobs/qiyuan_uitest/config.xml

输出：
    修改后的 D:/jenkins/data/jobs/qiyuan_uitest/config.xml
"""

from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import xml.sax.saxutils as saxutils
import re

EXT_PUB = Path(r"D:/jenkins/data/hudson.plugins.emailext.ExtendedEmailPublisher.xml")
JOB_CFG = Path(r"D:/jenkins/data/jobs/qiyuan_uitest/config.xml")


def read_default_body() -> str:
    """从全局 ExtendedEmailPublisher.xml 解析出 defaultBody 的明文。"""
    text = EXT_PUB.read_text(encoding="utf-8")

    # 取 <defaultBody>...</defaultBody> 之间内容
    m = re.search(r"<defaultBody>(.*?)</defaultBody>", text, flags=re.DOTALL)
    if not m:
        raise RuntimeError("没找到 <defaultBody>，先确认全局配置存在")

    inner = m.group(1)

    # 反转 XML 实体，得到真正可用的 HTML 字符串
    inner = (inner
             .replace("&lt;", "<")
             .replace("&gt;", ">")
             .replace("&quot;", '"')
             .replace("&apos;", "'")
             .replace("&amp;", "&"))
    return inner


def clean_template(html: str) -> str:
    """修正模板里会导致 Jelly 解析异常 / 留空的小问题。"""
    # 1) ${PROJECT_NAME } 末尾多余空格 -> ${PROJECT_NAME}
    html = html.replace("${PROJECT_NAME }", "${PROJECT_NAME}")
    # 2) ${ENV, var="JOB_NAME"} 里的双引号在 Jelly 里没问题，保留
    return html


def escape_for_xml_body(html: str) -> str:
    """作为 <body>...< /body> 元素内容写入 config.xml 时的转义。

    只转义 & 和 < 即可（> 可选转义，但这里保险起见一起转）。
    注意：Jelly 模板语法 ${...} 在写入 XML 时不需要额外处理，因为它就是普通字符。
    """
    return (html
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def patch_job_config(body_html: str) -> None:
    cfg_text = JOB_CFG.read_text(encoding="utf-8")
    body_xml = escape_for_xml_body(body_html)

    # 替换两个触发器里的 <body>$PROJECT_DEFAULT_CONTENT</body>
    # 因为有 2 处，用 replace_all 即可；这里手写 replace 全局一次
    new_text = cfg_text.replace(
        "<body>$PROJECT_DEFAULT_CONTENT</body>",
        f"<body>{body_xml}</body>",
    )

    if new_text == cfg_text:
        raise RuntimeError("没有替换发生，请检查 config.xml 里是否仍是 $PROJECT_DEFAULT_CONTENT")

    JOB_CFG.write_text(new_text, encoding="utf-8")
    print(f"[OK] 替换完成。新 config.xml 字节数: {len(new_text)}")


def validate_xml() -> None:
    """用 ET 解析确认 XML 没破。"""
    ET.parse(JOB_CFG)
    print("[OK] XML 格式校验通过")


def main() -> int:
    html = read_default_body()
    html = clean_template(html)
    print(f"[INFO] defaultBody 明文长度: {len(html)} chars")
    patch_job_config(html)
    validate_xml()
    print("[DONE] qiyuan_uitest/config.xml 已更新；下次 Reload Configuration from Disk 后生效")
    return 0


if __name__ == "__main__":
    sys.exit(main())
