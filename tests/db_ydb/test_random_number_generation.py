from db.db_ydb.predictions import get_random_number


class TestRandomNumberGeneration:

    @classmethod
    def setup_class(cls):
        cls.data1 = [0, 1, 2, 3, 4, 5, 6, 100, 778, 838, 2207]
        cls.data2 = [5, 8, 10, 15, 16, 17, 100, 101, 102, 103]

        cls.counter = 1_000_000

    def assert_random_number_generation(self, range_max, data, expected_values):
        results = [get_random_number(range_max, data) for _ in range(self.counter)]

        for num in results:
            assert num in expected_values

        for num in expected_values:
            assert num in results

    def test_range_max_is_0(self):
        assert get_random_number(0, self.data1) is None
        assert get_random_number(0, self.data2) == 0

    def test_range_max_is_1(self):
        assert get_random_number(1, self.data1) is None
        self.assert_random_number_generation(1, self.data2, (0, 1))

    def test_range_max_is_5(self):
        self.assert_random_number_generation(5, self.data2, (0, 1, 2, 3, 4))

    def test_range_max_is_7(self):
        assert all(get_random_number(7, self.data1) == 7 for _ in range(self.counter))
        self.assert_random_number_generation(7, self.data2, (0, 1, 2, 3, 4, 6, 7))

    def test_range_max_is_10(self):
        self.assert_random_number_generation(10, self.data1, (7, 8, 9, 10))
        self.assert_random_number_generation(10, self.data2, (0, 1, 2, 3, 4, 6, 7, 9))

    def test_range_max_is_105(self):
        self.assert_random_number_generation(105, self.data1, set(range(106)) - set(self.data1))
        self.assert_random_number_generation(105, self.data2, set(range(106)) - set(self.data2))
