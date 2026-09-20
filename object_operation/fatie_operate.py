from __future__ import annotations

from time import sleep
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy

from page_element.login_page import EXPECT_WAIT_TIMEOUT
from page_element.fatie_page import (
    POST_BUTTON,
    POST_ARTICLE_BUTTON,
    UPLOAD_COVER_BUTTON,
    SELECT_COVER_BUTTON,
    TITLE_INPUT,
    CONTENT_INPUT,
    TOPIC_BUTTON,
    TOPIC_LIST,
    SELECT_IMAGE_BUTTON,
    PERMISSION_ALLOW_BUTTON,
    GOUXUAN_IMAGE_BUTTON,
    GOUXUAN_IMAGE_CHECK_TEXT,
    GOUXUAN_IMAGE_UNCHECKED,
    CONFIRM_GOUXUAN_IMAGE_BUTTON,
    CONFIRM_COVER_IMAGE_BUTTON,
    CONFIRM_CONTENT_IMAGE_BUTTON,
    GOUXUAN_IMAGE_CHECKED,
    CONFIRM_COVER_IMAGE_ELEMENT,
    CLICK_CONTENT_IMAGE_BUTTON,
    SELECT_CONTENT_IMAGE_BUTTON,
    CONFIRM_QUEDING_IMAGE_BUTTON,
    PUBLISH_BUTTON,
    )

