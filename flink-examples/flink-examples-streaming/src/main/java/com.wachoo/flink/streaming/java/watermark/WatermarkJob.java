package com.wachoo.flink.streaming.java.watermark;

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.KeyedBroadcastProcessFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.util.Collector;

import java.time.Duration;
import java.util.Properties;

public class WatermarkJob {

    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        DataStream<String> stream = getStringDataStream(env);

        // String 转 Event
        DataStream<Event> eventStream = stream.map(Event::fromString);

        // 为事件时间分配时间戳和水印
        DataStream<Event> withTimestampsAndWatermarks = eventStream
                .assignTimestampsAndWatermarks(
                        WatermarkStrategy.<Event>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                                .withTimestampAssigner((event, timestamp) -> event.getTimestamp())
                );

        // 按客群ID分组
        DataStream<Event> keyed = withTimestampsAndWatermarks.keyBy(Event::getGroupId);

        // 定义状态描述符
        ValueStateDescriptor<Long> stateDescriptor = new ValueStateDescriptor<>(
            "latestEventTimestamp", // 状态名称
            Long.class // 状态类型
        );


        // 使用KeyedBroadcastProcessFunction来结合Watermark和状态管理
        // 需要一个外部基于Watermark的信号来触发Ready通知
            /*
        DataStream<String> readyNotifications = keyed.process(new KeyedBroadcastProcessFunction<String, Event, Void, String>() {
            private transient ValueState<Long> state;
            @Override
            public void open(org.apache.flink.configuration.Configuration parameters) throws Exception {
                state = getRuntimeContext().getState(stateDescriptor);
            }
            @Override
            public void processElement(Event value, ReadOnlyContext ctx, Collector<String> out) throws Exception {
                // 更新状态：记录每个客群ID的最新事件时间戳
                ValueState<Long> state = getRuntimeContext().getState(stateDescriptor);
                long currentTimestamp = value.getTimestamp();
                state.update(currentTimestamp);

                // 这里不直接发送Ready通知，因为我们需要基于Watermark来检查
            }

            @Override
            public void processBroadcastElement(Void value, Context ctx, Collector<String> out) throws Exception {
                // 这个方法通常用于处理广播流，但在这里我们可以模拟Watermark的进展
                // 然而，Flink没有直接的API来“监听”Watermark，所以我们通常通过窗口或定时器来间接实现
                // 这里为了简化，我们不实现广播逻辑
            }


            // 在Watermark进展时触发操作
            @Override
            public void onTimer(long timestamp, OnTimerContext ctx, Collector<String> out) throws Exception {
                // 当Watermark到达时，检查状态
                ValueState<Long> state = getRuntimeContext().getState(stateDescriptor);
                long latestEventTimestamp = state.value();
                long allowedLatency = 5000;
                if (timestamp >= latestEventTimestamp + allowedLatency) {
                    // 发送Ready通知
                    out.collect("Group " + ctx.getCurrentKey() + " is ready");
                }
            }

        });*/
        // 使用窗口函数（如TumblingEventTimeWindows）结合状态来检查Watermark

         env.execute("Combined Watermark and State Example");
    }

    private static DataStream<String> getStringDataStream(StreamExecutionEnvironment env) {

        // 假设我们有一个DataStream<Event>，其中Event包含客群ID、事件内容和时间戳
        // Kafka 消费者配置
        Properties properties = new Properties();
        properties.setProperty("bootstrap.servers", "localhost:9092");
        properties.setProperty("group.id", "flink-consumer-group");

        // 创建 Kafka 消费者
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
                "your-kafka-topic", // Kafka 主题
                new SimpleStringSchema(), // 反序列化模式
                properties
        );

        // 将 Kafka 消费者添加到数据流中
        DataStream<String> stream = env.addSource(kafkaConsumer);
        return stream;
    }

    // Event类的定义（假设它包含groupId、内容和时间戳）
    public static class Event {
        private String groupId;
        private String content;
        private long timestamp;

        // 构造函数、getter 和 setter 省略

        public String getGroupId() {
            return groupId;
        }

        public void setGroupId(String groupId) {
            this.groupId = groupId;
        }

        public String getContent() {
            return content;
        }

        public void setContent(String content) {
            this.content = content;
        }

        public long getTimestamp() {
            return timestamp;
        }

        public void setTimestamp(long timestamp) {
            this.timestamp = timestamp;
        }

        public static Event fromString(String s) {
            // 解析逻辑，这里只是一个简单的示例
            String[] parts = s.split(",");
            Event event = new Event();
            event.setGroupId(parts[ 0 ]);
            event.setContent(parts[ 1 ]);
            event.setTimestamp(Long.parseLong(parts[ 2 ]));
            return event;
        }
    }
}