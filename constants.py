from enum import Enum

class Xpaths(Enum):
    PRODUCT_CONTAINER = '//div[@class="Ms6aG"]'
    PRODUCT_PRICE = './/div[@class="aBrP0"]'
    PRODUCT_NAME = './/div[@class="RfADt"]'
    PRODUCT_SOLD = './/div[@class="_6uN7R"]/span[@class="_1cEkb"]'
    NEXT_PAGE = '//button[@class="ant-pagination-item-link"]/span[@aria-label="right"]'