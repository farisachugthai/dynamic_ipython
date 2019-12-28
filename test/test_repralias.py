# We either need the pytest fixture I made or just craft it by hand. Assume the fixtures here I guess


def test_alias_manager(_ip):
    assert len(_ip.alias_manager.aliases) > len(_ip.alias_manager.user_aliases)