class FatieOperate:
    def __init__(
        self,
        driver: WebDriver,
        logger: Any,
        webview_operate: Any = None,
        expect_wait_timeout: int = EXPECT_WAIT_TIMEOUT,
    ):
        self.driver = driver
        self.logger = logger
        self.webview_operate = webview_operate
        self.expect_wait_timeout = expect_wait_timeout

        self.wait = WebDriverWait(self.driver, self.expect_wait_timeout)

    def click_post_button(self):
        self.driver.find_element(*POST_BUTTON).click()
        self.logger.info("点击发帖入口按钮")
        # 等待发文章按钮出现
        self.wait.until(
            EC.presence_of_element_located(POST_ARTICLE_BUTTON)
        )
    def click_post_article_button(self):
        self.driver.find_element(*POST_ARTICLE_BUTTON).click()
        self.logger.info("点击发文章按钮")
        
    def switch_to_post_article_webview(self):
        # 切换到发文章编辑页面的webview
        self.webview_operate.switch_to_webview()
        self.logger.info("切换到发文章编辑页面的webview")

        # 打印 url + title
        try:
            self.logger.info(f"当前页面url: {self.driver.current_url}")
            self.logger.info(f"当前页面title: {self.driver.title}")
        except Exception as e:
            self.logger.error(f"获取当前页面url + title失败: {e}")

        # 断言发文章页面加载完成（H5 url 含 circle/publish）
        assert "circle/publish" in self.driver.current_url, (
            f"期望 url 包含 circle/publish，实际: {self.driver.current_url}"
        )
        self.logger.info("断言发文章页面加载完成，url 含 circle/publish")

    def click_upload_cover_button(self):
        self.logger.info("点击上传封面按钮")
        self.driver.find_element(*UPLOAD_COVER_BUTTON).click()
    
        # 切回native_app
        self.webview_operate.switch_to_native()
        self.logger.info("已切换回native app 页面")
        # 等待选择图片按钮出现
        self.wait.until(
            EC.presence_of_element_located(SELECT_IMAGE_BUTTON)
        )
    def click_select_image_button(self):
        self.driver.find_element(*SELECT_IMAGE_BUTTON).click()
        self.logger.info("点击选择图片按钮")

        # 等图片权限授权弹窗出现（系统弹窗，native context）
        # 出现就点允许；不出现（之前已授权过）就跳过
    def click_permission_allow_button(self):
        self.logger.info("等待图片权限授权弹窗出现")
        try:
            self.wait.until(
                EC.presence_of_element_located(PERMISSION_ALLOW_BUTTON)
            )
            self.driver.find_element(*PERMISSION_ALLOW_BUTTON).click()
            self.logger.info("已点击图片权限允许按钮")
        except Exception as e:
            self.logger.info(
                f"未出现图片权限授权弹窗（可能已授权），跳过: "
                f"{e.__class__.__name__}"
            )

        # 等相册界面加载完成
        # 勾选图片
    def click_gouxuan_image_button(self):
        """勾选相册中图片）。
        """
        self.logger.info(
            f"等待相册界面加载完成，准备勾选图片"
        )
        # 用 XPath 轴语法 [.//...] 在父节点下找子节点作为过滤条件
        # 等价 SQL: SELECT ll_check WHERE EXISTS(check_text WHERE text='')
        xpath = (
            "(//android.widget.LinearLayout[@resource-id='com.changan.oushangCos1:id/ll_check']"
            "[.//android.widget.TextView[@resource-id='com.changan.oushangCos1:id/check' and @text='']])[3]"
        )
        from selenium.webdriver.common.by import By
        dynamic_locator = (By.XPATH, xpath)
        try:
            self.wait.until(
                EC.element_to_be_clickable(dynamic_locator),
                f"5s 内未找到勾选的图片",
            ).click()
            self.logger.info(f"已勾选图片")
        except Exception as e:
            self.logger.warning(
                f"勾选图片失败: "
                f"{e.__class__.__name__}"
            )
        # 断言图片勾选成功
        self.wait.until(
            EC.presence_of_element_located(GOUXUAN_IMAGE_CHECKED)
        )
        self.logger.info("已断言图片勾选成功")

    # 点击已完成按钮
    def click_confirm_gouxuan_image_button(self):
        self.driver.find_element(*CONFIRM_GOUXUAN_IMAGE_BUTTON).click()
        self.logger.info("点击已完成按钮")

    # 点击封面图片确认按钮
    def click_confirm_cover_image_button(self):
        self.driver.find_element(*CONFIRM_COVER_IMAGE_BUTTON).click()
        self.logger.info("点击封面图片确认按钮")

        # 点击封面确认按钮后界面会回到 H5 编辑页，切回 WebView 才能继续后续 H5 操作
        self.webview_operate.switch_to_webview()
        self.logger.info("已切换回发文章编辑页面的webview")
        
        # 切换到发文章编辑页面的webview
    def switch_to_post_article_webview(self):
        self.webview_operate.switch_to_webview()
        self.logger.info("已切换到发文章编辑页面的webview")
        # 打印 url + title
        try:
            self.logger.info(f"当前页面url: {self.driver.current_url}")
            self.logger.info(f"当前页面title: {self.driver.title}")
        except Exception as e:
            self.logger.error(f"获取当前页面url + title失败: {e}")

        # 断言发文章页面加载完成（用 url 含 circle/publish 判断，封面元素还没上传不在此处断言）
        assert "circle/publish" in self.driver.current_url, (
            f"期望 url 包含 circle/publish，实际: {self.driver.current_url}"
        )
        self.logger.info("断言发文章页面加载完成，url 含 circle/publish")

    # 点击标题输入框，输入标题
    def click_title_input(self, title: str = "此刻我想吟诗一首"):
        """点击标题输入框并输入文本。

        Args:
            title: 要填入的标题内容，默认 "此刻我想吟诗一首"。
        """
        self.driver.find_element(*TITLE_INPUT).click()
        self.logger.info("点击标题输入框")
        self.driver.find_element(*TITLE_INPUT).send_keys(title)
        self.logger.info(f"输入标题: {title}")

    # 点击内容输入框，输入内容
    def click_content_input(
        self,
        content_text: str = (
            "远看山有色，近看山无色。近看山有影，远看山无影。"
            "春去春来，山色不改。秋去冬来，白雪皑皑。一去二三里，天色不早矣"
        ),
        expected_keyword: str = "远看山有色",
    ):
        """点击内容输入框，用 JS 注入方式写入内容（适用于 contenteditable 富文本）。

        Args:
            content_text: 要写入的内容文本。
            expected_keyword: 断言必须包含的关键字，默认 "远看山有色"。
        """
        # 先 click 触发 needsclick（部分富文本组件需要真实的鼠标事件）
        content_el = self.driver.find_element(*CONTENT_INPUT)
        content_el.click()
        self.logger.info("点击内容输入框")

        # contenteditable 富文本编辑器不能直接 send_keys，改用 JS：
        # 1) focus() 拿到光标 2) innerText 写入 3) 派发 input/change 事件让 Vue 响应式感知
        self.driver.execute_script(
            """
            const el = arguments[0];
            const text = arguments[1];
            el.focus();
            el.innerText = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            """,
            content_el,
            content_text,
        )
        self.logger.info("输入内容（JS 注入方式）")

        # 断言页面内容文本包含期望关键字，则输入成功
        actual_text = self.driver.execute_script(
            "return arguments[0].innerText || arguments[0].textContent",
            content_el,
        )
        assert expected_keyword in actual_text, (
            f"内容输入失败，期望包含 '{expected_keyword}'，实际: {actual_text}"
        )
        self.logger.info("内容输入成功")

    # 点击内容图片上传按钮
    def click_content_image_button(self):
        self.driver.find_element(*CLICK_CONTENT_IMAGE_BUTTON).click()
        self.logger.info("点击内容图片上传按钮")
        # 断言出现选择图片弹窗按钮SELECT_CONTENT_IMAGE_BUTTON
        self.wait.until(
            EC.presence_of_element_located(SELECT_CONTENT_IMAGE_BUTTON)
        )
        self.logger.info("已断言出现选择图片弹窗按钮SELECT_CONTENT_IMAGE_BUTTON")

    # 点击选择图片弹窗按钮
    def click_select_content_image_button(self):
        self.driver.find_element(*SELECT_CONTENT_IMAGE_BUTTON).click()
        self.logger.info("点击选择图片弹窗按钮")

        # 切换回native-app
        self.webview_operate.switch_to_native()
        self.logger.info("已切换回native-app")
        # 勾选图片
    def click_gouxuan_image_button(self):
        """勾选相册中图片）。
        """
        self.logger.info(
            f"等待相册界面加载完成，准备勾选图片"
        )
        # 用 XPath 轴语法 [.//...] 在父节点下找子节点作为过滤条件
        # 等价 SQL: SELECT ll_check WHERE EXISTS(check_text WHERE text='')
        xpath = (
            "(//android.widget.LinearLayout[@resource-id='com.changan.oushangCos1:id/ll_check']"
            "[.//android.widget.TextView[@resource-id='com.changan.oushangCos1:id/check' and @text='']])[3]"
        )
        from selenium.webdriver.common.by import By
        dynamic_locator = (By.XPATH, xpath)
        try:
            self.wait.until(
                EC.element_to_be_clickable(dynamic_locator),
                f"5s 内未找到勾选的图片",
            ).click()
            self.logger.info(f"已勾选图片")
        except Exception as e:
            self.logger.warning(
                f"勾选图片失败: "
                f"{e.__class__.__name__}"
            )
        # 断言图片勾选成功
        self.wait.until(
            EC.presence_of_element_located(GOUXUAN_IMAGE_CHECKED)
        )
        self.logger.info("已断言图片勾选成功")

    # 点击已完成按钮
    def click_confirm_gouxuan_image_button(self):
        self.driver.find_element(*CONFIRM_GOUXUAN_IMAGE_BUTTON).click()
        self.logger.info("点击已完成按钮")
        # 点完"已完成"后相册关闭，回到 H5 编辑页（不需要再等任何按钮）

    # 点击确定选择按钮
    def click_confirm_queding_image_button(self):
        self.driver.find_element(*CONFIRM_QUEDING_IMAGE_BUTTON).click()
        self.logger.info("点击确定选择按钮")
        # 切换回发文章编辑页面的webview
        self.webview_operate.switch_to_webview()
        self.logger.info("已切换到发文章编辑页面的webview")
        # 打印 url + title
        try:
            self.logger.info(f"当前页面url: {self.driver.current_url}")
            self.logger.info(f"当前页面title: {self.driver.title}")
        except Exception as e:
            self.logger.error(f"获取当前页面url + title失败: {e}")

        # 断言发文章页面加载完成（用 url 含 circle/publish 判断，封面元素还没上传不在此处断言）
        assert "circle/publish" in self.driver.current_url, (
            f"期望 url 包含 circle/publish，实际: {self.driver.current_url}"
        )
        self.logger.info("断言发文章页面加载完成，url 含 circle/publish")

    # 点击发布按钮
    def click_publish_button(self):
        publish_btn = self.driver.find_element(*PUBLISH_BUTTON)
        is_enabled = publish_btn.is_enabled()
        self.logger.info(f"发布按钮 enabled={is_enabled}")
        assert is_enabled, "发布按钮被禁用，表单可能不完整（标题/内容/封面缺失）"
        publish_btn.click()
        self.logger.info("点击发布按钮")

        # 给 App 一点时间：点击 → Vue 触发 → 接口 → H5 销毁 → 切回 native
        sleep(2)

        # 切回 native（App 自己会切；这里兜底再切一次，确保 native 上下文）
        self.webview_operate.switch_to_native()
        self.logger.info("已切换回native-app")
        self.logger.info("✅ 发布完成（按钮可点 + 已切回 native）")


    
        



