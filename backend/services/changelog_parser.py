from typing import Dict, List, Any, cast
from datetime import datetime
import logging
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class ChangelogParser:
    """Parser for extracting structured data from Cursor changelog HTML."""

    def parse_changelog(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Parse the HTML content of the Cursor changelog page and extract structured data.

        Args:
            html_content: The HTML content of the changelog page

        Returns:
            A list of dictionaries containing structured changelog entries
        """
        logger.info("Parsing changelog HTML content")
        soup = BeautifulSoup(html_content, "lxml")

        articles = soup.find_all("article")
        logger.info(f"Found {len(articles)} changelog entries")

        changelog_entries = []

        for article_element in articles:
            try:
                article = cast(Tag, article_element)
                date_version_text = article.get_text().strip().split("\n")[0]
                date_str = (
                    date_version_text.split("0.")[0].strip()
                    if "0." in date_version_text
                    else date_version_text
                )

                version = None
                if "0." in date_version_text:
                    version = "0." + date_version_text.split("0.")[1].strip()

                try:
                    date_obj = datetime.strptime(date_str, "%B %d, %Y")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    logger.warning(f"Could not parse date: {date_str}")
                    formatted_date = date_str

                title_element = article.find("h2")
                title = (
                    cast(Tag, title_element).get_text().strip()
                    if title_element
                    else "No title"
                )

                description = ""

                current_tag = article.find("h2")
                if current_tag:
                    next_sibling = current_tag.next_sibling
                    while next_sibling and not (
                        isinstance(next_sibling, Tag)
                        and getattr(next_sibling, "name", "") == "h3"
                    ):
                        if hasattr(next_sibling, "strip") and callable(
                            getattr(next_sibling, "strip")
                        ):
                            stripped = getattr(next_sibling, "strip")()
                            if stripped:
                                description += stripped + " "
                        next_sibling = getattr(next_sibling, "next_sibling", None)

                for element in article.find_all(["p", "ul"]):
                    element_tag = cast(Tag, element)
                    if element_tag.find_previous(
                        "h2"
                    ) and not element_tag.find_previous("h3"):
                        description += element_tag.get_text().strip() + " "

                tags = []
                for h3 in article.find_all("h3"):
                    tags.append(cast(Tag, h3).get_text().strip())

                entry = {
                    "date": formatted_date,
                    "version": version,
                    "title": title,
                    "description": description.strip(),
                    "tags": tags,
                    "html_content": str(article),  # Store original HTML for reference
                    "id": (
                        f"{formatted_date}-{version}" if version else formatted_date
                    ),  # Create a unique ID for deduplication
                }

                changelog_entries.append(entry)
                logger.debug(f"Parsed entry: {entry['date']} - {entry['title']}")

            except Exception as e:
                logger.error(f"Error parsing changelog entry: {e}")
                continue

        return changelog_entries
