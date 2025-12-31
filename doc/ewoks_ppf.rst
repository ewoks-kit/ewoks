Execute an Ewoks workflow with pypushflow
=========================================

This page presents the ewoks workflow execution with ppf engine and without ppf engine and compare result.

Initial setup
-------------

Install *ewoks*, *ewoksppf*, and *numpy*

.. code:: bash

  pip install ewoks
  pip install ewoksppf
  pip install numpy


For the demonstration, let's create a workflow with simple matrix/vector operations,
and save it as *computation.py* in a folder say "ppf_demo_task" in your current working directory.

.. code:: python
  from ewokscore import Task
  import numpy


  class GenMatrix(
      Task,
      input_names=["rows", "cols", "fill"],
      output_names=["matrix"],
  ):
    def run(self):
      rows = self.inputs.rows
      cols = self.inputs.cols
      val = self.inputs.fill
      self.outputs.matrix = numpy.full((rows, cols), val)


  class GenVector(
    Task,
    input_names=["length", "fill"],
    output_names=["vector"],
  ):
    def run(self):
      length = self.inputs.length
      val = self.inputs.fill
      self.outputs.vector = numpy.full(length, val)


  class VectorScaling(
    Task,
    input_names=["input_vector", "scale"],
    output_names=["rVec"],
  ):
    def run(self):
      ve = self.inputs.input_vector
      sc = self.inputs.scale

      self.outputs.rVec = sc * ve


  class MatrixTranspose(
    Task,
    input_names=["M"],
    output_names=["Mt"],
  ):
    def run(self):
      iM = self.inputs.M
      self.outputs.Mt = iM.transpose()


  class Mat2DFlip(
    Task,
    input_names=["M", "dir"],
    output_names=["F"],
  ):
    """flipping 2D array (horizontal or vertical)"""

    def run(self):
      direction = self.inputs.dir
      iM = self.inputs.M

      if direction == "v" or direction == "V":
        self.outputs.F = numpy.flip(iM, 0)
      elif direction == "h" or direction == "H":
        self.outputs.F = numpy.flip(iM, 1)
      else:
        self.outputs.F = iM


  class MatVecMul(
    Task,
    input_names=["M", "A", "B"],
    output_names=["C"],
  ):
    """C = B + M * A"""

    def run(self):
      M = self.inputs.M
      A = self.inputs.A
      B = self.inputs.B
      self.outputs.C = numpy.dot(M, A) + B



In the current folder, let's create an execution flow graph for our *computation* tasks.
We are making it so, it will show how a parallel execution of our computational workflow executed using ppf ewoks!


.. mermaid::

  flowchart TD
    %% Define the parallel lines
    GenMat --> Transpose --> Flip
    GenVecA --> Scale
    GenVecB

    %% Connect all to the final computation
    Flip --> MatVecMul
    Scale --> MatVecMul
    GenVecB --> MatVecMul

    %% Style for clarity
    style GenMat fill:#f9f,stroke:#333,stroke-width:2px
    style Transpose fill:#ccf,stroke:#333,stroke-width:2px
    style Flip fill:#cfc,stroke:#333,stroke-width:2px
    style GenVecA fill:#ff9,stroke:#333,stroke-width:2px
    style Scale fill:#9ff,stroke:#333,stroke-width:2px
    style GenVecB fill:#f99,stroke:#333,stroke-width:2px
    style MatVecMul fill:#9f9,stroke:#333,stroke-width:2px

    %% Box labels
    GenMat[Generate 2D Matrix]
    Transpose[Transpose Matrix]
    Flip[Flip Matrix Vertically]
    GenVecA[Generate Vector A]
    Scale[Scale Vector A]
    GenVecB[Generate Vector B]
    MatVecMul[Matrix-Vector Multiplication (C = B + M * A)]


The python code for the above computational flow chart 
say *ppf_tutorial.py*

