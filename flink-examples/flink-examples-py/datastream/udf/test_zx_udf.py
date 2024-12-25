import os
from unittest import TestCase

import numpy as np
import onnxruntime as ort
from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, TableEnvironment, DataTypes
from pyflink.table.udf import udf

from datastream.udf.zx_udf import ZxUDF

parent_dir = os.path.dirname((os.path.dirname(__file__)))


class TestZfUDF(TestCase):

    def setUp(self):
        env_settings = EnvironmentSettings.new_instance().in_batch_mode().build()
        self.table_env = TableEnvironment.create(env_settings)
        self.env = StreamExecutionEnvironment.get_execution_environment()
        self.table_env.create_temporary_system_function(
            "ZxUDF",
            udf(
                ZxUDF(),
                DataTypes.MAP(
                    DataTypes.STRING(),
                    DataTypes.ARRAY(DataTypes.FLOAT())
                ),
                DataTypes.DOUBLE()
            )
        )

    def test_eval(self):

        data_stream = self.env.from_collection([(1,), (2,)], type_info=Types.ROW_NAMED(["a"], [Types.INT()]))
        table = self.table_env.create_temporary_view("input_table", data_stream)
        result = self.table_env.sql_query("SELECT double(a) FROM input_table")
        result.execute().print()

    def test_eval1(self):
        # 固定随机种子，确保测试的可重复性
        np.random.seed(42)
        # 准备输入数据
        feat_vals = np.random.rand(1, 27).astype(np.float32)
        feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64)

        # 创建输入字典
        inputs = {
            'feat_vals': feat_vals,
            'feat_ids': feat_ids
        }
        # 执行 UDF 函数
        query = """
                    SELECT ZxUDF(ARRAY[{feat_vals}], ARRAY[{feat_ids}]) AS score
                    FROM VALUES (1)
                """
        formatted_query = query.format(
            feat_vals=inputs['feat_vals'][0],
            feat_ids=inputs['feat_ids'][0]
        )

        print(formatted_query)
        try:
            result = self.table_env.sql_query(formatted_query)
            result.execute().print()
        except Exception as e:
            print(f"An error occurred: {e}")

    def test_eval2(self):
        model_path = os.path.join(parent_dir, "models", "zx_model.onnx")

        try:
            with open(model_path, "rb") as f:
                model_data = f.read()
            self.session = ort.InferenceSession(model_data)
        except FileNotFoundError:
            raise FileNotFoundError(f"Model file not found at {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ONNX session: {e}")
        # 打印模型的输入和输出节点信息
        # for input_tensor in self.session.get_inputs():
        #     print(
        #         f"输入节点信息:\n名称: {input_tensor.name}, 形状: {input_tensor.shape}, 数据类型: {input_tensor.type}")
        #
        # for output_tensor in self.session.get_outputs():
        #     print(
        #         f"输出节点信息:\n名称: {output_tensor.name}, 形状: {output_tensor.shape}, 数据类型: {output_tensor.type}")

        np.random.seed(42)  # 固定随机种子，确保测试的可重复性
        feat_vals = np.random.rand(1, 27).astype(np.float32)  # 示例输入数据，形状为 (1, 27)
        feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64)  # 示例输入数据，形状为 (1, 27)
        self.eval_model(feat_ids, feat_vals)

    def eval_model(self, feat_ids, feat_vals):
        if self.session is None:
            raise ValueError("ONNX session is not initialized")
        inputs = {
            'feat_vals': feat_vals,
            'feat_ids': feat_ids
        }

        outputs = self.session.run(None, inputs)
        # 获取并打印输出结果
        prob = outputs[0]  # 假设 'prob' 是模型的输出节点
        print("\n推理结果:")
        print(prob)
        return prob
