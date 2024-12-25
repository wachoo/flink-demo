import logging
import os
import unittest

import numpy as np
from pyflink.table import EnvironmentSettings, TableEnvironment, DataTypes, expressions as expr
from pyflink.table.udf import udf

from table.udf.zx_udf import ZxUDF, zx_func

parent_dir = os.path.dirname((os.path.dirname(__file__)))


# 定义一个简单的UDF，接受两个整数参数并返回它们的和
@udf(input_types=[DataTypes.BIGINT(), DataTypes.BIGINT()], result_type=DataTypes.BIGINT())
def add_func(i, j):
    return i + j


# 定义测试类
class PyFlinkUDFTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_func(self):
        add = udf(lambda i, j: i + j, result_type=DataTypes.BIGINT())
        f = add._func
        assert f(1, 2) == 3

    def test_add_func1(self):
        assert add_func(1, 2) == 3

    def test_zx_udf(self):
        np.random.seed(42)
        feat_vals = np.random.rand(1, 27).astype(np.float32(2))  # 示例输入数据，形状为 (1, 27)
        feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64(2))  # 示例输入数据，形状为 (1, 27)
        logging.debug("feat_vals: %s", feat_vals)
        print(feat_vals.tolist())
        logging.debug("feat_ids: %s", feat_ids)
        print(feat_ids.tolist())
        zx_udf = udf(
            ZxUDF(),
            [DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())),
             DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.BIGINT()))],
            DataTypes.DOUBLE()
        )
        result = zx_udf(feat_vals, feat_ids)
        assert result == [0.5002536]


# 定义测试类
class TableApiUDFTest(unittest.TestCase):

    def setUp(self):
        env_settings = EnvironmentSettings.new_instance().in_batch_mode().build()
        self.table_env = TableEnvironment.create(env_settings)
        self.table_env.create_temporary_system_function("AddFunc", add_func)
        self.table_env.create_temporary_system_function("ZxFunc", zx_func)
        self.table_env.create_temporary_system_function(
            "ZxUDF",
            udf(
                ZxUDF(),
                [DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT())),
                 DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.BIGINT()))],
                DataTypes.DOUBLE()
            )
        )

    def test_add_func(self):
        self.table_env.sql_query("SELECT AddFunc(1, 2)").execute().print()

    def test_zx_func(self):
        np.random.seed(42)
        feat_vals = np.random.rand(1, 27).astype(np.float32)  # 示例输入数据，形状为 (1, 27)
        feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64)  # 示例输入数据，形状为 (1, 27)
        logging.debug("feat_vals: %s", feat_vals)
        print(feat_vals.tolist())
        logging.debug("feat_ids: %s", feat_ids)
        print(feat_ids.tolist())
        try:
            schema = DataTypes.ROW([
                DataTypes.FIELD("feat_vals", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT()))),
                DataTypes.FIELD("feat_ids", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.BIGINT())))
            ])

            # 创建一个临时表
            table = self.table_env.from_elements([(feat_vals.tolist(), feat_ids.tolist())], schema)

            # 使用 Table API 进行查询
            result_table = table.select(expr.call("ZxFunc", expr.col("feat_vals"), expr.col("feat_ids")))

            # 执行查询并打印结果
            result_table.execute().print()
            # # 使用参数化查询防止 SQL 注入
            # query = f"SELECT ZxFunc({feat_vals.tolist()}, {feat_ids.tolist()})"
            # print(query)
            # result = self.table_env.sql_query(query).execute()
            # result.print()
        except Exception as e:
            # 异常处理
            logging.error("SQL query execution failed: %s", str(e))

    def test_zx_udf(self):
        np.random.seed(42)
        feat_vals = np.random.rand(1, 27).astype(np.float32)  # 示例输入数据，形状为 (1, 27)
        feat_ids = np.random.randint(0, 100, size=(1, 27)).astype(np.int64)  # 示例输入数据，形状为 (1, 27)
        logging.debug("feat_vals: %s", feat_vals)
        print(feat_vals.tolist())
        logging.debug("feat_ids: %s", feat_ids)
        print(feat_ids.tolist())
        try:
            schema = DataTypes.ROW([
                DataTypes.FIELD("feat_vals", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.FLOAT()))),
                DataTypes.FIELD("feat_ids", DataTypes.ARRAY(DataTypes.ARRAY(DataTypes.BIGINT())))
            ])

            table = self.table_env.from_elements([(feat_vals.tolist(), feat_ids.tolist())], schema)

            result_table = table.select(expr.call("ZxUDF", expr.col("feat_vals"), expr.col("feat_ids")))

            result_table.execute().print()
        except Exception as e:
            # 异常处理
            logging.error("SQL query execution failed: %s", str(e))


if __name__ == '__main__':
    unittest.main()
