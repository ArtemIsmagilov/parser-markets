#!/usr/bin/env python

import asyncio
import csv

import httpx
from bs4 import (
    BeautifulSoup,
    Tag,
)


class AssortmentMetro:
    def __init__(self, q: str, filename: str = "egg.csv"):
        self.base_url = "https://online.metro-cc.ru"
        self.endpoint = "/search"
        self.q = q
        self.filename = filename
        self.products = []

    def parsing(self):
        response = httpx.get(url=self.base_url + self.endpoint, params={"q": self.q})
        if response.status_code != 200:
            raise Exception(f"Error operation! Status code is {response.status_code}")

        soup = BeautifulSoup(response.text, "lxml")

        for product in soup.find_all(
            "div",
            class_="catalog-2-level-product-card product-card page-search__products-item with-prices-drop",
        ):
            price_actual = product.find(
                "div", class_="product-unit-prices__actual-wrapper"
            )

            product_actual_rubles = price_actual.find(
                "span", class_="product-price__sum-rubles"
            )
            product_actual_penny = price_actual.find(
                "span", class_="product-price__sum-penny"
            )

            price_old = product.find("div", class_="product-unit-prices__old-wrapper")

            product_old_rubles = price_old.find(
                "span", class_="product-price__sum-rubles"
            )
            product_old_penny = price_old.find(
                "span", class_="product-price__sum-penny"
            )

            product_name = product.find("span", class_="product-card-name__text")

            product_link = product.find(
                "a", class_="product-card-photo__link reset-link"
            )

            p_obj = Product(
                parse_id_tag_metro(product),
                parse_text_tag_metro(product_name),
                parse_link_tag_metro(self.base_url, product_link),
                parse_text_tag_metro(product_actual_rubles),
                parse_text_tag_metro(product_actual_penny),
                parse_text_tag_metro(product_old_rubles),
                parse_text_tag_metro(product_old_penny),
            )

            self.products.append(p_obj)

    def convert_to_csv(self):
        with open(self.filename, "w") as csv_file:
            fieldnames = ["product_id", "name", "link", "actual_price", "old_price"]
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(fieldnames)
            csv_writer.writerows(
                [p.product_id, p.name, p.link, p.ac_price, p.old_price]
                for p in self.products
            )

    def run(self):
        self.parsing()
        self.convert_to_csv()


class Product:
    def __init__(
        self,
        product_id: str | None,
        name: str | None,
        link: str | None,
        ac_rub: str | None,
        ac_pen: str | None,
        old_rub: str | None,
        old_pen: str | None,
    ):
        self.product_id = product_id
        self.name = name
        self.link = link
        self.ac_rub = ac_rub
        self.ac_pen = ac_pen
        self.old_rub = old_rub
        self.old_pen = old_pen

    @property
    def ac_price(self):
        if self.ac_rub and self.ac_pen:
            return self.ac_rub + self.ac_pen
        elif self.ac_rub:
            return self.ac_rub

    @property
    def old_price(self):
        if self.old_rub and self.old_pen:
            return self.old_rub + self.old_pen
        elif self.old_rub:
            return self.old_rub


def parse_text_tag_metro(tag: Tag | None):
    if tag:
        return tag.get_text(strip=True)


def parse_link_tag_metro(domain_url, tag: Tag | None):
    if tag:
        return domain_url + tag.get("href")


def parse_id_tag_metro(tag: Tag | None):
    if tag:
        return tag.get("id")


async def main():
    a = AssortmentMetro("яблоки")
    a.run()


asyncio.run(main())
