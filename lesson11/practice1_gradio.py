import gradio as gr
from datetime import datetime
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
import os


def launch_browser(p: Playwright) -> Browser:
    return p.chromium.launch()


def search_wikipedia(page: Page, keyword: str) -> str:
    page.goto("https://zh.wikipedia.org")
    page.locator("#searchInput").fill(keyword)
    screenshot_path = os.path.join(
        os.path.dirname(__file__),
        f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
    )
    page.screenshot(path=screenshot_path)
    page.keyboard.press("Enter")
    page.wait_for_load_state("networkidle")
    return screenshot_path


def get_search_result(page: Page) -> dict:
    heading: str = page.locator("#firstHeading").inner_text()
    elements = page.locator("#mw-content-text p")
    content: str = elements.first.inner_text() if elements.count() > 0 else ""
    return {"heading": heading, "content": content}


def crawl(keyword: str):
    screenshot_path = None
    with sync_playwright() as p:
        browser: Browser = launch_browser(p)
        try:
            page: Page = browser.new_page()
            screenshot_path = search_wikipedia(page, keyword)
            result: dict = get_search_result(page)

            page.go_back()
            page.wait_for_load_state("networkidle")

            return (
                result["heading"],
                result["content"],
                screenshot_path,
                f"已完成對「{keyword}」的搜尋並返回首頁：{page.title()}",
            )
        except Exception as e:
            return (
                "搜尋失敗",
                str(e),
                None,
                f"爬蟲執行失敗: {e}",
            )
        finally:
            browser.close()


custom_css = """
.gradio-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}
#main-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(10px);
}
#main-card h1 {
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-size: 2.5em;
    margin-bottom: 10px;
}
#main-card h3 {
    text-align: center;
    color: #666;
    font-weight: 300;
    margin-bottom: 30px;
}
.search-section {
    background: #f8f9ff;
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 20px;
    border: 1px solid #e0e5ff;
}
.result-section {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 15px;
    padding: 25px;
    border: 1px solid #e0e5ff;
}
.result-section h2 {
    color: #4a5568;
    font-size: 1.3em;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #667eea;
}
footer {
    display: none !important;
}
"""

with gr.Blocks(
    theme=gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui"],
    ),
    title="維基百科爬蟲",
    css=custom_css,
) as demo:
    gr.HTML(
        """
        <div id="main-card">
            <h1>維基百科爬蟲</h1>
            <h3>輸入關鍵字，自動搜尋維基百科並擷取結果</h3>
        </div>
        """
    )

    with gr.Row(elem_id="main-card"):
        with gr.Column(scale=1, elem_classes="search-section"):
            gr.Markdown("### 搜尋設定")
            keyword_input = gr.Textbox(
                label="關鍵字",
                placeholder="請輸入維基百科搜尋關鍵字...",
                value="Benjamin Franklin",
                elem_id="keyword-box",
            )
            search_btn = gr.Button(
                "開始搜尋",
                variant="primary",
                size="lg",
                elem_id="search-btn",
            )
            gr.Examples(
                examples=[
                    ["Benjamin Franklin"],
                    ["Python (程式語言)"],
                    ["台灣"],
                    ["人工智慧"],
                ],
                inputs=keyword_input,
                label="快速選擇範例",
            )

        with gr.Column(scale=2, elem_classes="result-section"):
            gr.Markdown("### 搜尋結果")
            with gr.Row():
                heading_output = gr.Textbox(
                    label="頁面標題",
                    interactive=False,
                    elem_id="heading-box",
                )
            with gr.Row():
                content_output = gr.Textbox(
                    label="摘要內容",
                    lines=5,
                    interactive=False,
                    elem_id="content-box",
                )
            with gr.Row():
                status_output = gr.Textbox(
                    label="狀態",
                    interactive=False,
                    elem_id="status-box",
                )
            with gr.Row():
                screenshot_output = gr.Image(
                    label="搜尋截圖",
                    type="filepath",
                    elem_id="screenshot-box",
                )

    search_btn.click(
        fn=crawl,
        inputs=keyword_input,
        outputs=[heading_output, content_output, screenshot_output, status_output],
    )

if __name__ == "__main__":
    demo.launch()
