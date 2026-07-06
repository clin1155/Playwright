import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

WORKSPACE = Path(".")
SCREENSHOTS = WORKSPACE / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        await page.goto("https://www.bot.com.tw", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        await page.screenshot(path=str(SCREENSHOTS / "explore_4_home.png"))

        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Get innerText and innerHTML of the whole body
        inner_text = await page.evaluate("() => document.body.innerText")
        print("\n=== BODY INNER TEXT ===")
        print(inner_text)

        # Get all elements that contain numeric rate values
        all_elements = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('*');
                const results = [];
                for (const el of all) {
                    if (el.children.length === 0 && el.textContent.trim()) {
                        const t = el.textContent.trim();
                        if (/^[0-9.]+$/.test(t)) {
                            results.push({
                                tag: el.tagName,
                                text: t,
                                parentClass: el.parentElement?.className || '',
                                parentTag: el.parentElement?.tagName || ''
                            });
                        }
                    }
                }
                return results;
            }
        """)
        print("\n=== NUMERIC VALUES ===")
        for r in all_elements:
            print(f"  {r}")

        await browser.close()

asyncio.run(main())
