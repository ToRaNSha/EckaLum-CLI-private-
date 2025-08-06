import math


class ndarray(list):
    def __mul__(self, other):
        return ndarray([x * other for x in self])

    __rmul__ = __mul__

    def __truediv__(self, other):
        return ndarray([x / other for x in self])

    def argmax(self):
        return max(range(len(self)), key=self.__getitem__)

    @property
    def shape(self):
        return (len(self),)

    def tolist(self):
        return list(self)


def array(seq):
    return ndarray(seq)


def log1p(arr):
    return ndarray([math.log1p(x) for x in arr])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


class LinalgModule:
    @staticmethod
    def norm(a):
        return math.sqrt(sum(x * x for x in a))


linalg = LinalgModule()


class TestingModule:
    @staticmethod
    def assert_allclose(a, b, rtol=1e-7, atol=0.0):
        if len(a) != len(b):
            raise AssertionError("Array lengths differ")
        for x, y in zip(a, b):
            if abs(x - y) > atol + rtol * abs(y):
                raise AssertionError(f"{x} !~ {y}")


testing = TestingModule()
