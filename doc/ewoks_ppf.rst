ewoks ppf
===============

This page presents the ewoks workflow execution with ppf engine.

Initial setup
---------------

Install *ewoks*, *ewoksppf*, and *numpy*

.. code:: bash

  pip install ewoks
  pip install ewoksppf
  pip install numpy


For the demonstration, let's create a simple matrix/vector operations, 
and save it as *computation.py* in a folder say *result* from your current directories

.. code:: python

    from ewokscore import Task
    import numpy

    class VecScal(
        Task,
        input_names=["iVec", "scale"],
        output_names=["rVec"],
        ):
      """ Scalling a vector
      """
      def run(self):
        ve = self.inputs.iVec
        sc = self.inputs.scale

        self.outputs.rVec = sc * ve
    
    class MatTrans(
        Task,
        input_names=["M"],
        output_names=["Mt"],
        ):
      """ Matrix Transpose
      """
      def run(self):
        iM = self.inputs.M
        self.outputs.Mt = iM.transpose()

    class Mat2DFlip(
      Task,
      input_names=["M", "dir"],
      output_names=["F"],
      ):
      """ flipping 2D array (horizontal or vertical)
      """
      def run(self):
        direction = self.inputs.dir
        iM = self.inputs.M

        if direction == 'v' or direction == 'V':
          self.outputs.F = numpy.flip(iM, 0)
        elif direction == 'h' or direction == 'H':
          self.outputs.F = numpy.flip(iM, 1)
        else :  
          self.outputs.F = iM
    
    class MatVecMul(
      Task,
      input_names=["M", "A", "B"],
      output_names=["C"],
      ):
      """ C = B + M * A
      """
      def run(self):
        M = self.inputs.M
        A = self.inputs.A
        B = self.inputs.B
        self.outputs.C = numpy.dot(M, A) + B
    
    class LoadNumpyFile(
      Task,
      input_names=["npFilePath"],
      output_names=["npArr"],
      ):
      """  loading a .npy file and load the array
      """
      def run(self):
        pth = self.inputs.npFilePath
        self.outputs.npArr = numpy.load(pth)


In the current folder, let's create an execution flow graph for our *computation* tasks.
We are making it so, it will show how a parallel processing can be performed using ppf ewoks!

.. mermaid::

   flowchart TD
       %% Define the three lines of boxes
       A1 --> B1 --> C1
       D1 --> E1
       F1

       %% Connect all lines to the output box
       C1 --> Output
       E1 --> Output
       F1 --> Output

       %% Define styles for clarity (optional)
       style A1 fill:#f9f,stroke:#333,stroke-width:2px
       style B1 fill:#ccf,stroke:#333,stroke-width:2px
       style C1 fill:#cfc,stroke:#333,stroke-width:2px
       style D1 fill:#ff9,stroke:#333,stroke-width:2px
       style E1 fill:#9ff,stroke:#333,stroke-width:2px
       style F1 fill:#f99,stroke:#333,stroke-width:2px
       style Output fill:#9f9,stroke:#333,stroke-width:2px

       %% Box labels
       A1[Load Numpy Matrix file (2D)]
       B1[Transpose 2D Array]
       C1[Flipping 2D Array]
       D1[Load Numpy Vector file]
       E1[Scale Vector]
       F1[Load Numpy Vector file]
       Output[Matrix Vector Mul]


The python code for the above computational flow chart 
say *ppf_tut.py*

