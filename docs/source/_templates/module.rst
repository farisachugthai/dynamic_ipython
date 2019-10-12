{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :show-inheritance:

{% block functions %}
{% if functions %}
.. rubric:: Functions

.. autosummary::
   :template: autosummary.rst
   :toctree:

{% for item in functions %}
  {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block classes %}
{% if classes %}
.. rubric:: Classes

.. autosummary::
   :template: autosummary.rst
   :toctree:

{% for item in classes %}
  {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

{% block exceptions %}
{% if exceptions %}
.. rubric:: Exceptions

.. autosummary::

{% for item in exceptions %}
  {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}
