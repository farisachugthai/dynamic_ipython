.. currentmodule:: default_profile.util.profile_override

==============================
Rewrite the IPython ProfileDir
==============================

Override the IPython ProfileDir.

Profile Override
================

Initially created to implement a repr for the class, it was expanded in order
to also modify the behavior that automatically adds a PID dir,

It automatically creates them in the current working directory and this
behavior was not designed to be modifiable.

As a result, profiles are frequently created in the
wrong dir often enough that it should be toggleable behavior.

See Also
--------

:mod:`IPython.core.profileapp`.

Profile App API
===============
.. automodule:: default_profile.util.profile_override
   :synopsis: Rewrite IPython profiles.
   :members:
   :undoc-members:
   :show-inheritance:
