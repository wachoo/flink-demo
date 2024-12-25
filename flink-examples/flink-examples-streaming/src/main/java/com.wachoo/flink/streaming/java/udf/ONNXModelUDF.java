package com.wachoo.flink.streaming.java.udf;

import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtSession;
import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtSession.Result;
import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.configuration.Configuration;

import java.nio.FloatBuffer;
import java.util.Collections;


public class ONNXModelUDF extends RichMapFunction<String, Float> {
    public OrtEnvironment env;
    public OrtSession session;

    @Override
    public void open(Configuration parameters) throws Exception {
        super.open(parameters);
        // 初始化ONNX Runtime环境和会话
        env = OrtEnvironment.getEnvironment();
        session = env.createSession("path/to/your/model.onnx", new OrtSession.SessionOptions());
    }

    @Override
    public Float map(String value) throws Exception {
        // 将输入字符串转换为浮点数组（这里需要根据实际情况进行转换）
        float[] inputData = parseInput(value);

        // 创建输入张量
        OnnxTensor inputTensor = OnnxTensor.createTensor(env, inputData);

        // 进行模型推理
        Result result = session.run(Collections.singletonMap(session.getInputNames().iterator().next(), inputTensor));

        // 获取并处理输出结果（假设模型输出一个浮点数）
        FloatBuffer outputBuffer = (FloatBuffer) result.get(0).getValue();
        float output = outputBuffer.get(0);

        return output;
    }

    // 示例输入解析方法（根据实际情况实现）
    public float[] parseInput(String input) {
        // 这里只是一个示例，你需要根据模型的输入格式来解析输入字符串
        String[] parts = input.split(",");
        float[] inputData = new float[parts.length];
        for (int i = 0; i < parts.length; i++) {
            inputData[i] = Float.parseFloat(parts[i]);
        }
        return inputData;
    }

    @Override
    public void close() throws Exception {
        super.close();
        // 关闭会话和环境
        if (session != null) {
            session.close();
        }
        if (env != null) {
            env.close();
        }
    }
}
