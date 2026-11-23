
import sys
from pathlib import Path

from models import BookCatalog

DATA_FILE = Path(__file__).with_name("books.json")


def configure_console():
    for stream in (sys.stdout, sys.stdin):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (AttributeError, OSError, ValueError):
            continue


def load_examples(catalog):
    examples = [
        ("1984", "Джордж Оруел", 1949),
        ("Майстора и Маргарита", "Михаил Булгаков", 1967),
        ("Под игото", "Иван Вазов", 1894),
        ("Хари Потър и Философският камък", "Дж. К. Роулинг", 1997),
    ]
    for title, author, year in examples:
        catalog.add_book(title, author, year)


def print_menu():
    print()
    print("=== Каталог на книги ===")
    print("1. Добави книга")
    print("2. Покажи всички")
    print("3. Филтрирай по автор")
    print("4. Сортирай по година")
    print("5. Търси по заглавие")
    print("6. Премахни книга")
    print("0. Изход")


def show_books(catalog, books):
    print()
    print(catalog.format_table(books))


def add_book(catalog):
    title = input("Заглавие: ")
    author = input("Автор: ")
    year = input("Година: ")
    try:
        catalog.add_book(title, author, year)
    except ValueError as error:
        print(error)
        return
    print("Книгата е добавена и записана.")


def filter_books(catalog):
    author = input("Автор (или част от името): ")
    try:
        found = catalog.filter_by_author(author)
    except ValueError as error:
        print(error)
        return
    show_books(catalog, found)


def sort_books(catalog):
    print("1. От най-старата към най-новата")
    print("2. От най-новата към най-старата")
    direction = input("Посока: ").strip()

    if direction == "1":
        ordered = catalog.sort_by_year(newest_first=False)
    elif direction == "2":
        ordered = catalog.sort_by_year(newest_first=True)
    else:
        print("Невалидна посока. Въведете 1 или 2.")
        return

    show_books(catalog, ordered)


def remove_book(catalog):
    if not catalog.books:
        print("Каталогът е празен.")
        return

    title = input("Заглавие на книгата за премахване: ")
    try:
        found = catalog.find_by_title(title)
    except ValueError as error:
        print(error)
        return

    if not found:
        print("Няма книга с това заглавие.")
        return

    if len(found) == 1:
        chosen = found[0]
    else:
        print("Има повече от една книга с това заглавие:")
        show_books(catalog, found)
        author = input("Автор на книгата, която да се премахне: ")
        try:
            matches = catalog.find_by_title(title, author)
        except ValueError as error:
            print(error)
            return
        if len(matches) != 1:
            print("Няма книга с това заглавие и автор.")
            return
        chosen = matches[0]

    answer = input(
        f"Да се премахне ли „{chosen['title']}“ от {chosen['author']}? (д/н): "
    ).strip().lower()
    if answer != "д":
        print("Премахването е отказано.")
        return

    try:
        removed = catalog.remove_book(chosen["title"], chosen["author"])
    except ValueError as error:
        print(error)
        return
    print(f"Премахната е „{removed['title']}“ и промяната е записана.")


def search_books(catalog):
    query = input("Текст от заглавието: ")
    try:
        found = catalog.search_by_title(query)
    except ValueError as error:
        print(error)
        return
    show_books(catalog, found)


def main():
    configure_console()
    catalog = BookCatalog(DATA_FILE)

    try:
        file_exists = catalog.load()
    except ValueError as error:
        print(error)
        return

    if file_exists:
        print(f"Заредени са {len(catalog.books)} книги от {DATA_FILE.name}.")
        if catalog.skipped:
            print(f"Пропуснати са {catalog.skipped} невалидни записа.")
    else:
        load_examples(catalog)
        print(f"Създаден е нов каталог във файл {DATA_FILE.name}.")

    while True:
        print_menu()
        choice = input("Избор: ").strip()

        if choice == "1":
            add_book(catalog)
        elif choice == "2":
            show_books(catalog, catalog.list_books())
        elif choice == "3":
            filter_books(catalog)
        elif choice == "4":
            sort_books(catalog)
        elif choice == "5":
            search_books(catalog)
        elif choice == "6":
            remove_book(catalog)
        elif choice == "0":
            print("Довиждане.")
            break
        else:
            print("Невалиден избор. Въведете число от менюто.")


if __name__ == "__main__":
    main()