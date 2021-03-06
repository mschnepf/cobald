=======================
Component Configuration
=======================

Configuration of the :py:mod:`cobald.daemon` is performed at startup via one of two methods:
a YAML file or Python code.
While the former is more structured and easier to verify, the later allows for greater freedom.

The configuration file is the only positional argument when launching the :py:mod:`cobald.daemon`.
The file extension determines the type of configuration interface to use -
``.py`` for Python files and ``.yaml`` for YAML files.

.. code:: bash

    $ python3 -m cobald.daemon /etc/cobald/config.yaml
    $ python3 -m cobald.daemon /etc/cobald/config.py

The YAML Interface
------------------

The top level of a YAML configuration file is a mapping with two sections:
the ``pipeline`` section setting up a pool control pipeline,
and the ``logging`` section setting up the logging facilities.
The ``logging`` section is optional and follows the standard `configuration dictionary schema`_.

The ``pipeline`` section contains a sequence of :py:class:`~cobald.interface.Controller`,
:py:class:`~cobald.interface.Decorator` and :py:class:`~cobald.interface.Pool`\ s.
This uses an invocation mechanism that can use arbitrary callables to construct objects:
each mapping with a ``__type__`` key is invoked with its items as keyword arguments,
and the optional ``__args__`` as positional arguments.

.. code:: yaml

    pipeline:
        # same as ``package.module.callable(a, b, keyword1="one", keyword2="two")
        - __type__: package.module.callable
          __args__:
            - a
            - b
          keyword1: one
          keyword2: two

Each ``pipeline`` is constructed in order:
the *last* element should be a :py:class:`~cobald.interface.Pool`,
and subsequent elements recursively receive their predecessor as the ``target`` keyword.

Python Code Inclusion
---------------------

Python configuration files are loaded like regular modules.
This allows to define arbitrary types and functions, and directly chain components or configure logging.
At least one :py:class:`~.cobald.daemon.service.service` should be instantiated.

.. _`configuration dictionary schema`: https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema
