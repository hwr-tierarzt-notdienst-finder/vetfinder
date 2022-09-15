from src import db


class TestGetDb:

    def test_can_get(self) -> None:
        # Get twice to test caching
        db.get_db()
        db.get_db()
