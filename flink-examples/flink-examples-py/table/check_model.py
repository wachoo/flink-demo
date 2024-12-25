import os
import onnxruntime as ort
import numpy as np

# 加载 ONNX 模型
model_path = os.path.abspath("models/zx_model.onnx")
try:
    with open(model_path, "rb") as f:
        model_data = f.read()
    session = ort.InferenceSession(model_data)
except FileNotFoundError:
    raise FileNotFoundError(f"Model file not found at {model_path}")
except Exception as e:
    raise RuntimeError(f"Failed to initialize ONNX session: {e}")
# 打印模型的输入和输出节点信息
print("输入节点信息:")
for input_tensor in session.get_inputs():
    print(f"名称: {input_tensor.name}, 形状: {input_tensor.shape}, 数据类型: {input_tensor.type}")

print("\n输出节点信息:")
for output_tensor in session.get_outputs():
    print(f"名称: {output_tensor.name}, 形状: {output_tensor.shape}, 数据类型: {output_tensor.type}")

# 准备输入数据
feat_vals = np.random.rand(1, 27).astype(np.float32)  # 示例输入数据，形状为 (1, 27)
feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64)  # 示例输入数据，形状为 (1, 27)

print(feat_vals)

# 创建输入字典
inputs = {
    'feat_vals': feat_vals,
    'feat_ids': feat_ids
}

# 执行推理
outputs = session.run(None, inputs)

# 获取并打印输出结果
prob = outputs[0]  # 假设 'prob' 是模型的输出节点
print("\n推理结果:")
print(prob)

