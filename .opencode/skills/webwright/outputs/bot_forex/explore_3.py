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
        await page.screenshot(path=str(SCREENSHOTS / "explore_3_home.png"))

        print("URL:", page.url)
        print("TITLE:", await page.title())

        # Find the forex rate section - look for USD text
        # Get HTML around the USD rate area
        rate_section = await page.evaluate("""
            () => {
                // Find the element containing '即時匯率' or 'USD'
                const body = document.body;
                const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, null, false);
                let node;
                while (node = walker.nextNode()) {
                    if (node.textContent.includes('USD')) {
                        const parent = node.parentElement;
                        return {
                            text: parent.textContent.trim(),
                            outerHTML: parent.outerHTML.substring(0, 2000),
                            tagName: parent.tagName,
                            className: parent.className,
                            id: parent.id
                        };
                    }
                }
                return 'USD not found';
            }
        """)
        print("\n=== USD RATE SECTION ===")
        print(rate_section)

        # Also look for the rate table more broadly
        table_html = await page.evaluate("""
            () => {
                // Find tables or elements with rate data
                const allDivs = document.querySelectorAll('div');
                for (const div of allDivs) {
                    if (div.textContent.includes('USD') && div.textContent.includes('現金買入')) {
                        return {
                            html: div.outerHTML.substring(0, 5000),
                            id: div.id,
                            classes: div.className
                        };
                    }
                }
                return 'table not found';
            }
        """)
        print("\n=== RATE TABLE HTML ===")
        print(table_html)

        # Get the specific text nodes around USD rates
        rates_text = await page.evaluate("""
            () => {
                const body = document.body;
                const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT, null, false);
                const results = [];
                let node;
                while (node = walker.nextNode()) {
                    const t = node.textContent.trim();
                    if (t && (t.includes('USD') || t.includes('現金買入') || t.includes('現金賣出') || 
                        t.includes('即期買入') || t.includes('即期賣出') || t.includes('更新時間'))) {
                        results.push(t);
                    }
                }
                return results;
            }
        """)
        print("\n=== RATES TEXT NODES ===")
        for r in rates_text:
            print(f"  '{r}'")

        await browser.close()

asyncio.run(main())
