"""Приёмочные тесты. Каждый метод соответствует одному ID в TEST_CASES.md."""
import math
import unittest
from decimal import Decimal
from fractions import Fraction
from enum import IntEnum
from chertolet import Chertolet, ChertoletError, FlightStateError
from tests.pilot import Pilot

class IntChild(int):
    pass


class FloatChild(float):
    pass


class StrChild(str):
    pass


class Level(IntEnum):
    ONE = 1
BAD_NUMBERS = [Decimal("1"), Fraction(1, 2), IntChild(1), FloatChild(1), Level.ONE]

class ChertoletTests(unittest.TestCase):
    def assert_close(self, actual, expected):
        """Сравнение времени/пути: rel_tol=1e-6, abs_tol=1e-12."""
        if isinstance(expected, (list, tuple)):
            self.assertEqual(len(actual), len(expected))
            for value, target in zip(actual, expected):
                self.assert_close(value, target)
        else:
            self.assertTrue(math.isclose(actual, expected, rel_tol=1e-06, abs_tol=1e-12), msg=f'{actual!r} != {expected!r}')

    def test_TC_M_001_defaults(self):
        """TC-M-001 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet()
        self.assertEqual(c.get_status(), dict(name='Грешник-3000', sin_level=0, boost_kmh=0.0, speed_kmh=0.0, position_km=0.0, is_flying=False))
        expected = dict(name=str, sin_level=int, boost_kmh=float, speed_kmh=float, position_km=float, is_flying=bool)
        self.assertEqual({key: type(value) for key, value in c.get_status().items()}, expected)

    def test_TC_M_002_custom_init(self):
        """TC-M-002 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet('  Люцифер-экспресс  ', 50)
        self.assertEqual(c.name, 'Люцифер-экспресс')
        self.assertEqual(c.sin_level, 50)
        self.assertEqual(c.boost_kmh, 100.0)
        self.assertEqual(c.speed_kmh, 0.0)

    def test_TC_M_003_bad_name(self):
        """TC-M-003 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for name, error, message in [('', ValueError, 'name must not be blank'), (' \t\n', ValueError, 'name must not be blank'), (None, TypeError, 'name must be a string'), (12, TypeError, 'name must be a string'), (True, TypeError, 'name must be a string'), (StrChild('Имя'), TypeError, 'name must be a string')]:
            with self.subTest(name=name, error=error, message=message):
                with self.assertRaises(error) as exc:
                    Chertolet(name)
                self.assertEqual(str(exc.exception), message)

    def test_TC_M_004_sin_bounds(self):
        """TC-M-004 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level in [0, 1, 50, 99, 100]:
            with self.subTest(level=level):
                c = Chertolet(sin_level=level)
                self.assertEqual(c.sin_level, level)
                self.assertIs(type(c.sin_level), int)

    def test_TC_M_005_bad_sin_range(self):
        """TC-M-005 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level in [-1, 101, 10 ** 1000]:
            with self.subTest(level=level):
                with self.assertRaisesRegex(ValueError, '^sin_level must be between 0 and 100$'):
                    Chertolet(sin_level=level)

    def test_TC_M_006_bad_sin_type(self):
        """TC-M-006 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level in [0.0, 50.5, '50', None, True, False, float('nan'), float('inf')] + BAD_NUMBERS:
            with self.subTest(level=level):
                with self.assertRaisesRegex(TypeError, '^sin_level must be an integer$'):
                    Chertolet(sin_level=level)

    def test_TC_M_007_read_only(self):
        """TC-M-007 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for attr, value in [('name', 'X'), ('sin_level', 1), ('boost_kmh', 2.0), ('speed_kmh', 32.0), ('position_km', 1.0), ('is_flying', True)]:
            with self.subTest(attr=attr, value=value):
                c = Chertolet()
                before = c.get_status()
                with self.assertRaises(AttributeError):
                    setattr(c, attr, value)
                self.assertEqual(c.get_status(), before)

    def test_TC_M_008_take_off_speed(self):
        """TC-M-008 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level, speed in [(0, 30.0), (1, 32.0), (50, 130.0), (100, 230.0)]:
            with self.subTest(level=level, speed=speed):
                c = Chertolet(sin_level=level)
                self.assertIs(c.take_off(), None)
                self.assertIs(c.is_flying, True)
                self.assertEqual(c.speed_kmh, speed)
                self.assertIs(type(c.speed_kmh), float)
                self.assertEqual(c.position_km, 0.0)
                self.assertEqual(c.sin_level, level)

    def test_TC_M_009_double_take_off(self):
        """TC-M-009 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=10)
        c.take_off()
        before = c.get_status()
        with self.assertRaisesRegex(FlightStateError, '^already flying$'):
            c.take_off()
        self.assertEqual(c.get_status(), before)

    def test_TC_M_010_land(self):
        """TC-M-010 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level, added, expected in [(50, 0, 130.0), (10, 40, 130.0)]:
            with self.subTest(level=level, added=added, expected=expected):
                c = Chertolet(sin_level=level)
                c.take_off()
                c.move(13)
                self.assertIs(c.land(), None)
                self.assertTrue(c.speed_kmh == 0.0 and c.is_flying is False)
                self.assertEqual(c.position_km, 13.0)
                self.assertTrue(c.sin_level == level and c.boost_kmh == 2.0 * level)
                if added:
                    c.add_sins(added)
                    self.assertEqual(c.speed_kmh, 0.0)
                c.take_off()
                self.assertEqual(c.speed_kmh, expected)
                self.assertEqual(c.sin_level, level + added)
                self.assert_close(c.move(13), 0.1)
                self.assertEqual(c.position_km, 26.0)

    def test_TC_M_011_land_on_ground(self):
        """TC-M-011 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet()
        before = c.get_status()
        with self.assertRaisesRegex(FlightStateError, '^already on ground$'):
            c.land()
        self.assertEqual(c.get_status(), before)

    def test_TC_M_012_move(self):
        """TC-M-012 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for distance, level, time in [(30, 0, 1.0), (13.0, 50, 0.1), (0.5, 100, 0.5 / 230), (1000000, 0, 1000000 / 30)]:
            with self.subTest(distance=distance, level=level, time=time):
                c = Chertolet(sin_level=level)
                c.take_off()
                duration = c.move(distance)
                self.assertIs(type(duration), float)
                self.assert_close(duration, time)
                self.assert_close(c.position_km, distance)
                self.assertIs(type(c.position_km), float)
                self.assertEqual(c.sin_level, level)
                self.assertIs(c.is_flying, True)

    def test_TC_M_013_ground_move(self):
        """TC-M-013 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=100)
        before = c.get_status()
        with self.assertRaisesRegex(FlightStateError, '^cannot move on ground$'):
            c.move(1)
        self.assertEqual(c.get_status(), before)

    def test_TC_M_014_bad_distance_range(self):
        """TC-M-014 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                for distance in [0, -1, 1000001, 10 ** 1000, float('inf'), float('-inf'), float('nan')]:
                    with self.subTest(distance=distance):
                        c = Chertolet()
                        if flying:
                            c.take_off()
                            c.move(1)
                        before = c.get_status()
                        with self.assertRaises(ValueError) as exc:
                            c.move(distance)
                        self.assertEqual(str(exc.exception), 'distance_km must be between 0 (exclusive) and 1000000')
                        self.assertEqual(c.get_status(), before)

    def test_TC_M_015_bad_distance_type(self):
        """TC-M-015 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                for distance in ['1', None, True, False, [], complex(1, 0)] + BAD_NUMBERS:
                    with self.subTest(distance=distance):
                        c = Chertolet()
                        if flying:
                            c.take_off()
                            c.move(1)
                        before = c.get_status()
                        with self.assertRaisesRegex(TypeError, '^distance_km must be a number$'):
                            c.move(distance)
                        self.assertEqual(c.get_status(), before)

    def test_TC_M_016_add_sins(self):
        """TC-M-016 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                c = Chertolet(sin_level=10)
                if flying:
                    c.take_off()
                    c.move(5)
                self.assertIs(c.add_sins(1), None)
                self.assertEqual(c.sin_level, 11)
                self.assertEqual(c.boost_kmh, 22.0)
                self.assertEqual(c.speed_kmh, 52.0 if flying else 0.0)
                self.assertEqual(c.position_km, 5.0 if flying else 0.0)
                self.assertIs(c.is_flying, flying)

    def test_TC_M_017_sin_cap(self):
        """TC-M-017 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for level, amount in [(0, 100), (99, 1), (90, 20), (100, 100)]:
            with self.subTest(level=level, amount=amount):
                c = Chertolet(sin_level=level)
                c.take_off()
                c.add_sins(amount)
                self.assertEqual(c.sin_level, 100)
                self.assertEqual(c.speed_kmh, 230.0)

    def test_TC_M_018_bad_amount_range(self):
        """TC-M-018 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                for amount in [0, -1, 101, 10 ** 1000]:
                    with self.subTest(amount=amount):
                        c = Chertolet(sin_level=10)
                        if flying:
                            c.take_off()
                        before = c.get_status()
                        with self.assertRaisesRegex(ValueError, '^amount must be between 1 and 100$'):
                            c.add_sins(amount)
                        self.assertEqual(c.get_status(), before)

    def test_TC_M_019_bad_amount_type(self):
        """TC-M-019 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                for amount in [1.0, '1', None, True, False, float('nan'), float('inf')] + BAD_NUMBERS:
                    with self.subTest(amount=amount):
                        c = Chertolet(sin_level=10)
                        if flying:
                            c.take_off()
                        before = c.get_status()
                        with self.assertRaisesRegex(TypeError, '^amount must be an integer$'):
                            c.add_sins(amount)
                        self.assertEqual(c.get_status(), before)

    def test_TC_M_020_absolution(self):
        """TC-M-020 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        for flying in [False, True]:
            with self.subTest(flying=flying):
                for level in [0, 1, 100]:
                    with self.subTest(level=level):
                        c = Chertolet(sin_level=level)
                        if flying:
                            c.take_off()
                            c.move(5)
                        self.assertIs(c.absolve_sins(), None)
                        self.assertEqual(c.sin_level, 0)
                        self.assertEqual(c.boost_kmh, 0.0)
                        self.assertEqual(c.speed_kmh, 30.0 if flying else 0.0)
                        self.assertEqual(c.position_km, 5.0 if flying else 0.0)
                        self.assertIs(c.is_flying, flying)
                        self.assertEqual(c.name, 'Грешник-3000')
                        before = c.get_status()
                        c.absolve_sins()
                        self.assertEqual(c.get_status(), before)
                        c.add_sins(1)
                        self.assertTrue(c.sin_level == 1 and c.boost_kmh == 2.0)
                        self.assertEqual(c.speed_kmh, 32.0 if flying else 0.0)
                        self.assertEqual(c.position_km, before['position_km'])
                        self.assertIs(c.is_flying, flying)

    def test_TC_M_021_snapshot(self):
        """TC-M-021 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=50)
        old = c.get_status()
        c.take_off()
        c.move(13)
        current = c.get_status()
        self.assertTrue(old['position_km'] == 0.0 and old['is_flying'] is False)
        self.assertEqual(current, dict(name='Грешник-3000', sin_level=50, boost_kmh=100.0, speed_kmh=130.0, position_km=13.0, is_flying=True))
        current.clear()
        self.assertEqual(c.get_status()['position_km'], 13.0)
        self.assertEqual(c.get_status()['sin_level'], 50)

    def test_TC_M_022_exception_hierarchy(self):
        """TC-M-022 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        self.assertTrue(issubclass(ChertoletError, RuntimeError))
        self.assertTrue(issubclass(FlightStateError, ChertoletError))
        with self.assertRaises(ChertoletError):
            Chertolet().move(1)

    def test_TC_M_023_independent_instances(self):
        """TC-M-023 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        a, b = (Chertolet(), Chertolet())
        before = b.get_status()
        a.add_sins(50)
        a.take_off()
        a.move(13)
        self.assertEqual(b.get_status(), before)

    def test_TC_M_024_constructor_validation_order(self):
        """TC-M-024 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        with self.assertRaisesRegex(TypeError, '^name must be a string$'):
            Chertolet(None, -1)
        with self.assertRaisesRegex(ValueError, '^name must not be blank$'):
            Chertolet(' ', True)

    def test_TC_S_001_sinner_route(self):
        """TC-S-001 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=50)
        pilot = Pilot(c)
        pilot.take_off()
        times = [pilot.move(13), pilot.move(26)]
        pilot.land()
        self.assert_close(times, [0.1, 0.2])
        self.assertEqual(c.position_km, 39.0)
        self.assertEqual(c.sin_level, 50)
        self.assertEqual(c.speed_kmh, 0.0)
        self.assertIs(c.is_flying, False)

    def test_TC_S_002_absolution_in_air(self):
        """TC-S-002 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=100)
        pilot = Pilot(c)
        pilot.take_off()
        first = pilot.move(23)
        pilot.absolve_sins()
        self.assertIs(c.is_flying, True)
        self.assertTrue(c.speed_kmh == 30.0 and c.boost_kmh == 0.0)
        second = pilot.move(3)
        self.assert_close((first, second), (0.1, 0.1))
        self.assertTrue(c.position_km == 26.0 and c.sin_level == 0)

    def test_TC_S_003_sin_again(self):
        """TC-S-003 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet()
        pilot = Pilot(c)
        pilot.take_off()
        times = [pilot.move(3)]
        pilot.add_sins(50)
        times.append(pilot.move(13))
        pilot.add_sins(80)
        times.append(pilot.move(23))
        self.assert_close(times, [0.1, 0.1, 0.1])
        self.assertEqual(c.position_km, 39.0)
        self.assertTrue(c.sin_level == 100 and c.speed_kmh == 230.0)

    def test_TC_S_004_error_and_resume(self):
        """TC-S-004 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        # Given / Arrange: настоящий аппарат и пилот.
        c = Chertolet(sin_level=10)
        pilot = Pilot(c)
        # When: первый рейс.
        pilot.take_off()
        self.assert_close(pilot.move(5), 0.1)
        pilot.land()
        # Then: посадка сохраняет грехи и путь.
        self.assertEqual(c.position_km, 5.0)
        self.assertEqual(c.sin_level, 10)
        self.assertEqual(c.boost_kmh, 20.0)
        self.assertEqual(c.speed_kmh, 0.0)
        self.assertIs(c.is_flying, False)
        before = c.get_status()
        # When / Then: каждая ошибочная команда сохраняет снимок.
        for action, error in [(lambda: pilot.move(1), FlightStateError), (lambda: pilot.move(0), ValueError), (lambda: pilot.add_sins(True), TypeError)]:
            with self.assertRaises(error):
                action()
            self.assertEqual(c.get_status(), before)
        # When: отпущение на земле.
        pilot.absolve_sins()
        # Then: обнулены грехи и прибавка, путь сохранён.
        self.assertEqual(c.sin_level, 0)
        self.assertEqual(c.boost_kmh, 0.0)
        self.assertEqual(c.speed_kmh, 0.0)
        self.assertEqual(c.position_km, 5.0)
        self.assertIs(c.is_flying, False)
        # When / Then: второй рейс со скоростью 30.
        pilot.take_off()
        self.assertEqual(c.speed_kmh, 30.0)
        self.assert_close(pilot.move(3), 0.1)
        pilot.land()
        self.assertEqual(c.position_km, 8.0)
        self.assertTrue(c.sin_level == 0 and c.is_flying is False)

    def test_TC_S_005_ground_absolution(self):
        """TC-S-005 — Arrange: новый аппарат; Act: команды; Assert: контракт и снимок."""
        c = Chertolet(sin_level=100)
        pilot = Pilot(c)
        pilot.take_off()
        self.assert_close(pilot.move(23), 0.1)
        pilot.land()
        # Then: первый рейс завершён, прибавка сохранена.
        self.assertEqual(c.position_km, 23.0)
        self.assertEqual(c.sin_level, 100)
        self.assertEqual(c.boost_kmh, 200.0)
        self.assertEqual(c.speed_kmh, 0.0)
        self.assertIs(c.is_flying, False)
        # When: отпущение между рейсами.
        pilot.absolve_sins()
        # Then: аппарат на земле с прежним путём.
        self.assertEqual(c.sin_level, 0)
        self.assertEqual(c.position_km, 23.0)
        self.assertIs(c.is_flying, False)
        self.assertTrue(c.speed_kmh == 0.0 and c.boost_kmh == 0.0)
        # When / Then: повторный взлёт без старой прибавки.
        pilot.take_off()
        self.assertEqual(c.speed_kmh, 30.0)
        self.assert_close(pilot.move(3), 0.1)
        self.assertTrue(c.position_km == 26.0 and c.sin_level == 0)
        self.assertIs(c.is_flying, True)
