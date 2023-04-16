from enum import Enum
from functools import lru_cache

from pydantic import BaseSettings


class CurrenciesEnum(str, Enum):
    AED = "AED"
    AFN = "AFN"
    ALL = "ALL"
    AMD = "AMD"
    ANG = "ANG"
    AOA = "AOA"
    ARS = "ARS"
    AUD = "AUD"
    AZN = "AZN"
    BAM = "BAM"
    BDT = "BDT"
    BGN = "BGN"
    BHD = "BHD"
    BIF = "BIF"
    BMD = "BMD"
    BND = "BND"
    BOB = "BOB"
    BRL = "BRL"
    BSD = "BSD"
    BTN = "BTN"
    BWP = "BWP"
    BYN = "BYN"
    BZD = "BZD"
    CAD = "CAD"
    CDF = "CDF"
    CHF = "CHF"
    CLP = "CLP"
    CNY = "CNY"
    COP = "COP"
    CRC = "CRC"
    CUC = "CUC"
    CUP = "CUP"
    CVE = "CVE"
    CZK = "CZK"
    DJF = "DJF"
    DKK = "DKK"
    DOP = "DOP"
    DZD = "DZD"
    EGP = "EGP"
    ERN = "ERN"
    ETB = "ETB"
    EUR = "EUR"
    FJD = "FJD"
    FKP = "FKP"
    GBP = "GBP"
    GEL = "GEL"
    GHS = "GHS"
    GIP = "GIP"
    GMD = "GMD"
    GNF = "GNF"
    GTQ = "GTQ"
    GYD = "GYD"
    HKD = "HKD"
    HNL = "HNL"
    HUF = "HUF"
    IDR = "IDR"
    ILS = "ILS"
    INR = "INR"
    IQD = "IQD"
    IRR = "IRR"
    ISK = "ISK"
    JMD = "JMD"
    JOD = "JOD"
    JPY = "JPY"
    KES = "KES"
    KGS = "KGS"
    KHR = "KHR"
    KMF = "KMF"
    KPW = "KPW"
    KRW = "KRW"
    KWD = "KWD"
    KYD = "KYD"
    KZT = "KZT"
    LAK = "LAK"
    LBP = "LBP"
    LKR = "LKR"
    LRD = "LRD"
    LSL = "LSL"
    LYD = "LYD"
    MAD = "MAD"
    MDL = "MDL"
    MGA = "MGA"
    MKD = "MKD"
    MMK = "MMK"
    MNT = "MNT"
    MOP = "MOP"
    MRU = "MRU"
    MUR = "MUR"
    MVR = "MVR"
    MWK = "MWK"
    MXN = "MXN"
    MYR = "MYR"
    MZN = "MZN"
    NAD = "NAD"
    NGN = "NGN"
    NIO = "NIO"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    OMR = "OMR"
    PAB = "PAB"
    PEN = "PEN"
    PGK = "PGK"
    PHP = "PHP"
    PKR = "PKR"
    PLN = "PLN"
    PYG = "PYG"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RUB = "RUB"
    RWF = "RWF"
    SAR = "SAR"
    SBD = "SBD"
    SCR = "SCR"
    SDG = "SDG"
    SEK = "SEK"
    SGD = "SGD"
    SHP = "SHP"
    SLL = "SLL"
    SOS = "SOS"
    SRD = "SRD"
    STN = "STN"
    SVC = "SVC"
    SYP = "SYP"
    SZL = "SZL"
    THB = "THB"
    TJS = "TJS"
    TMT = "TMT"
    TND = "TND"
    TOP = "TOP"
    TRY = "TRY"
    TTD = "TTD"
    TWD = "TWD"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    USD = "USD"
    UYU = "UYU"
    UZS = "UZS"
    VND = "VND"
    VUV = "VUV"
    WST = "WST"
    XAF = "XAF"
    XAG = "XAG"
    XAU = "XAU"
    XCD = "XCD"
    XDR = "XDR"
    XOF = "XOF"
    XPF = "XPF"
    YER = "YER"
    ZAR = "ZAR"
    ZMW = "ZMW"


class Config(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 3

    SQLALCHEMY_DATABASE_URI: str

    # Currency conversion API
    CURRENCYSCOOP_API_KEY: str
    CURRENCYSCOOP_HISTORICAL_URL: str = "https://api.currencyscoop.com/v1/historical?api_key={key}&base=EUR&date={date}&symbols={symbols}"
    CURRENCYSCOOP_CURRENCIES_URL: str = (
        "https://api.currencybeacon.com/v1/currencies?api_key={key}"
    )


@lru_cache()
def get_config() -> Config:
    return Config()  # reads variables from environment


LOGGING_CONFIG = {
    "disable_existing_loggers": False,
    "formatters": {
        "access_file": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(client_addr)s %(request_line)s %(status_code)s",
            "use_colors": False,
        },
        "access_stream": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(client_addr)s %(request_line)s %(status_code)s",
            "use_colors": True,
        },
        "default_file": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": False,
        },
        "default_stream": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": True,
        },
    },
    "handlers": {
        "requests_to_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "access_file",
            "filename": "logs/requests.log",
            "maxBytes": 10240,
            "backupCount": 10,
        },
        "requests_to_stream": {
            "class": "logging.StreamHandler",
            "formatter": "access_stream",
            "stream": "ext://sys.stdout",
        },
        "errors_to_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default_file",
            "filename": "logs/internal.log",
            "maxBytes": 10240,
            "backupCount": 10,
        },
        "errors_to_stream": {
            "class": "logging.StreamHandler",
            "formatter": "default_stream",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "uvicorn.access": {
            "handlers": ["requests_to_file", "requests_to_stream"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["errors_to_file", "errors_to_stream"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["errors_to_file", "errors_to_stream"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "version": 1,
}
