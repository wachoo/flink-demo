from unittest import TestCase

from pyflink.common import Configuration
from pyflink.table import EnvironmentSettings, TableEnvironment, DataTypes
from pyflink.table.expressions import call
from pyflink.table.udf import udf

from datastream.udf.hash_code import HashCode, IntToString


def add(a, b):
    return a + b


class TestHashCode(TestCase):
    def test_add(self):
        assert add(1, 2) == 3

    def setUp(self):
        env_settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
        self.table_env = TableEnvironment.create(env_settings)
        self.table_env.create_temporary_system_function("IntToString",
                                                        udf(IntToString(), DataTypes.BIGINT(), DataTypes.STRING()))

    def test_int_to_string(self):
        self.table_env.execute_sql(
            "CREATE TABLE datagen_source (" +
            "  user_id INT," +
            "  item_id STRING," +
            "  behavior STRING" +
            ") WITH (" +
            "  'connector' = 'datagen'" +
            ")"
        )
        result = self.table_env.sql_query("SELECT IntToString(user_id), item_id, behavior FROM datagen_source")
        result.execute().print()

    def test_eval(self):
        # self.fail()

        hash_code = udf(HashCode(), result_type=DataTypes.BIGINT())

        print(hash_code('a'))

        f = hash_code._func
        # assert callable(f)
        # assert f.__name__ == 'predict'
        print(f(123))
        print(f.__name__)
        assert f(123) == 3

    def test_table_api(self):
        config = Configuration()
        config.set_string("restart.strategy", "fixed-delay")
        config.set_integer("restart.fixed-delay.attempts", 3)
        config.set_float("restart.fixed-delay.delay", 10000)
        settings = EnvironmentSettings.in_batch_mode()
        table_env = TableEnvironment.create(settings)

        hash_code = udf(HashCode(), result_type=DataTypes.BIGINT())

        hash_code(call('a'))

        """
            1. use the Python function in Python Table API
            2. use the Python function in SQL API
        """
        my_table = table_env.from_elements([(1, 2, "Lee"),
                                            (3, 4, "Jay"),
                                            (5, 6, "Jay"),
                                            (7, 8, "Lee")]) \
            .alias("value", "count", "name")
        # 1. use the Python function in Python Table API
        my_table.print_schema()
        my_table.alias("value1", "name1", "count1") \
            .execute().print()
        my_table.select(my_table.value, my_table.name, my_table.count, hash_code(my_table.count)) \
            .alias("value2", "name2", "count2", "hash_code_name") \
            .execute().print()

        # 2. use the Python function in SQL API
        # table_env.create_temporary_function("hash_code", udf(HashCode(), result_type=DataTypes.BIGINT()))
        # table_env.sql_query("SELECT hash_code(1212)")
        # table_env.list_views()
