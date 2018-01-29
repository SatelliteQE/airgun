from fauxfactory import gen_string


def valid_data_list():
    """Generates a list of valid input values."""
    return [
        gen_string('alphanumeric', 25),
        gen_string('alpha', 15),
    ]


def test_positive_create(session):
    with session:
        for name in valid_data_list():
            session.architecture.create_architecture({'name': name})
