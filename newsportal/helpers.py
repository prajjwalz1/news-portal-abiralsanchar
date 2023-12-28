from django.utils.text import slugify
from unidecode import unidecode


def custom_slugify(s):
    # Use unidecode to transform non-English i.e. Nepali Language characters into English equivalents
    s = unidecode(s)
    return slugify(s)
