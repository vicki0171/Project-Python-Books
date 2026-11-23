
import json
from pathlib import Path
from tabulate import tabulate
class BookCatalog:

    def __init__(self, filepath):
        self.path = Path(filepath)
        self.books = []
        self.skipped = 0

    def add_book(self, title, author, year):
        title = self._normalize_title(title)
        author = self._normalize_author(author)
        year = self._parse_year(year)

        if not title or not author:
            raise ValueError("Заглавието и авторът не могат да са празни.")

        for book in self.books:
            same_title = book["title"].lower() == title.lower()
            same_author = book["author"].lower() == author.lower()
            if same_title and same_author:
                raise ValueError("Тази книга вече е в каталога.")

        self.books.append({"title": title, "author": author, "year": year})
        self.save()

    def find_by_title(self, title, author=None):
        title = self._normalize_title(title)
        if not title:
            raise ValueError("Въведете заглавие.")

        author_name = None
        if author is not None:
            author_name = self._normalize_author(author).lower()
            if not author_name:
                raise ValueError("Въведете автор.")

        found = []
        for book in self.books:
            if book["title"].lower() != title.lower():
                continue
            if author_name is not None and book["author"].lower() != author_name:
                continue
            found.append(dict(book))
        return found

    def remove_book(self, title, author):
        title = self._normalize_title(title)
        author = self._normalize_author(author)
        if not title or not author:
            raise ValueError("Заглавието и авторът не могат да са празни.")

        for index, book in enumerate(self.books):
            same_title = book["title"].lower() == title.lower()
            same_author = book["author"].lower() == author.lower()
            if same_title and same_author:
                removed = self.books.pop(index)
                self.save()
                return removed

        raise ValueError("Няма книга с това заглавие и автор.")

    def load(self):
        if not self.path.is_file():
            return False

        try:
            content = self.path.read_text(encoding="utf-8")
            data = json.loads(content)
        except OSError as error:
            raise ValueError(f"Каталогът не може да се прочете: {error}") from error
        except json.JSONDecodeError as error:
            raise ValueError(
                "Файлът с книгите е повреден и не е зареден, за да не се загуби."
            ) from error

        if not isinstance(data, list):
            raise ValueError("Файлът с книгите няма очаквания формат.")

        loaded = []
        skipped = 0
        for item in data:
            if not isinstance(item, dict):
                skipped += 1
                continue
            try:
                title = self._normalize_title(item.get("title"))
                author = self._normalize_author(item.get("author"))
                year = self._parse_year(item.get("year"))
            except ValueError:
                skipped += 1
                continue
            if not title or not author:
                skipped += 1
                continue
            loaded.append({"title": title, "author": author, "year": year})

        self.books = loaded
        self.skipped = skipped
        return True

    def save(self):
        try:
            self.path.write_text(
                json.dumps(self.books, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as error:
            raise ValueError(f"Каталогът не може да се запише: {error}") from error

    def list_books(self):
        result = []
        for book in self.books:
            result.append(dict(book))
        return result

    def filter_by_author(self, author):
        query = self._normalize_author(author).lower()
        if not query:
            raise ValueError("Въведете автор за филтриране.")

        found = []
        for book in self.books:
            if query in book["author"].lower():
                found.append(dict(book))
        return found

    def search_by_title(self, query):
        needle = " ".join(str(query).strip().lower().split())
        if not needle:
            raise ValueError("Въведете текст за търсене.")

        found = []
        for book in self.books:
            if needle in book["title"].lower():
                found.append(dict(book))
        return found

    def sort_by_year(self, newest_first=False):
        ordered = self.list_books()
        ordered.sort(key=lambda book: book["year"], reverse=newest_first)
        return ordered

    def format_table(self, books):
        if not books:
            return "Няма намерени книги."

        rows = []
        for index, book in enumerate(books, start=1):
            rows.append([index, book["title"], book["author"], book["year"]])

        return tabulate(
            rows,
            headers=["№", "Заглавие", "Автор", "Година"],
            tablefmt="simple",
        )

    def _clean_spaces(self, value):
        if value is None:
            return ""
        return " ".join(str(value).strip().split())

    def _normalize_title(self, value):
        cleaned = self._clean_spaces(value)
        if not cleaned:
            return ""
        if cleaned.isupper() or cleaned.islower():
            return cleaned[:1].upper() + cleaned[1:].lower()
        return cleaned[:1].upper() + cleaned[1:]

    def _normalize_author(self, value):
        words = []
        for word in self._clean_spaces(value).split(" "):
            if not word:
                continue
            words.append(word[:1].upper() + word[1:].lower())
        return " ".join(words)

    def _parse_year(self, year):
        if isinstance(year, bool):
            raise ValueError("Годината трябва да е цяло число.")

        if isinstance(year, str):
            cleaned = year.strip()
            if not cleaned.isdigit():
                raise ValueError("Годината трябва да е цяло положително число.")
            year = int(cleaned)
        elif not isinstance(year, int):
            raise ValueError("Годината трябва да е цяло число.")

        if year < 1 or year > 2100:
            raise ValueError("Годината трябва да е между 1 и 2100.")

        return year