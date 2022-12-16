from unittest import TestCase

from exceptions import RoomNameAlreadyExistsError
from stores.rooms_store import RoomStore


class TestRoomStore(TestCase):

    def setUp(self) -> None:
        super().setUp()

        self.room_store = RoomStore(False)

    def test_init_count_in_store(self):
        self.assertEqual(1, len(self.room_store.rooms))

    def test_add_room_to_store(self):
        self.room_store.add_room('super_chat', 'superuser')

        result = [r.name for r in self.room_store.rooms]
        result_owners = [r.owner for r in self.room_store.rooms]

        self.assertIn('super_chat', result)
        self.assertIn('superuser', result_owners)
        self.assertEqual(2, len(self.room_store.rooms))

    def test_get_rooms_by_name(self):
        result1 = self.room_store.get_rooms_by_name('public')
        self.assertEqual(1, len(result1))

        self.room_store.add_room('awesome_room', 'sudo')
        result2 = self.room_store.get_rooms_by_name('awesome_room')
        self.assertEqual(1, len(result2))
        self.assertEqual(2, len(self.room_store.rooms))

        with self.assertRaises(RoomNameAlreadyExistsError):
            self.room_store.add_room('awesome_room', 'user')

    def test_get_room_by_id(self):
        result1 = self.room_store.get_rooms_by_name('public')

        room_id = result1[0].id_
        result1_ = self.room_store.get_room_by_id(room_id)
        self.assertEqual('public', result1_.name)    # type: ignore

        result2_ = self.room_store.get_room_by_id('hasdf')

        self.assertIsNone(result2_)
