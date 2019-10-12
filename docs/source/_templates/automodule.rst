{{ fullname | escape | underline}}

.. automodule:: {{ fullname }}
   :members:
   :undoc-members:
   :show-inheritance:

{# Thanks Matplotlib <3 #}

{% block classes %}
{% if classes %}

Classes
-------

.. autosummary::
   :template: autosummary.rst
   :toctree:

  {% for item in classes %}

   <!-- {% if item not in ['zip', 'map', 'reduce'] %} -->
     {{ item }}
    <!-- {% endif %} -->
  {% endfor %}
{% endif %}

{% endblock %}

{% block functions %}
  {% if functions %}

Functions
---------

.. autosummary::
   :template: autosummary.rst
   :toctree:

    {% for item in functions %}
      {% if item not in ['zip', 'map', 'reduce'] %}
        {{ item }}
      {% endif %}
    {% endfor %}
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
{# Vim: set ft=htmljinja: #}
