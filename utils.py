"""SaudiExchange eReference Data utils

https://www.saudiexchange.sa/wps/portal/saudiexchange/trading/market-services/market-information-services/ereference-data?locale=en
"""
import re
from pathlib import Path
from functools import cached_property

import pandas as pd

__all__ = ["SectorData", "commission"]

SECTORS_AR = (
    "إدارة وتطوير العقارات",
    "السلع الرأسمالية",
    "الطاقة",
    "تجزئة السلع الكمالية",
    "التأمين",
    "المواد الأساسية",
    "الرعاية الصحية",
    "إنتاج الأغذية",
    "البنوك",
    "تجزئة الأغذية",
    "النقل",
    "السلع طويلة الاجل",
    "الخدمات الإستهلاكية",
    "الإعلام والترفيه",
    "الادوية",
    "الإستثمار والتمويل",
    "المرافق العامة",
    "الخدمات التجارية والمهنية",
    "الإتصالات",
    "الصناديق العقارية المتداولة",
    "التطبيقات وخدمات التقنية",
)

SECTORS_EN = (
    "Real Estate Mgmt & Dev't",
    "Capital Goods",
    "Energy",
    "Retailing",
    "Insurance",
    "Materials",
    "Health Care Equipment & Svc",
    "Food & Beverages",
    "Banks",
    "Food & Staples Retailing",
    "Transportation",
    "Consumer Durables & Apparel",
    "Consumer Services",
    "Media and Entertainment",
    "Pharma, Biotech & Life Science",
    "Diversified Financials",
    "Utilities",
    "Commercial & Professional Svc",
    "Telecommunication Services",
    "REITs",
    "Software & Services",
)


def _read_bad_csv(path: str | Path, count: int) -> pd.DataFrame:
    def fix(fields):
        *fields, news = ",".join(fields).split(",", count)
        return fields + re.split(r"(?!\d),(?!\d)", news, 1)

    return pd.read_csv(
        path,
        encoding="utf-8-sig",
        sep="(?! ),(?! )",
        parse_dates=[[-4, -3]],
        on_bad_lines=fix,
        engine="python",
    )


def read_prices(path: str | Path) -> pd.DataFrame:
    """Read Equites_Historical_Adjusted_Prices_Report.csv"""
    path = Path(path) / "Equites_Historical_Adjusted_Prices_Report.csv"
    return pd.read_csv(
        path,
        encoding="utf-8-sig",
        parse_dates=[3],
        date_format="%d-%b-%y",
        index_col=False,
    )


def read_market_news(path: str | Path, by_day="[SEP]") -> pd.DataFrame:
    """Read Market_News_Report.csv"""
    path = Path(path) / "Market_News_Report.csv"
    df = _read_bad_csv(path, 2)
    if by_day:
        df.fillna("", inplace=True)
        date, title, _ = df.columns
        df[date] = df[date].dt.date
        group = df.groupby(date)
        df = group[title].apply(f" {by_day} ".join).reset_index()
    return df


def read_company_news(path: str | Path, by_sector="[SEP]") -> pd.DataFrame:
    """Read Company_Announcement_Report.csv"""
    path = Path(path) / "Company_Announcement_Report.csv"
    df = _read_bad_csv(path, 5)
    if by_sector:
        df.fillna("", inplace=True)
        date, sector, *_, title, _ = df.columns
        df[date] = df[date].dt.date
        group = df.groupby([date, sector])
        df = group[title].apply(f" {by_sector} ".join).reset_index()
    return df


def merge_news(
    sector_news: pd.DataFrame, market_news: pd.DataFrame, sep=""
) -> pd.DataFrame:
    """Merge sector news and market_news"""
    date, title = sector_news.columns
    df = sector_news.set_index(date)
    df = market_news.set_index(date).join(df, how="outer", lsuffix="_")
    df.fillna("", inplace=True)
    if sep:
        df[title] += f" {sep} " + df.pop(title + "_")
    df.reset_index(inplace=True)
    return df


def sector_prices(prices: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Get prices per sector"""
    if not isinstance(prices, pd.DataFrame):
        prices = read_prices(prices)
    sector, date, close, change = prices.columns[[0, 3, -6, -5]]

    def change_percent(x):
        old = (x[close] - x[change]).sum()
        return 0 if old == 0 else 100 * x[change].sum() / old

    df = prices.groupby([date, sector]).apply(change_percent).reset_index()
    df.rename({0: prices.columns[-4]}, axis=1, inplace=True)
    return df


def select(data: pd.DataFrame, column: str, value) -> pd.DataFrame:
    """Filter rows where `data[column] == value`"""
    return data[data[column] == value].drop(column, axis=1)


def sector_data(company_news, market_news, prices, sector_name):
    """Extract sector news and prices per day"""
    sector = company_news.columns[1]
    sec_df = select(company_news, sector, sector_name)
    sec_df = merge_news(sec_df, market_news)
    sec_df.set_index(sec_df.columns[0], inplace=True)
    df = select(prices, sector, sector_name)
    df.set_index(df.columns[0], inplace=True)
    df = sec_df.join(df)
    df.reset_index(inplace=True)
    df.dropna(inplace=True)
    return df


class SectorData:
    """SaudiExchange eReference Data"""

    def __init__(self, path):
        self.path = path
        # hard coded sector names to unify the order of sectors for all languages
        self.names = SECTORS_EN if "Date" in self.market.columns[0] else SECTORS_AR

    @cached_property
    def prices(self):
        """Sector price change %"""
        return sector_prices(self.path)

    @cached_property
    def company(self):
        """Sector companies' news"""
        return read_company_news(self.path)

    @cached_property
    def market(self):
        """Market news"""
        return read_market_news(self.path)

    def sector(self, name: str | int):
        """Sector and market news with price change %"""
        if not isinstance(name, str):
            name = self.names[name]
        return sector_data(self.company, self.market, self.prices, name)

    def __getitem__(self, index):
        if not isinstance(index, str):
            index = self.names[index]
        return index, self.sector(index)


def commission(broker=10.5e-4, tadawul=5e-4, cma_fee=3.2e-4, vat=0.15):
    r"""Calculate CMA commission + VAT for trading stocks in Saudi Exchange

    When trading stocks, usually there are applied fees/taxes.
    In the Saudi stock market (Saudi Exchange, a.k.a. Tadawul), the fees inculde:
    - the borker fees,
    - Tadawul fees,
    - the Capital Market Authority (CMA) commission,
    - and the Saudi Value Added Tax (VAT).

    The total commission ($\approx 0.0017375$ per $1$ SAR)
    - will be added to the price of any buy trade
    - and subtracted from any sell trade.
    Therefore, it is important to account for these fees when considering to buy or sell.

    If a stock costs $30$ SAR per share, and we want to buy $10$ shares we will have to pay:
    $$30 \times 10 \times (1 + 0.0017375) \approx 300.52$$

    If a stock costs $30$ SAR per share, and we want to sell $10$ shares we will receive:
    $$30 \times 10 \times (1 - 0.0017375) \approx 299.48$$
    """
    # https://www.argaam.com/en/article/articledetail/id/1387911
    cma_fee = round(cma_fee, 4)  # this rounding is noticed in actual trades
    vat_fee = vat * (broker + tadawul - cma_fee)  # value added tax
    return broker + tadawul + vat_fee  # 0.0017375
