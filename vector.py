import math

"""
The Vector class is used to represent a vector and incorporates methods used in vector math.
This is the backbone in all of the other code files, mainly used for things such as movement,
game setup, or otherwise.
"""
class Vector(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.threshold = 0.000001

    def __str__(self):
        """
        Returns a string representation of the vector.
        :return: string representation of the vector
        """
        return f'<{self.x}, {self.y}>'

    def __add__(self, other):
        """
        Returns a new Vector object with the addition of the two vectors.
        :param other: Vector
        :return: new Vector
        """
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """
        Returns a new Vector object with the subtraction of the two vectors.
        :param other: Vector
        :return: new Vector
        """
        return Vector(self.x - other.x, self.y - other.y)

    def __neg__(self):
        """
        Returns a new Vector object with the negation of the vector.
        :return: new Vector
        """
        return Vector(-self.x, -self.y)

    def __mul__(self, scalar):
        """
        Returns a new Vector object with the multiplication of the two vectors.
        :param scalar: value to multiply vector by
        :return: new Vector with resulting scalar multiplication
        """
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return self.__div__(scalar)

    def __div__(self, scalar):
        """
        Divides the vector by a scalar, unless said scalar is 0.
        :param scalar: value to divide vector by
        :return: new Vector with resulting scalar division
        """
        if scalar != 0:
            return Vector(int(self.x / float(scalar)), int(self.y / float(scalar)))
        return None

    def __eq__(self, other):
        """
        Returns true if two vectors are equal, otherwise returns false.
        :param other: Vector
        :return: true if two vectors are equal, false otherwise
        """
        if abs(self.x - other.x) < self.threshold and abs(self.y - other.y) < self.threshold: return True
        return False

    def magnitude_squared(self):
        """
        Returns the magnitude of the vector, squared.
        :return: squared magnitude of the vector
        """
        return math.pow(self.x, 2) + math.pow(self.y, 2)

    def magnitude(self):
        """
        Returns the magnitude of the vector by taking the root of the squared magnitude.
        :return: magnitude of the vector
        """
        return math.sqrt(self.magnitude_squared())

    def copy(self):
        """
        Returns a new Vector object with the copy of the vector.
        :return: new Vector
        """
        return Vector(self.x, self.y)

    def as_tuple(self):
        """ Returns the vector as a tuple. """
        return self.x, self.y

    def as_int(self):
        """ Returns the vector as an integer. """
        return int(self.x), int(self.y)
