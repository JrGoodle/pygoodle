"""array utilities

.. codeauthor:: JeanExtreme002

"""

def array_split(array: list, n = 10):

    """
    Split an array into multiple sub-arrays of equal or near-equal size.
    """

    new_array, length = [], len(array)
    ratio = (length // n) + (1 if length % n != 0 else 0)

    for row in range(n):
        new_array.append(array[row * ratio: ratio * (row + 1)])

    return new_array
