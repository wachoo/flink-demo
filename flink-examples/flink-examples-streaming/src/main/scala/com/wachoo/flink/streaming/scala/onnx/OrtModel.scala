package com.wachoo.flink.streaming.scala.onnx

import org.apache.commons.io.IOUtils.toByteArray
import ai.onnxruntime.{OrtEnvironment, OrtSession}

class OrtModel(resourceName: String, var env: OrtEnvironment = null) {
  var session: OrtSession = null

  def load(): Unit = {
    // Get the current ONNX runtime environment if not specified
    if (env == null) {
      env = OrtEnvironment.getEnvironment()
    }

    // Load the ONNX model from the resources InputStream
    val modelArray = toByteArray(getClass.getResourceAsStream(resourceName))
    session = env.createSession(modelArray)
  }
}
