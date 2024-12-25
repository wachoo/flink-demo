import unittest

from pyflink.table import EnvironmentSettings, TableEnvironment, DataTypes
from pyflink.table.udf import udf

from datastream.udf.udf_add import AddFive, AddThree


class FlinkUDFTest(unittest.TestCase):

    def setUp(self):
        env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
        self.table_env = TableEnvironment.create(env_settings)
        self.table_env.create_temporary_system_function("AddFive",
                                                        udf(AddFive(), DataTypes.DOUBLE(), DataTypes.DOUBLE()))
        self.table_env.create_temporary_system_function("AddThree",
                                                        udf(AddThree(), DataTypes.INT(), DataTypes.INT()))

    def test_add_five(self):
        self.table_env.execute_sql("CREATE TABLE input_table (i INT) "
                                   "WITH ('connector' = 'datagen', "
                                   "'fields.i.kind' = 'random', "
                                   "'fields.i.min' = '1', "
                                   "'fields.i.max' = '10')")
        result = self.table_env.sql_query("SELECT i, AddFive(i) as i_add3 FROM input_table")
        result.execute().print()

    def test_predict(self):
        predict = udf(AddFive(), DataTypes.INT(), DataTypes.INT())
        print(predict.__class__.__name__)
        a = predict(3)
        print(a)
        assert predict(3) == 8
        assert predict(3) == 7

    def test_path(self):
        import os
        parent_dir = os.path.dirname(os.path.dirname((os.path.dirname(__file__))))
        print(parent_dir)
