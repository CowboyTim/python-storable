result = [None, 'yy', [Ellipsis]]


def is_equal(a, b, message):

    comparable_a = [
        a[0],
        a[1],
        [Ellipsis]
    ]

    comparable_b = [
        b[0],
        b[1],
        [Ellipsis]
    ]

    if len(a) != len(b):
        raise AssertionError(message + ': Array length differs')

    non_recursive_a = [a[0], a[1]]
    non_recursive_b = [b[0], b[1]]
    if non_recursive_a != non_recursive_b:
        raise AssertionError(message + ': non-recursive part differs')

    if comparable_a != comparable_b:
        raise AssertionError(message + ': recursive part differs')
