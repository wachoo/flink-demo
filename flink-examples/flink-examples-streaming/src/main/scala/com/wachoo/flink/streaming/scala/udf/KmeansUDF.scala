package com.wachoo.flink.streaming.scala.udf

import ai.onnxruntime.OnnxTensor
import com.wachoo.flink.streaming.scala.onnx.OrtModel
import org.apache.flink.api.common.functions.RichMapFunction
import org.apache.flink.configuration.Configuration

import scala.collection.JavaConversions.mapAsJavaMap


class KmeansUDF extends RichMapFunction[Array[Float], Float] {
  var model: OrtModel = null

  override def open(config: Configuration): Unit = {
    model = new OrtModel("/kmeans_model.onnx")
    model.load()
  }

  override def close(): Unit = {
    model.session.close()
    model.env.close()
  }

  def map(in: Array[Float]): Float = {
    val tensor = OnnxTensor.createTensor(model.env, Array(in))
    val inputs = mapAsJavaMap(Map("float_input" -> tensor))
    
    // Run the inputs through the ONNX model
    val results = model.session.run(inputs).get(0)
    val output = results.getValue().asInstanceOf[Array[Float]]
    println(s">>>>>>>>>>output: ${output(0)}")
    output(0)
  }
}
