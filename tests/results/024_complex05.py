result = [
    None,
    6,
    ['a', 'b', 'c', {'uu': 5.6, 'ii': {Ellipsis}}],
    {'uu': 5.6, 'ii': {Ellipsis}},
    {'uu': 5.6, 'ii': {Ellipsis}},
    ['a', 'b', 'c', {'uu': 5.6, 'ii': {Ellipsis}}],
    None,
    6
]



def is_equal(a, b, message):

    comparable_a = [
        a[0],
        a[1],
        [a[2][0], a[2][1], a[2][2], {'uu': a[2][3]['uu'],
                                     'ii': [Ellipsis]}],
        {'uu': a[3]['uu'], 'ii': [Ellipsis]},
        {'uu': a[4]['uu'], 'ii': [Ellipsis]},
        [a[5][0], a[5][1], a[5][2], {'uu': a[5][3]['uu'],
                                     'ii': [Ellipsis]}],
        a[6],
        a[7],
    ]

    comparable_b = [
        b[0],
        b[1],
        [b[2][0], b[2][1], b[2][2], {'uu': b[2][3]['uu'],
                                     'ii': [Ellipsis]}],
        {'uu': b[3]['uu'], 'ii': [Ellipsis]},
        {'uu': b[4]['uu'], 'ii': [Ellipsis]},
        [b[5][0], b[5][1], b[5][2], {'uu': b[5][3]['uu'],
                                     'ii': [Ellipsis]}],
        b[6],
        b[7],
    ]

    if len(a) != len(b):
        raise AssertionError(message + ': Array length differs')

    non_recursive_a = [a[0], a[1], a[-2], a[-1]]
    non_recursive_b = [b[0], b[1], b[-2], b[-1]]
    if non_recursive_a != non_recursive_b:
        raise AssertionError(message + ': non-recursive part differs')

    if comparable_a != comparable_b:
        raise AssertionError(message + ': recursive part differs')
