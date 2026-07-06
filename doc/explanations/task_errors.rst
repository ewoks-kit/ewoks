Errors raised when executing an :term:`Ewoks` :term:`task <Task>`
=================================================================

.. warning::

    To showcase the errors raised when executing a :term:`task <Task>`, we use the :term:`task <Task>` execution mechanism described in `Execute a task from Python <../howtoguides/task_python>`_.
    
    Be sure to read `Execute a task from Python <../howtoguides/task_python>`_ before reading this page.

    The principle stays the same when executing a :term:`task <Task>` in a :term:`workflow`.


An exception encountered when running an :term:`Ewoks` :term:`task <Task>` will always be chained with a ``RuntimeError`` telling which :term:`task <Task>` failed:

.. code-block:: python

    >>> from ewokscore.tests.examples.tasks.sumtask import SumTask
    >>> task = SumTask(inputs={"a": 'a_string', "b": 10})
    >>> task.execute()
    Traceback (most recent call last):
      <...>
    TypeError: can only concatenate str (not "int") to str

    The above exception was the direct cause of the following exception:

    Traceback (most recent call last):
      <...>
    RuntimeError: Task 'ewokscore.tests.examples.tasks.sumtask.SumTask' failed

The top-level exception will always be ``RuntimeError`` while the real exception (in this case ``TypeError``) is one level below.

This is particularly important when testing or catching exceptions:

.. code-block:: python

    >>> task = SumTask(inputs={"a": 'a_string', "b": 10})
    >>> try:
    ...    task.execute()
    ... except TypeError as e:
    ...     print('TYPE_ERROR')
    ...     exception = e
    ... except RuntimeError as e:
    ...     print('RUNTIME_ERROR')
    ...     exception = e
    RUNTIME_ERROR
    >>> exception
    RuntimeError("Task 'ewokscore.tests.examples.tasks.sumtask.SumTask' failed")

We see here that the error caught is indeed the ``RuntimeError`` and not the ``TypeError``. To retrieve the original error, we have to go back to the ``RuntimeError`` cause:

.. code-block:: python
    
    >>> original_exception = exception.__cause__
    >>> original_exception
    TypeError('can only concatenate str (not "int") to str')

Full code
---------


.. code-block:: python

    from ewokscore.tests.examples.tasks.sumtask import SumTask

    task = SumTask(inputs={"a": 'a_string', "b": 10})
    try:
       task.execute()
    except TypeError as e:
        print('TYPE_ERROR')
        exception = e
    except RuntimeError as e:
        print('RUNTIME_ERROR')
        exception = e
    original_exception = exception.__cause__
