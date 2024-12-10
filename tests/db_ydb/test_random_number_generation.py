from db.db_ydb.predictions import get_random_number


class TestRandomNumberGeneration:

    @classmethod
    def setup_class(cls):
        cls.data = [
            [0, 1, 2, 3, 4, 5, 6, 318, 778, 838, 2207],
            [5, 8, 10, 15, 16, 17, 100, 101, 102, 105]
        ]
        cls.counter = 1000

    def test_range_max_is_0(self):
        assert get_random_number(0, self.data[0]) is None
        assert get_random_number(0, self.data[1]) == 0

    def test_range_max_is_1(self):
        assert get_random_number(1, self.data[0]) is None
        _data = []
        for i in range(self.counter):
            _data.append(get_random_number(1, self.data[1]))
        assert (0 in _data and 1 in _data)

    def test_range_max_is_5(self):
        assert get_random_number(5, self.data[0]) is None

        _data = []
        for i in range(self.counter):
            _data.append(get_random_number(5, self.data[1]))

        assert all([num in (0, 1, 2, 3, 4) for num in _data])
        assert all([num in _data for num in (0, 1, 2, 3, 4)])
