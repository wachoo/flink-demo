import os

import onnxruntime as ort
from pyflink.table import ScalarFunction

parent_dir = os.path.dirname((os.path.dirname(__file__)))

"""
This example shows how to use ONNX model in PyFlink.
"""


class AddFive(ScalarFunction):
    def __init__(self):
        self.onnx_session = None

    def open(self, function_context):
        model_path = os.path.join(parent_dir, "models", "add_five.onnx")
        try:
            with open(model_path, "rb") as f:
                model_data = f.read()
            self.onnx_session = ort.InferenceSession(model_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ONNX session: {e}")

    def eval(self, x):
        if not isinstance(x, (int, float)):
            raise TypeError("Input must be a number")
        return self.eval_model(x)

    def eval_model(self, x):
        input_name = self.onnx_session.get_inputs()[0].name
        output_name = self.onnx_session.get_outputs()[0].name
        result = self.onnx_session.run([output_name], {input_name: x})
        print(result[0])
        return result[0]


class AddThree(ScalarFunction):
    def open(self, function_context):
        pass

    def eval(self, x):
        if not isinstance(x, (int, float)):
            raise TypeError("Input must be a number")
        return x + 3
