
from steel import Steel
from playwright.async_api import async_playwright
from browser_use import Agent, BrowserSession
from browser_use.llm import ChatAnthropic
import os
from dotenv import load_dotenv

# List of websites to look for plugins in
WEBSITES = [
    "https://hangar.papermc.io/",
]

# This class defines the web agent that will get the plugins from plugin websites
class WebAgent:
    load_dotenv()
    __api_key = os.getenv("STEEL_API_KEY")
    __api_key_claude = os.getenv("ANT_API_KEY")

    print("<APP> Starting Web Agent Loop")

    def __init__(self):
        # Create Steel client
        self.client = Steel(steel_api_key=self._WebAgent__api_key)

    async def plugin_search(self, prompt:str):
        
        # Go through every website in WEBSITES
        for url in WEBSITES:
            # Create a web browsing session
            self.session = self.client.sessions.create(
                use_proxy={"geolocation": {"country": "CA"}},
                solve_captcha=True,
                stealth_config={
                    "auto_captcha_solving": True,
                    "humanize_interactions": True,
                },
            )
            print("<BROWSER> Session created")

            # Sets up a flag for Playwright
            pw = None

            try:
                # Create URL for CDP
                cdp_url = f"{self.session.websocket_url}&apiKey={self._WebAgent__api_key}"

                # Create Playwright
                pw = await async_playwright().start()
                print("<TERMINAL> Playwright started")

                # Create browser
                browser = await pw.chromium.connect_over_cdp(cdp_url)
                print("<TERMINAL> Playwright connected")

                # Grabs context
                context = browser.contexts[0]

                # Create a browser session for Browser Use
                browser_session = BrowserSession(
                    cdp_url=cdp_url,
                    cross_origin_iframes=False
                )
                print("<TERMINAL> Browser Use connected")

                # Create the agent to do the task
                agent = Agent(
                    task = f"""You are already on {url}.
                
                            Work only on {url} and its subdomains.
                            NEVER use a web search engine and never navigate to another website.
                            Use this websites search box and look for a Minecraft PaperMC plugin that based on the users prompt:
                            {prompt}

                            Look through the search results and find the plugin that performs/conforms to the prompt the best.
                            Once you find the best plugin, navigate to the download button for the .jar and return the link address, beacuse it will be passed to an agent controlling a remote Linux computer and will perform wget on the domain you return to download the .jar file.
                            Again: return ONLY the LINK ADDRESS and NOTHING ELSE, as whatever you return will be DIRECTLY PLUGGED INTO THE BASH COMMAND.""",
                    llm = ChatAnthropic(
                        model = "claude-haiku-5-5",
                        api_key = self._WebAgent__api_key_claude
                    ),
                    browser_session = browser_session,
                )
                print("<TERMINAL> Agent started")

                # Load and go to new page
                page = await context.new_page()
                response = await page.goto(url, wait_until="domcontentloaded", timeout=60_000)

                # Check if Agent is blocked
                if response is not None and response.status >= 400:
                    print(f"<TERMINAL> Blocked by {url}: HTTP {response.status}")
                    continue

                # Run the agent to perform the task
                result = await agent.run()
                print(f"<TERMINAL> Download Address Found: {result.final_result()}")
                

            # Release the session
            finally:
                if pw is not None:
                    await pw.stop()
                self.client.sessions.release(self.session.id)
                print("Session closed")

            return result.final_result()


# Current workflow uses a loop but theres only one site being tested right now






