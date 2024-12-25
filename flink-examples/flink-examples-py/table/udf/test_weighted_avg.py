import unittest

import numpy as np
from pyflink.common import Row, Configuration
from pyflink.table import AggregateFunction, DataTypes, TableEnvironment, EnvironmentSettings
from pyflink.table.expressions import call
from pyflink.table.expressions import col, lit
from pyflink.table.udf import udaf
from pyflink.table.window import Tumble


class WeightedAvg(AggregateFunction):

    def create_accumulator(self):
        # Row(sum, count)
        return Row(0, 0)

    def get_value(self, accumulator):
        if accumulator[1] == 0:
            return None
        else:
            return accumulator[0] / accumulator[1]

    def accumulate(self, accumulator, value, weight):
        accumulator[0] += value * weight
        accumulator[1] += weight

    def retract(self, accumulator, value, weight):
        accumulator[0] -= value * weight
        accumulator[1] -= weight

    def get_result_type(self):
        return DataTypes.BIGINT()

    def get_accumulator_type(self):
        return DataTypes.ROW([
            DataTypes.FIELD("f0", DataTypes.BIGINT()),
            DataTypes.FIELD("f1", DataTypes.BIGINT())])


# 定义测试类
class FlinkUDFTest(unittest.TestCase):

    def setUp(self):
        env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
        self.table_env = TableEnvironment.create(env_settings)
        config = Configuration()
        config.set_string("restart.strategy", "fixed-delay")
        config.set_integer("restart.fixed-delay.attempts", 3)
        config.set_float("restart.fixed-delay.delay", 10000)
        self.weighted_avg = udaf(
            f=WeightedAvg(),
            result_type=DataTypes.DOUBLE(),
            accumulator_type=DataTypes.ROW([
                DataTypes.FIELD("sum", DataTypes.BIGINT()),
                DataTypes.FIELD("count", DataTypes.BIGINT())
            ])
        )

    def test_weighted_avg(self):
        # 创建一个DataStream并转换为Table
        data = [(1, 2), (3, 4), (5, 6)]
        ds = self.table_env.from_elements(data, ['value', 'weight'])
        df_data = ds.to_pandas()
        for col_ in df_data.columns:
            df_data[col_] = df_data[col_].astype(np.float64)  # pip install pyarrow==3.0.0
        table = self.table_env.from_pandas(df_data)
        # 使用WeightedAvg函数进行聚合计算
        result_table = table.group_by(table.value).select(
            self.weighted_avg(table.value, table.weight).alias("avg_value"))

        # 执行查询并打印结果
        result_table.execute().print()

    def test_add_func(self):
        # the result type and accumulator type can also be specified in the udaf decorator:
        # weighted_avg = udaf(WeightedAvg(), result_type=DataTypes.BIGINT(), accumulator_type=...)
        weighted_avg = udaf(WeightedAvg())
        t = self.table_env.from_elements([(1, 2, "Lee"),
                                          (3, 4, "Jay"),
                                          (5, 6, "Jay"),
                                          (7, 8, "Lee")]).alias("value", "count", "name")

        # call registered function in Table API
        result = t.group_by(t.name).select(call("weighted_avg", t.value, t.count).alias("avg")).to_pandas()
        print(result)

        # register table
        self.table_env.create_temporary_view("source", t)

        # call registered function in SQL
        result = self.table_env.sql_query(
            "SELECT weighted_avg(`value`, `count`) AS avg FROM source GROUP BY name").to_pandas()
        print(result)

        # use the general Python aggregate function in GroupBy Window Aggregation
        tumble_window = Tumble.over(lit(1).hours) \
            .on(col("rowtime")) \
            .alias("w")

        result = t.window(tumble_window) \
            .group_by(col('w'), col('name')) \
            .select("w.start, w.end, weighted_avg(value, count)") \
            .to_pandas()
        print(result)
