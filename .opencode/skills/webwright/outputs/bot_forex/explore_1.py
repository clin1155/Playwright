import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

WORKSPACE = Path("outputs/bot_forex")
SCREENSHOTS = WORKSPACE / "screenshots"
SCREENSHOTS.mkdir(parents=True, exist_ok=True)

async def main():
    async with async_playwright() as playwright:
        browser = await playwright.firefox.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 1800})
        page = await context.new_page()

        await page.goto("https://www.bot.com.tw", wait_until="domcontentloaded")
        await page.screenshot(path=str(SCREENSHOTS / "explore_1_home.png"))

        print("URL:", page.url)
        print("TITLE:", await page.title())

        snapshot = await page.locator("body").aria_snapshot()
        print("ARIA:", snapshot)

        await browser.close()

asyncio.run(main())