.. code:: python
  from ewoks import convert_graph

  if __name__ == "__main__":
    node_load_npMat = {'id': 'ldMat',  'task_identifier': 'result.computation.LoadNumpyFile',   'task_type': 'class'}
    node_load_npA   = {'id': 'ldVecA', 'task_identifier': 'result.computation.LoadNumpyFile',   'task_type': 'class'}
    node_load_npB   = {'id': 'ldVecB', 'task_identifier': 'result.computation.LoadNumpyFile',   'task_type': 'class'}

    node_trans      = {'id': 'matTrans', 'task_identifier': 'result.computation.MatTrans',   'task_type': 'class'}
    node_flip       = {'id': 'matFlip',  'task_identifier': 'result.computation.Mat2DFlip',  'task_type': 'class',
                        "default_inputs": [{"name": "dir", "value": 'v'}] }

    node_scalVec    = {'id': 'scalVec', 'task_identifier': 'result.computation.VecScal',   'task_type': 'class',
                        "default_inputs": [{"name": "scale", "value": 1.0}] }

    node_matVecMul  = {'id': 'matVecMul', 'task_identifier': 'result.computation.MatVecMul',   'task_type': 'class'}


    link_ldMat_matTrans = {"source": "ldMat", "target": "matTrans", "data_mapping": [{"source_output": "npArr", "target_input": "M"}] }
    link_matTrans_matFlip = {"source": "matTrans", "target": "matFlip", "data_mapping": [{"source_output": "Mt", "target_input": "M"}] }

    link_ldVecA_scalVec  = {"source": "ldVecA", "target": "scalVec", "data_mapping": [{"source_output": "npAr", "target_input": "iVec"}] }


    link_ldVecB_matVecMul  = {"source": "ldVecB", "target": "matVecMul", "data_mapping": [{"source_output": "npArr", "target_input": "B"}] }
    link_scalVec_matVecMul = {"source": "scalVec", "target": "matVecMul", "data_mapping": [{"source_output": "rVec", "target_input": "A"}] }
    link_flipM_matVecMul   = {"source": "matFlip", "target": "matVecMul", "data_mapping": [{"source_output": "F", "target_input": "M"}] }

    al_nodes = [node_load_npMat,
                node_load_npA,
                node_load_npB,
                node_trans,
                node_flip,
                node_scalVec,
                node_matVecMul,
              ]

    al_links = [link_ldMat_matTrans,
               link_matTrans_matFlip,
               link_ldVecA_scalVec,
               link_ldVecB_matVecMul,
               link_scalVec_matVecMul,
               link_flipM_matVecMul,
              ]
    
    graph = {"id": "mathParallelFlow"}
    workflow = {"nodes" : al_nodes,
                "links" : al_links,
                "graph" : graph,
              }
    convert_graph(workflow, "result/mathParallelFlow.json")

.. code:: bash
  python ppf_tut.py

This will create *mathParallelFlow.json* file in the folder *result*

To test our workflow, let's create some sample .npy matrix and vector files

*sample.py*
.. code:: python
  import numpy
  
  M = numpy.array([[1,2],[3,4]])
  A = numpy.array([1,1])
  numpy.save('result/matrix', M)
  numpy.save('result/vector', A)

.. code:: bash
  python sample.py

It created the two files in the folder *result* namely *matrix.npy* and *vector.npy*

Lets run the created workflow json in simple ewoks
.. code:: bash
  ewoks execute result/mathParallelFlow.json -p ldMat:npFilePath="result/matrix.npy" -p ldVecA:npFilePath="result/vector.npy" -p ldVecB:npFilePath="result/vector.npy" --output=end

In the above command, *-p* means the parameter *ldMat:npFilePath="result/matrix.npy"* means providing the path as string to the input of the *ldMat* node. 


The above ewoks command runs the above workflow. When looking at the workflow, it could be parallelized, we have three
computational lines that join, those computations can be executed in parallel.

We will do parallel execution using ppf engine as follows

.. code:: bash
  ewoks execute result/mathParallelFlow.json -p ldMat:npFilePath="result/matrix.npy" -p ldVecA:npFilePath="result/vector.npy" -p ldVecB:npFilePath="result/vector.npy" --output=end --merge-outputs --engine=ppf


When you analyse using a time profile, you won't see any difference, since our numpy vectors are too small or the computation involved here also not that heavy.
But when you develop some engine for heavy computation, that might create the difference. But may not be linearly effective; there is always a hardware/core OS bottleneck!
