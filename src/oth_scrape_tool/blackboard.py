import requests
from bs4 import BeautifulSoup


class BlackbordEntry:
    """
    Represents an entry on the blackboard and handles
    converting it to string and markdown
    """

    def __init__(self, title: str, published_at: str, content: str):
        self.title = title
        self.published_at = published_at
        self.content = content

    def __str__(self) -> str:
        return f'{self.title}\n{self.published_at} {self.content}'

    def to_markdown(self) -> str:
        return f'## {self.title}\n**{self.published_at}** {self.content}'


class Blackboard:
    """
    Responsible for scraping the OTH IM-Faculty blackboard
    and converting it's data to strings or markdown format.
    """

    def __init__(self, url: str):
        self.url = url
        self.entries: list[BlackbordEntry] = []

    def scrape(self) -> None:
        """
        Scrape the OTH Regensburg blackboard for entries.
        Args:
            url: The URL of the OTH Regensburg blackboard.
        Returns:
            A list of tuples containing the header and teaser text of each entry.
        """
        # Note: The User-Agent header is commented out, as it may not be necessary.
        # headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = requests.get(self.url)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        entries = soup.find_all('div', class_='header')
        more_links = soup.find_all('a', class_='more')

        for header, more_url in zip(entries, more_links, strict=True):
            header_text = header.get_text(strip=True)

            complete_url = self.url[:self.url.rfind(
                '/')] + more_url['href']  # type: ignore

            creation_date, content = self.scrape_contents(complete_url)

            self.entries.append(BlackbordEntry(
                header_text, creation_date, content))

    def scrape_contents(self, url: str) -> tuple[str, str]:
        """
        Scrapes the "more" url from the OTH Regensburg blackboard page and returns the text.
        Does a little markdown formatting for the time.
        Args:
            url: The URL of the "more" link to scrape.
        Returns:
            a tuple of the creation time and content
        """
        res = requests.get(url)
        res.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(res.text, 'html.parser')

        # find the time of creation
        time = soup.find('time', itemprop='datePublished')
        # Find the content in the page
        content = soup.find('span', itemprop='description')

        if content:
            # type: ignore
            return time.get_text(strip=True), content.get_text(strip=True)
        else:
            raise ValueError(f"No content found at {
                             url}. The structure of the page may have changed.")

    def __str__(self) -> str:
        res = ''
        for entry in self.entries:
            res += f'{entry}\n'
        return res

    def to_markdown_str(self) -> str:
        """
        Converts the blackboard to a markdown string
        """
        res = ''
        for entry in self.entries:
            res += entry.to_markdown() + '\n'
        return res
