from __future__ import annotations

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.by import By

from .login_page import APP_PACKAGE


# 发帖入口按钮
POST_BUTTON = (
    AppiumBy.ID,
    f"{APP_PACKAGE}:id/iv_menu",
)
# 发文章按钮
POST_ARTICLE_BUTTON = (
    AppiumBy.XPATH,
    f"//android.widget.TextView[@resource-id='{APP_PACKAGE}:id/tv_content' and @text='发文章']",
)
# 上传封面按钮（H5 页面内：class=uploadCoverClass 的占位 div）
# Chrome DevTools 验证过该 div 是"+号"图标的可点击区域
UPLOAD_COVER_BUTTON = (
    By.CSS_SELECTOR,
    ".uploadCoverClass",
)
# 选择封面图片按钮
SELECT_COVER_BUTTON = (
    By.XPATH,
    f"//*[@id='toast-wrapper']/div[2]/div[1]/button[1]",
)
# 标题输入框（H5 input 元素）
TITLE_INPUT = (
    By.XPATH,
    "//*[@id='app']/div/div[3]/div[1]/div/div[2]/input",
)
# 内容输入框（H5 富文本编辑器，contenteditable="true"）
# 联合定位：用 class + id 两个条件组合定位同一个元素（ss-editor needsclick 且 id="-1"）
CONTENT_INPUT = (
    By.XPATH,
    "//div[@class='ss-editor needsclick' and @id='-1']",
)
# 话题选择
TOPIC_LIST = (
    By.XPATH,
    f"//*[@id='app']/div/div[4]/div/div[2]/div/div[1]/div[1]/div/div[2]",
)
# 发布按钮（用文字内容定位，避免 span 索引歧义）
PUBLISH_BUTTON = (
    By.XPATH,
    "//span[normalize-space(text())='发布']",
)
# 选择图片按钮
SELECT_IMAGE_BUTTON = (
    AppiumBy.XPATH,
    f"//android.widget.Button[@text='选择图片']",
)
# 授权允许按钮（系统权限弹窗，Android 9 用 packageinstaller）
PERMISSION_ALLOW_BUTTON = (
    AppiumBy.ID,
    "com.android.packageinstaller:id/permission_allow_button",
)
# 勾选图片按钮（点击图片右上角的小圆圈区域）
# DOM 层级：ImageView(fv_picture) → LinearLayout(ll_check) → TextView(check)
# 整个 LinearLayout 是可点击区
# 注意：勾选状态不在 LinearLayout 的 @checked 属性，而在子 TextView 的 @text：
#   text=""   → 未选
#   text="1"   → 已选 1 张（数字是已选张数）
GOUXUAN_IMAGE_BUTTON = (
    AppiumBy.XPATH,
    "//android.widget.LinearLayout[@resource-id='com.changan.oushangCos1:id/ll_check']",
)
# 勾选图片的子元素（未勾选状态 TextView）
# text="" 时表示该图片未选
GOUXUAN_IMAGE_CHECK_TEXT = (
    AppiumBy.XPATH,
    "//android.widget.TextView[@resource-id='com.changan.oushangCos1:id/check' and @text='']",
)
# 联合定位：找一个 ll_check，它**包含**未勾选的 check TextView（用 .// 轴）
# 排除已选的图片，确保每次点到的都是未选中的
# 语法说明：两个 [] 都是同一个 LinearLayout 的谓词，第二个用 .// 轴引用后代节点作为筛选条件
# 等价 SQL: SELECT ll_check WHERE EXISTS(descendant check WHERE text='')
GOUXUAN_IMAGE_UNCHECKED = (
    AppiumBy.XPATH,
    "(//android.widget.LinearLayout[@resource-id='com.changan.oushangCos1:id/ll_check']"
    "[.//android.widget.TextView[@resource-id='com.changan.oushangCos1:id/check' and @text='']])[3]",
)
# 图片选中后元素
GOUXUAN_IMAGE_CHECKED = (
    AppiumBy.XPATH,
    "//android.widget.TextView[@resource-id='com.changan.oushangCos1:id/check' and @text='1']",
)
# 已完成按钮
CONFIRM_GOUXUAN_IMAGE_BUTTON = (
    AppiumBy.ID,
    f"com.changan.oushangCos1:id/picture_tv_ok",
)
# 封面图片确认按钮
CONFIRM_COVER_IMAGE_BUTTON = (
    AppiumBy.ID,
    f"com.changan.oushangCos1:id/tvcomit",
)
# 已设置封面元素
CONFIRM_COVER_IMAGE_ELEMENT = (
    By.CLASS_NAME,
    "coverImg",
)
# 点击内容图片上传按钮
CLICK_CONTENT_IMAGE_BUTTON = (
    By.XPATH,
    f"//*[@id='bottom-other-item']/div/div[1]",
)
# 话题选择按钮
TOPIC_BUTTON = (
    By.XPATH,
    f"//*[@id='bottom-other-item']/div/div[2]",
)
# 内容图片选择按钮-弹窗
SELECT_CONTENT_IMAGE_BUTTON = (
    By.XPATH,
    f"//*[@id='app']/div/div[7]/div[1]/button",
)
# 内容图片确认按钮
CONFIRM_CONTENT_IMAGE_BUTTON = (
    AppiumBy.ID,
    f"com.changan.oushangCos1:id/pt_tvright",
)
# 确定选择按钮-弹窗
CONFIRM_QUEDING_IMAGE_BUTTON = (
    AppiumBy.ID,
    f"com.changan.oushangCos1:id/pt_tvright",
)
# 发布成功提示-弹窗文本（H5 内的元素，用通用文本定位）
PUBLISH_SUCCESS_TEXT = (
    By.XPATH,
    "//*[contains(text(),'发布成功')]",
)
