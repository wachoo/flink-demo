package com.wachoo.flink.streaming.java.udf;

import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtSession;
import org.junit.Before;
import org.junit.Test;

import java.nio.FloatBuffer;
import java.util.Collections;
import java.util.Random;

import static org.junit.Assert.assertEquals;
import static org.mockito.Mockito.*;

public class ONNXModelUDFTest {

    private ONNXModelUDF onnxModelUDF;
    private OrtSession mockSession;
    private OrtEnvironment mockEnv;

    @Before
    public void setUp() {
        onnxModelUDF = new ONNXModelUDF();
        mockSession = mock(OrtSession.class);
        onnxModelUDF.session = mockSession;
        onnxModelUDF.env = mockEnv;
    }

    @Test
    public void testOpen() {
        // 测试代码
    }

    @Test
    public void testMap() throws Exception {
        // Mock the input string
        String input = "1.0,2.0,3.0";

        // Mock the input parsing
        when(onnxModelUDF.parseInput(input)).thenReturn(new float[]{1.0f, 2.0f, 3.0f});

        // Mock the tensor creation
        OnnxTensor mockTensor = mock(OnnxTensor.class);
        when(OnnxTensor.createTensor(mockEnv, new float[]{1.0f, 2.0f, 3.0f})).thenReturn(mockTensor);

        // Mock the session run
        OrtSession.Result mockResult = mock(OrtSession.Result.class);
        FloatBuffer mockFloatBuffer = FloatBuffer.wrap(new float[]{0.5f});
        when(mockResult.get(0).getValue()).thenReturn(mockFloatBuffer);
        when(mockSession.run(anyMap())).thenReturn(mockResult);

        // Call the map method
        Float output = onnxModelUDF.map(input);

        // Verify the output
        assertEquals(0.5f, output, 0.001);

        // Verify interactions
        verify(onnxModelUDF).parseInput(input);
        verify(mockSession).run(anyMap());
    }
    public static float[][] generateRandomArray(int rows, int cols) {
        Random random = new Random();
        float[][] array = new float[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                array[i][j] = random.nextFloat(); // nextFloat() generates a float between 0.0 and 1.0
            }
        }
        return array;
    }
    @Test
    public void testMap2() throws Exception {
        String input = "1.0,2.0,3.0";
//        float[][] inputData = generateRandomArray(1, 768);
        System.out.println(input);
        OrtEnvironment env = OrtEnvironment.getEnvironment();
	    String modelPath = getClass().getClassLoader().getResource("roberta-sequence-classification-9.onnx").getPath();
        System.out.println(modelPath);
       // 确保路径正确
       if (modelPath == null || !new java.io.File(modelPath).exists()) {
           throw new RuntimeException("Model file not found at path: " + modelPath);
       }
        OrtSession session = env.createSession(modelPath, new OrtSession.SessionOptions());
        float[] inputData = onnxModelUDF.parseInput(input);

        // 创建输入张量
        OnnxTensor inputTensor = OnnxTensor.createTensor(env, inputData);

        // 进行模型推理
        OrtSession.Result result = session.run(Collections.singletonMap(session.getInputNames().iterator().next(), inputTensor));

        // 获取并处理输出结果（假设模型输出一个浮点数）
        FloatBuffer outputBuffer = (FloatBuffer) result.get(0).getValue();
        float output = outputBuffer.get(0);
        System.out.println(output);
    }
}
