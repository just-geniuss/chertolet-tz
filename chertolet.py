"""Учебная модель «Чертолёт Грешник-3000» по SPEC.md версии 0.2.

Требуется Python 3.10 или новее. Внешние зависимости отсутствуют.
Скорость вычисляется из уровня грехов и состояния полёта; грехи
при движении не расходуются. Все публичные свойства доступны только для чтения.
"""

__all__ = ["Chertolet", "ChertoletError", "FlightStateError"]


class ChertoletError(RuntimeError):
    """Базовая ошибка состояния Чертолёта."""


class FlightStateError(ChertoletError):
    """Команда недопустима в текущем состоянии полёта."""


class Chertolet:
    """Одноместный аппарат с базовой скоростью 30 км/ч и прибавкой за грехи."""

    def __init__(self, name: str = "Грешник-3000", sin_level: int = 0) -> None:
        # Проверяем имя раньше уровня; подклассы встроенных типов запрещены.
        if type(name) is not str:
            raise TypeError("name must be a string")
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("name must not be blank")
        if type(sin_level) is not int:
            raise TypeError("sin_level must be an integer")
        if not 0 <= sin_level <= 100:
            raise ValueError("sin_level must be between 0 and 100")

        self._name = normalized_name
        self._sin_level = sin_level
        self._position_km = 0.0
        self._is_flying = False

    @property
    def name(self) -> str:
        """Имя без пробелов по краям."""
        return self._name

    @property
    def sin_level(self) -> int:
        """Текущий уровень грехов: от 0 до 100 включительно."""
        return self._sin_level

    @property
    def boost_kmh(self) -> float:
        """Прибавка к скорости, сохраняющаяся и на земле."""
        return 2.0 * self._sin_level

    @property
    def speed_kmh(self) -> float:
        """Скорость в км/ч: на земле 0, в воздухе от 30 до 230."""
        return 30.0 + self.boost_kmh if self._is_flying else 0.0

    @property
    def position_km(self) -> float:
        """Суммарный путь в километрах за все рейсы."""
        return self._position_km

    @property
    def is_flying(self) -> bool:
        """Находится ли аппарат в полёте."""
        return self._is_flying

    def take_off(self) -> None:
        """Взлететь, сохранив путь и текущий уровень грехов."""
        if self._is_flying:
            raise FlightStateError("already flying")
        self._is_flying = True

    def land(self) -> None:
        """Приземлиться, сохранив путь, грехи и прибавку к скорости."""
        if not self._is_flying:
            raise FlightStateError("already on ground")
        self._is_flying = False

    def move(self, distance_km: float) -> float:
        """Пролететь участок и вернуть его длительность в часах.

        Дистанция — строго встроенный int/float в диапазоне (0, 1_000_000].
        Ошибки аргумента имеют приоритет над запретом движения на земле.
        """
        if type(distance_km) not in (int, float):
            raise TypeError("distance_km must be a number")
        # Сравнение отклоняет NaN и ±inf, а также огромные int без их
        # преобразования в float, которое могло бы вызвать OverflowError.
        if not 0 < distance_km <= 1_000_000:
            raise ValueError(
                "distance_km must be between 0 (exclusive) and 1000000"
            )
        if not self._is_flying:
            raise FlightStateError("cannot move on ground")

        duration_hours = distance_km / self.speed_kmh
        self._position_km += distance_km
        return duration_hours

    def add_sins(self, amount: int) -> None:
        """Добавить от 1 до 100 грехов, ограничив итоговый уровень числом 100."""
        if type(amount) is not int:
            raise TypeError("amount must be an integer")
        if not 1 <= amount <= 100:
            raise ValueError("amount must be between 1 and 100")
        self._sin_level = min(100, self._sin_level + amount)

    def absolve_sins(self) -> None:
        """Обнулить грехи без изменения пути и состояния полёта."""
        self._sin_level = 0

    def get_status(self) -> dict:
        """Вернуть новый независимый снимок ровно с шестью полями."""
        return {
            "name": self.name,
            "sin_level": self.sin_level,
            "boost_kmh": self.boost_kmh,
            "speed_kmh": self.speed_kmh,
            "position_km": self.position_km,
            "is_flying": self.is_flying,
        }
