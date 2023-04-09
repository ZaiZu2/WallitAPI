from enum import Enum


class TagsEnum(str, Enum):
    USER = "USER"
    TRANSACTIONS = "TRANSACTIONS"
    CATEGORIES = "CATEGORIES"

tags_metadata = [
    {
        "name": TagsEnum.USER,
        "description": "The operations related to the user's account. The login and password logic is contained here.",
    },
    {
        "name": TagsEnum.TRANSACTIONS,
        "description": "The operations used for managing transactions. CRUD operations, transaction filtering, etc.",
    },
    {
        "name": TagsEnum.CATEGORIES,
        "description": "The operations used for managing user's categories.",
    },
]
