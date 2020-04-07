.. currentmodule:: default_profile.util.profile_override

================
Profile Override
================

Override the IPython :class:`IPython.core.profiledir.ProfileDir`.

Initially created to implement a repr for the class, it was expanded in order
to also modify the behavior that automatically adds the directories.:

#) PID

#) security

#) log

#) db

It automatically creates them in the current working directory and this
behavior was not designed to be modifiable.

As a result, profiles are frequently created in the
wrong dir often enough that it should be configurable behavior.

See Also
--------
:mod:`IPython.core.profileapp`
   How IPython implements the profile originally.
:mod:`IPython.core.profiledir`
   The overridden class.


Profile App API
===============

.. automodule:: default_profile.util.profile_override
   :synopsis: Rewrite IPython profiles.
   :members:
   :undoc-members:
   :show-inheritance:

