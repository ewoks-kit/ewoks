Define Task class inputs
========================

There are two ways of defining task inputs in Ewoks when using the `Task` class:

- :ref:`Input names`: inputs are defined by their names, given as lists of strings
- :ref:`Input model`: inputs are defined by a `Pydantic model <https://docs.pydantic.dev/latest/concepts/models/>`_

These two methods are incompatible and only one should be picked (see :ref:`Incompatibility`).

.. _Input names:

Input names
-----------

Required input names are given as a list of strings via the ``input_names`` subclass argument of ``Task``. 

They can then be retrieved in the task via ``self.inputs`` or ``self.get_input_value``:

.. code-block:: python

    from ewoks import Task

    class ExampleTask(Task, input_names=["a", "b"]):
        def run(self):
            a = self.inputs.a
            b = self.get_input_value("b")

            print(f"a={a} b={b}")

For demonstration purposes, we can `execute a task from Python <./task_python.rst>`_.

.. code-block:: python-console

    >>> task = ExampleTask(inputs={"a": 1, "b": 2})
    >>> task.run()
    a=1 b=2

Since these are **required** input names, Ewoks will throw a ``TaskInputError`` if one is missing

.. code-block:: python-console

    >>> task = ExampleTask(inputs={"a": 1})
    ewokscore.task.TaskInputError: Missing inputs for <class '__main__.ExampleTask'>: {'b'}


We can allow optional inputs by giving a list of strings to a ``optional_input_names`` subclass argument of ``Task``

.. code-block:: python

    class ExampleTaskWithOptional(Task, input_names=["a", "b"], optional_input_names=["c"]):
        def run(self):
            a = self.inputs.a
            b = self.get_input_value("b")
            c = self.inputs.c

            print(f"a={a} b={b} c={c}")

These optional inputs can be specified

.. code-block:: python-console

    >>> task = ExampleTaskWithOptional(inputs={"a": 1, "b": 2, "c": 3})
    >>> task.run()
    a=1 b=2 c=3

or omitted. In this case, they will be set to the special object ``MISSING_DATA``:

.. code-block:: python-console

    >>> task = ExampleTaskWithOptional(inputs={"a": 1, "b": 2})
    >>> task.run()
    a=1 b=2 c=<MISSING_DATA>

Default values can be given thanks to ``get_input_value``

.. code-block:: python

    class ExampleTaskWithDefault(Task, input_names=["a", "b"], optional_input_names=["c"]):
        def run(self):
            a = self.inputs.a
            b = self.get_input_value("b")
            c = self.get_input_value("c", 0) # <-- Default value

            print(f"a={a} b={b} c={c}")

.. code-block:: python-console

    >>> task = ExampleTaskWithDefault(inputs={"a": 1, "b": 2})
    >>> task.run()
    a=1 b=2 c=0


Subclassing
^^^^^^^^^^^

Subclasses of a task will inherit the input names from the base class and any additional input name will be added to those:

.. code-block:: python

    class ChildExampleTask(ExampleTaskWithOptional, input_names=["d"]):
        def run(self):
            print(self.get_input_values())

.. code-block:: python-console

    >>> task = ChildExampleTask(inputs={"a": 1, "b": 2, "c": 3, "d": 4}) 
    >>> # Accepts `a`, `b` and `c` in addition to `d` ^
    >>> task.run()
    {'a': 1, 'b': 2, 'c': 3, 'd': 4}

.. _Input model:

Input model
-----------

.. versionadded:: 1.1.0

Instead of input names, it is possible to provide a `Pydantic model <https://docs.pydantic.dev/latest/concepts/models/>`_ for inputs. 

The model needs to derive from ``ewoks.BaseInputModel`` and must be provided via ``input_model`` to the task.

Inputs can then be retrieved in the task via ``self.inputs`` or ``self.get_input_value``:

.. code-block:: python

    from ewoks import Task
    from ewoks import BaseInputModel

    class Inputs(BaseInputModel):
        a: int
        b: int


    class ExampleTaskWithModel(Task, input_model=Inputs):
        def run(self):
            a = self.inputs.a
            b = self.get_input_value("b")

            print(f"a={a} b={b}")

.. code-block:: python-console

    >>> task = ExampleTaskWithModel(inputs={"a": 1, "b": 2})
    >>> task.run()
    a=1 b=2


The advantage of using a model is that **inputs are validated by Pydantic**

.. code-block:: python-console

    >>> task = ExampleTaskWithModel(inputs={"a": 1})
    ewokscore.task.TaskInputError: 1 validation error for Inputs
    b
        Field required [type=missing, input_value={'a': 1}, input_type=dict]
        For further information visit https://errors.pydantic.dev/2.10/v/missing

    >>> task = ExampleTaskWithModel(inputs={"a": 1, "b": "not_a_number"})
    ewokscore.task.TaskInputError: 1 validation error for Inputs
    b
        Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='not_a_number', input_type=str]
        For further information visit https://errors.pydantic.dev/2.10/v/int_parsing

All Pydantic features such has `Default values <https://docs.pydantic.dev/latest/concepts/fields/#default-values>`_, `Constraints <https://docs.pydantic.dev/latest/concepts/fields/#numeric-constraints>`_ or `Custom validation <https://docs.pydantic.dev/latest/concepts/validators/>`_ are available.

For example, we can add an optional input to our model by giving it a default value

.. code-block:: python

    from ewoks import Task
    from ewoks import BaseInputModel

    class Inputs(BaseInputModel):
        a: int
        b: int
        c: int = 0 # <-- `c` is optional

    class ExampleTaskWithModel(Task, input_model=Inputs):
        def run(self):
            a = self.inputs.a
            b = self.get_input_value("b")
            c = self.inputs.c

            print(f"a={a} b={b} c={c}")

.. code-block:: python-console

    >>> task = ExampleTaskWithModel(inputs={"a": 1, "b": 2})
    >>> task.run()
    a=1 b=2 c=0

.. note::

    It is possible to reproduce the default behaviour of `optional_input_names` that are set to ``MISSING_DATA`` if not set.

    For this, add ``MissingData`` as a possible type for the input in the model and use ``MISSING_DATA`` as the default value

    .. code-block:: python

        from ewoks import Task
        from ewoks import BaseInputModel
        from ewokscore.missing_data import MissingData, MISSING_DATA

        class Inputs(BaseInputModel):
            a: int
            b: int
            c: int | MissingData = MISSING_DATA # <-- `c` is optional

        class ExampleTaskWithModel(Task, input_model=Inputs):
            def run(self):
                a = self.inputs.a
                b = self.get_input_value("b")
                c = self.inputs.c

                print(f"a={a} b={b} c={c}")

    .. code-block:: python-console

        >>> task = ExampleTaskWithModel(inputs={"a": 1, "b": 2})
        >>> task.run()
        a=1 b=2 c=<MISSING_DATA>


.. _Subclassing models:

Subclassing
^^^^^^^^^^^

Subclasses of tasks with input models will inherit the model if they do not implement a model themselves

.. code-block:: python

    class ChildTask(ExampleTaskWithModel):
        def run(self):
            print(self.get_input_values())

.. code-block:: python-console

    >>> task = ChildTask(inputs={"a": 1, "b": 2, "c": 3})
    >>> task.run()
    {'a': 1, 'b': 2, 'c': 3}

If the subclass does have an input model, it must be inherit from the model of the base class to have compliant inputs

.. code-block:: python

    class NewInputs(Inputs):
        d: int


    class ChildTaskWithModel(ExampleTaskWithModel, input_model=NewInputs):
        def run(self):
            print(self.get_input_values())


.. code-block:: python-console

    >>> task = ChildTaskWithModel(inputs={"a": 1, "b": 2, "c": 3, "d": 4})
    >>> task.run()
    {'a': 1, 'b': 2, 'c': 3, 'd': 4}



.. _Incompatibility:

Incompatibility between methods
-------------------------------

.. danger::

    It is **not possible to mix** ``input_names``/``optional_input_names`` and ``input_model``!
    
    This means a ``Task`` **cannot** have both ``input_names``/``optional_input_names`` and ``input_model`` defined.
    
    But also, **a subclass must use the same input definition method as its base class**:

    - If the base class task uses ``input_names``/``optional_input_names``, the subclass must use ``input_names``/``optional_input_names`` as well.
    - If the base class task uses ``input_model``, the subclass must use an ``input_model`` that subclasses the model of the base task (see :ref:`above <Subclassing models>`).
