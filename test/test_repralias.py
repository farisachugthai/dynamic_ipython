from pathlib import Path
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
    # This is an odd way of doing thi but note that it's necessary as the object
    # passed to the package argument is the module not a string of the module
    # import default_profile
    # pytest.importorskip("ReprAlias", package=default_profile.startup.repralias)
    # Holy shit this still raises an error because startup isn't reocgnized
    # as an attribute of default. fuck.

    # It alternatively makes more sense to do this however.
    # Fuck me this is still raising errors
    # pytest.importorskip("default_profile.startup.repralias")
    from default_profile.startup import repralias
