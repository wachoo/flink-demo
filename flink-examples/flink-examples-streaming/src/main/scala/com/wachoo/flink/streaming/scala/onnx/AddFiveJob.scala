package com.wachoo.flink.streaming.scala.onnx

import com.wachoo.flink.streaming.scala.udf.AddFiveUDF
import org.apache.flink.streaming.api.scala._


object AddFiveJob {
  def main(args: Array[String]): Unit = {
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val data = env.fromElements(1.0, 2.0, 3.0, 4.0, 5.0)
    data.map {
      _.toFloat
    }.map(new AddFiveUDF).print()

    // execute program
    env.execute("Flink ONNX - Add Five")
  }
}
