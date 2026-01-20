import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def scrape_chicken_republic():
    options = ChromiumOptions()
    options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")

    async with Chrome(options=options) as browser:
        tab = await browser.start()
        await tab.go_to("https://www.chicken-republic.com/menu/#affordable-value-meals")
        await asyncio.sleep(5)
        for i in range(5):
            await tab.refresh()
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(scrape_chicken_republic())
