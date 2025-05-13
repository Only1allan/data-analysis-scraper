from scrapy import Item, Field


class ManagerItem(Item):
    """Item representing a fund manager."""
    id = Field()
    name = Field()
    link = Field()


class FilingItem(Item):
    """Item representing a 13F filing."""
    manager_id = Field()
    manager_name = Field()
    quarter = Field()
    filing_url = Field()
    holdings = Field()
    value = Field()
    top_holdings = Field()
    form_type = Field()
    filing_date = Field()
    filing_id = Field()


class HoldingItem(Item):
    """Item representing a holding in a 13F filing."""
    manager_id = Field()
    manager_name = Field()
    filing_id = Field()
    filing_date = Field()
    quarter = Field()
    symbol = Field()
    issuer = Field()
    cl = Field()
    cusip = Field()
    value = Field()
    percentage = Field()
    shares = Field()
    principal = Field()
    option = Field()