from src.object import Object, String


def test_string_hash_key():
    pairs: dict[Object, Object] = {}
    name1 = String(value="name")
    name3 = String(value="name2")
    name2 = String(value="name")
    diff1 = String(value="My name is johnny")
    diff2 = String(value="My name is johnny")
    monkey = String(value="Monkey")

    pairs[name1] = monkey

    assert pairs[name1] == pairs[name2]

    assert name1 == name2

    assert name1 != name3

    assert diff1 == diff2
