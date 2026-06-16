import argparse
import asyncio
import random

from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.models.database import Categories, CategoryTranslations


ICON_POOL: list[str] = [
    "https://img.icons8.com/fluency/96/book.png",
    "https://img.icons8.com/fluency/96/learning.png",
    "https://img.icons8.com/fluency/96/classroom.png",
    "https://img.icons8.com/fluency/96/laptop.png",
    "https://img.icons8.com/fluency/96/idea.png",
]


def _build_category_names(index: int) -> tuple[str, str]:
    vi_name = f"Danh muc {index:04d}"
    en_name = f"Category {index:04d}"
    return vi_name, en_name


def _build_descriptions(index: int) -> tuple[str, str]:
    vi_desc = f"Mo ta danh muc so {index:04d}."
    en_desc = f"Description for category {index:04d}."
    return vi_desc, en_desc


async def seed(total: int, reset: bool) -> None:
    random.seed(2026)

    async with AsyncSessionLocal() as db:
        if reset:
            await db.execute(text("TRUNCATE TABLE public.category_translations CASCADE"))
            await db.execute(text("TRUNCATE TABLE public.categories CASCADE"))

        categories: list[Categories] = []
        for index in range(1, total + 1):
            categories.append(
                Categories(
                    icon=random.choice(ICON_POOL),
                )
            )

        db.add_all(categories)
        await db.flush()

        translations: list[CategoryTranslations] = []
        for index, category in enumerate(categories, start=1):
            vi_name, en_name = _build_category_names(index)
            vi_desc, en_desc = _build_descriptions(index)
            translations.append(
                CategoryTranslations(
                    category_id=category.id,
                    lang="vi",
                    name=vi_name,
                    description=vi_desc,
                    is_auto_translated=False,
                )
            )
            translations.append(
                CategoryTranslations(
                    category_id=category.id,
                    lang="en",
                    name=en_name,
                    description=en_desc,
                    is_auto_translated=True,
                )
            )

        db.add_all(translations)
        await db.flush()

        await db.commit()

    print(f"Seeded {total} categories.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed fake categories.")
    parser.add_argument("--total", type=int, default=1000, help="Number of categories to create.")
    parser.add_argument("--reset", action="store_true", help="Truncate categories before seeding.")
    args = parser.parse_args()

    asyncio.run(seed(args.total, args.reset))


if __name__ == "__main__":
    main()
