from src.models import VetCreate, VetLocation, VetContact
from src import db


class TestGetDb:

    def test_can_get(self) -> None:
        # Get twice to test caching
        db.get_db()
        db.get_db()


class TestCreateVet:

    def test_can_create(self) -> None:
        db.create_vet(
            VetCreate(
                name="test",
                location=VetLocation(
                    address="test address",
                    lat=1,
                    lon=1,
                ),
                contact=VetContact(
                    tel="03012345678",
                    email="test@example.com",
                    url="https://example.com"
                )
            )
        )


class TestGetVets:

    def setup_method(self) -> None:
        db.get_vets_collection().drop()

    def test_can_get(self) -> None:
        db.create_vet(
            VetCreate(
                name="test",
                location=VetLocation(
                    address="test address",
                    lat=1,
                    lon=1,
                ),
                contact=VetContact(
                    tel="03012345678",
                    email="test@example.com",
                    url="https://example.com"
                )
            )
        )

        vets = db.get_vets()

        assert len(vets) == 1

        vet = vets[0]
        assert len(vet.id) == 24
        assert vet.name == "test"
        assert vet.location.address == "test address"
        assert vet.contact.tel == "03012345678"
