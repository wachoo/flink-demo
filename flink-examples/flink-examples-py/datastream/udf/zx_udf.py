import os

import onnxruntime as ort
from pyflink.table import ScalarFunction

parent_dir = os.path.dirname((os.path.dirname(__file__)))

"""
This example shows how to use ONNX model in PyFlink.
"""


class ZxUDF(ScalarFunction):
    def __init__(self):
        self.onnx_session = None

    def open(self, function_context):
        model_path = os.path.join(parent_dir, "models", "zx_model.onnx")
        try:
            with open(model_path, "rb") as f:
                model_data = f.read()
            self.onnx_session = ort.InferenceSession(model_data)
            for input_tensor in self.onnx_session.get_inputs():
                print(
                    f"输入节点信息:\n, 名称: {input_tensor.name}, 形状: {input_tensor.shape}, 数据类型: {input_tensor.type}")
            for output_tensor in self.onnx_session.get_outputs():
                print(
                    f"输出节点信息:\n, 名称: {output_tensor.name}, 形状: {output_tensor.shape}, 数据类型: {output_tensor.type}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ONNX session: {e}")

    def eval(self, feat_ids, feat_vals):
        if not isinstance(feat_ids, (int, float)):
            raise TypeError("feat_ids must be a number")
        return self.eval_model(feat_ids, feat_vals)

    def eval_model(self, feat_ids, feat_vals):
        if self.onnx_session is None:
            raise ValueError("ONNX session is not initialized")
        inputs = {
            'feat_vals': feat_vals,
            'feat_ids': feat_ids
        }

        outputs = self.onnx_session.run(None, inputs)
        # 获取并打印输出结果
        prob = outputs[0]  # 假设 'prob' 是模型的输出节点
        print("\n推理结果:")
        print(prob)
        return prob