.. code:: python
  from ewoks import convert_graph

  if __name__ == "__main__":
    node_genMat  = {'id': 'genMat', 'task_identifier': 'ppf_demo_task.computation.GenMatrix', 'task_type': 'class',
                    'default_inputs': [{"name": "rows", "value": 1000}, {"name": "cols", "value": 1000}, {"name": "fill", "value": 2.0}]}

    node_genVecA = {'id': 'genVecA', 'task_identifier': 'ppf_demo_task.computation.GenVector', 'task_type': 'class',
                    'default_inputs': [{"name": "length", "value": 1000}, {"name": "fill", "value": 1.0}]}

    node_genVecB = {'id': 'genVecB', 'task_identifier': 'ppf_demo_task.computation.GenVector', 'task_type': 'class',
                    'default_inputs': [{"name": "length", "value": 1000}, {"name": "fill", "value": 0.5}]}

    node_trans   = {'id': 'matTrans', 'task_identifier': 'ppf_demo_task.computation.MatrixTranspose', 'task_type': 'class'}
    node_flip    = {'id': 'matFlip', 'task_identifier': 'ppf_demo_task.computation.Mat2DFlip', 'task_type': 'class',
                    'default_inputs': [{"name": "dir", "value": "v"}]}

    node_scalVec = {'id': 'scalVec', 'task_identifier': 'ppf_demo_task.computation.VectorScaling', 'task_type': 'class',
                    'default_inputs': [{"name": "scale", "value": 3.0}]}

    node_matVecMul = {'id': 'matVecMul', 'task_identifier': 'ppf_demo_task.computation.MatVecMul', 'task_type': 'class'}

    links = [
        {"source": "genMat", "target": "matTrans", "data_mapping": [{"source_output": "matrix", "target_input": "M"}]},
        {"source": "matTrans", "target": "matFlip", "data_mapping": [{"source_output": "Mt", "target_input": "M"}]},
        {"source": "genVecA", "target": "scalVec", "data_mapping": [{"source_output": "vector", "target_input": "input_vector"}]},
        {"source": "matFlip", "target": "matVecMul", "data_mapping": [{"source_output": "F", "target_input": "M"}]},
        {"source": "scalVec", "target": "matVecMul", "data_mapping": [{"source_output": "rVec", "target_input": "A"}]},
        {"source": "genVecB", "target": "matVecMul", "data_mapping": [{"source_output": "vector", "target_input": "B"}]},
    ]

    nodes = [node_genMat, node_genVecA, node_genVecB, node_trans, node_flip, node_scalVec, node_matVecMul]

    workflow = {
        "graph": {"id": "parallelMatrixWorkflow"},
        "nodes": nodes,
        "links": links,
    }

    convert_graph(workflow, "parallelMatrixWorkflow.json")


.. code:: bash
  python ppf_workflow.py


Parallel Execution with ppf vs Standard ewoks
---------------------------------------------

This example will create the workflow file *parallelMatrixWorkflow.json* in the current working directory.
We will now benchmark the performance of the workflow by running it with and without NumPy's internal multithreading.


Run with NumPy restricted to a single thread (standard engine)
--------------------------------------------------------------

This disables NumPy's internal multithreading:

.. code:: bash
  time OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
  MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 
  VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1
  ewoks execute parallelMatrixWorkflow.json
    -p genMat:rows=8000 -p genMat:cols=8000
    -p genVecA:length=8000 -p genVecB:length=8000
    --merge-outputs --output=end

Run with default NumPy behavior (multi-threaded BLAS/CBLAS)
-----------------------------------------------------

.. code:: bash
  time ewoks execute parallelMatrixWorkflow.json  -p genMat:rows=8000 -p genMat:cols=8000   -p genVecA:length=8000 -p genVecB:length=8000 --merge-outputs --output=end

In these commands:

The -p flag is used to pass parameters to workflow nodes.
For example, genMat:rows=8000 sets the rows input of the genMat node to 8000.

The first version limits NumPy to a single thread using environment variables such as OMP_NUM_THREADS=1, OPENBLAS_NUM_THREADS=1, etc. 
This is useful for isolating and evaluating workflow execution with different workflow execution engine without interference from NumPy's own internal parallel processing.

On few systems (especially laptops), NumPy's multithreading can obscure or even underperform multi-threaded parallelism due to efficient cache usage and 
the highly optimized nature of BLAS operations.



Running the Same Workflow with the ppf Engine
---------------------------------------------

Now let's execute the workflow using the ppf engine, which enables concurrent workflow execution:

With NumPy restricted to single thread:

.. code:: bash
  time OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
  NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 BLIS_NUM_THREADS=1
  ewoks execute parallelMatrixWorkflow.json
    -p genMat:rows=8000 -p genMat:cols=8000
    -p genVecA:length=8000 -p genVecB:length=8000
  --merge-outputs --output=end --engine=ppf

With NumPy multithreading enabled (default):

.. code:: bash
  time ewoks execute parallelMatrixWorkflow.json
    -p genMat:rows=8000 -p genMat:cols=8000
    -p genVecA:length=8000 -p genVecB:length=8000
    --merge-outputs --output=end --engine=ppf



Performance Notes
-----------------

This workflow is structured to allow for parallel execution workflow itself. 
Specifically, the matrix generation, vector generation, and matrix transformation (transpose and flip) 
can all run concurrently before converging at a final matrix-vector multiplication.

However, the actual performance gain from using ppf depends heavily on your system:

On laptops, the default single-core NumPy version may perform better than ppf, since the shared memory cache and uniform compute-intensive operations benefit from 
long uninterrupted CPU execution.

On servers or multi-core machines, where processor affinity and independent caches are more favorable, the ppf engine typically performs better.

In summary, ppf provides true workflow level concurrent/parallelism, which is advantageous for heterogeneous workflows or IO-bound tasks.