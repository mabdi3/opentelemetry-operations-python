API Reference
=============

..
   The above .. prevents the autosummary table from rendering in the
   document, but still causes the recursive generation of autodoc stub files.

   .. autosummary::
      :toctree: _autosummary
      :caption: API Reference
      :template: custom-module-template.rst
      :recursive:

      opentelemetry.exporter
      opentelemetry.exporter.google
      opentelemetry.tools
      opentelemetry.tools.google



.. toctree::
   :maxdepth: 5
   :caption: API Reference
   :name: apireference

   _autosummary/opentelemetry.exporter
   _autosummary/opentelemetry.exporter.google
   _autosummary/opentelemetry.tools
   _autosummary/opentelemetry.tools.google
