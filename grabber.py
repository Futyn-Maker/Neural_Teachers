import re
import sqlite3

from loguru import logger

from vk_api import VkApi, VkTools

from emoji import emoji_count
from urlextract import URLExtract

from config import VK_SERVICE_TOKEN, PUBLICS


extract = URLExtract()

# Setting up a log entry to a file
logger.add("grabber.log")

make_small = False  # set True to include only single-line quotes

db_name = "corpus"
if make_small:
    db_name += "_small"
db_name += ".db"

# Create a database and tables
db = sqlite3.connect(db_name)
cur = db.cursor()
cur.executescript("""
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY,
        public TEXT NOT NULL,
        text TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS garbage (
        id INTEGER PRIMARY KEY,
        public TEXT NOT NULL,
        text TEXT NOT NULL
    );
""")
logger.info("The database f{db_name} has been initialized")

# Initialize VK API and VK Tools
vk = VkApi(token=VK_SERVICE_TOKEN)
tools = VkTools(vk)
logger.info("Vk API has been initialized")


# Functions for filtering and clearing posts
def is_garbage(entry):
    """Tries to identify garbage posts, that is, those that do not belong to quotes"""
    if entry["marked_as_ads"] or \
        "is_pinned" in entry.keys() or \
        "copy_history" in entry.keys() or \
        entry["attachments"] or \
        emoji_count(entry["text"]) or \
        extract.has_urls(entry["text"]) or \
        "club" in entry["text"] or \
        "[id" in entry["text"] or \
        "__" in entry["text"]:
        return True
    return False


def clear_post(quote):
    """Clears the text of the post from hashtags, mentions and signatures"""
    quote = re.sub(r"#\w+", "", quote)  # remove hashtags
    quote = re.sub(r"@\w+", "", quote)  # remove mentions
    # Try to remove most common signatures
    quote = re.sub(r"((\(c\))|(\(с\))|©).*", "", quote, flags=re.I)
    quote = re.sub(r"\n\n.*$", "", quote.strip())
    quote = re.sub(r"\n\s*[(\[{].*$", "", quote.strip())
    quote = re.sub(r"\n\w\.\s*(\w\.\s*)?\w+$", "", quote.strip(), flags=re.S)
    quote = re.sub(r"\n\w+[,\s]+\s*\w\.*\s*(\w\.\s*)?$", "", quote.strip())
    quote = re.sub(r"\n\w+$", "", quote.strip())
    # Remove duplicate space characters
    quote = re.sub(r"(\s){2,}", r"\1", quote.strip())
    # Normalize dash characters
    quote = re.sub(r"(^)[\-–]\s*", r"\1— ", quote, flags=re.M)
    quote = re.sub(r"\s*[\-–]\s+", " — ", quote)
    quote = re.sub(r"(\S)—", r"\1 —", quote)
    quote = re.sub(r"—(\S)", r"— \1", quote)
    return quote.strip()


# Make a corpus
for public in PUBLICS:
    if type(public) == int:
        param = "owner_id"  # get posts by ID
    else:
        param = "domain"  # get posts by nickname

    try:
        posts = tools.get_all("wall.get", 100, {param: public})
        logger.info(f"Got {posts['count']} posts from {public}")
        garbage_count = 0
        for post in posts["items"]:
            text = post["text"]
            if is_garbage(post):
                garbage_count += 1
                if text:
                    cur.execute("""INSERT INTO garbage (public, text)
                    VALUES (?, ?);""", (public, text))
            else:
                text = clear_post(text)
                if make_small and "\n" in text:
                    continue
                if text:
                    cur.execute("""INSERT INTO quotes (public, text)
                    VALUES (?, ?);""", (public, text))
        logger.info(f"Garbage: {garbage_count}")
    except Exception as e:
        logger.error(e)
        continue

db.commit()
logger.info("All done")
