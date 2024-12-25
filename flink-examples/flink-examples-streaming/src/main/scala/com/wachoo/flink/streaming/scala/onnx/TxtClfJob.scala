package com.wachoo.flink.streaming.scala.onnx

import com.wachoo.flink.streaming.scala.udf.KmeansUDF
import org.apache.flink.streaming.api.scala._

import scala.util.Random


object TxtClfJob {
  def main(args: Array[String]): Unit = {
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val data = env.fromElements(generateRandomArray(5, 768))
    data.map{
        _.map{
          case arr: Array[Float] => KmeansUDF(arr)
        }
      }
      .print()

    env.execute("Flink ONNX - TxtClfJob")
  }

  def generateRandomArray(rows: Int, cols: Int): Array[Array[Float]] = {
    val random = new Random
    val array = Array.ofDim[Float](rows, cols)
    for (i <- 0 until rows) {
      for (j <- 0 until cols) {
        array(i)(j) = random.nextFloat() // nextFloat() generates a float between 0.0 and 1.0
      }
    }
    array
  }
}
