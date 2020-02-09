import pytest


@pytest.fixture
def main_class():
    module_instance = ReprAlias()
    return module_instance


def test_ipython_has_an_alias_manager(_ip):
    assert hasattr(_ip, "alias_manager")


def test_alias_manager_aliases_greater_than_user_aliases(_ip):
    assert len(_ip.alias_manager.aliases) > len(_ip.alias_manager.user_aliases)


# def test_ReprAlias_is_iterable(main_class):
# This doesn't work because main_class is a reference to the function not
# the object. iter(main_class()) calls the fixture which pytest will raise
#  a Failure for. :/
# assert iter(main_class)
if __name__ == "__main__":
    pytest.importorskip("ReprAlias", package=default_profile.startup.repralias)
