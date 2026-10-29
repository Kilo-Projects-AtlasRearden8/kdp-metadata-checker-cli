"""Book metadata model for the KDP metadata checker."""


from typing import Optional


class BookMetadata:
    """Title, subtitle, description, categories, and keywords for one book."""

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        description: str = "",
        categories: Optional[list[str]] = None,
        keywords: Optional[list[str]] = None,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.categories = list(categories or [])
        self.keywords = list(keywords or [])

    @classmethod
    def from_dict(cls, data: dict) -> "BookMetadata":
        return cls(
            title=str(data.get("title", "")),
            subtitle=str(data.get("subtitle", "")),
            description=str(data.get("description", "")),
            categories=[str(item) for item in data.get("categories", [])],
            keywords=[str(item) for item in data.get("keywords", [])],
        )
