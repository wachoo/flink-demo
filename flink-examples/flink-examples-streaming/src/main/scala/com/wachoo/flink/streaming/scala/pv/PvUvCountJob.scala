package com.wachoo.flink.streaming.scala.pv

import org.apache.flink.api.common.state.{ValueState, ValueStateDescriptor}
import org.apache.flink.api.scala._
import org.apache.flink.configuration.Configuration
import org.apache.flink.streaming.api.TimeCharacteristic
import org.apache.flink.streaming.api.functions.KeyedProcessFunction
import org.apache.flink.streaming.api.functions.timestamps.BoundedOutOfOrdernessTimestampExtractor
import org.apache.flink.streaming.api.scala.{DataStream, StreamExecutionEnvironment}
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.util.Collector

import java.time.Instant

object PvUvCountJob {

  case class PageView(userId: String, timestamp: Long)

  case class PvUvResult(pv: Long, uv: Long)

  def main(args: Array[String]): Unit = {
    // 设置执行环境
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime)

    // 模拟输入数据流（在实际应用中，你会从Kafka、文件或其他源读取数据）
    val pageViews: DataStream[PageView] = env.fromElements(
      PageView("user1", Instant.now().toEpochMilli),
      PageView("user2", Instant.now().minusSeconds(10).toEpochMilli),
      PageView("user1", Instant.now().minusSeconds(5).toEpochMilli)
    )

    // 分配时间戳和watermark（在这个例子中，我们假设没有乱序数据）
    val assignedTimestamps = pageViews.assignTimestampsAndWatermarks(new BoundedOutOfOrdernessTimestampExtractor[PageView](Time.seconds(0)) {
      override def extractTimestamp(element: PageView): Long = element.timestamp
    })

    // 根据用户ID进行分组，并计算PV和UV
    val pvUvCounts: DataStream[PvUvResult] = assignedTimestamps
      .keyBy(_.userId)
      .process(new KeyedProcessFunction[String, PageView, PvUvResult] {

        private var pvState: ValueState[Long] = _
        private var uvSet: scala.collection.mutable.Set[String] = _

        override def open(parameters: Configuration): Unit = {
          super.open(parameters)
          val pvDesc = new ValueStateDescriptor[Long]("pvState", classOf[Long])
          pvState = getRuntimeContext.getState(pvDesc)

          // 初始化UV集合（注意：这里使用ValueState存储整个集合可能不是最佳实践，因为状态可能会变得很大。
          // 在实际应用中，你可能需要使用更复杂的状态管理策略，比如使用RocksDBStateBackend进行外部存储。）
          uvSet = scala.collection.mutable.Set.empty[String]
//          val uvDesc = new ValueStateDescriptor[String]("uvSetDummy", classOf[String])
//          val dummyState = getRuntimeContext.getState(uvDesc)
//          dummyState.update("") // 触发状态初始化
        }

        override def processElement(value: PageView, ctx: KeyedProcessFunction[String, PageView, PvUvResult]#Context, out: Collector[PvUvResult]): Unit = {
          // 更新PV
          var pv = pvState.value()
          if (pv == null) {
            pv = 0L
          }
          pv += 1
          pvState.update(pv)

          // 更新UV
          if (!uvSet.contains(value.userId)) {
            uvSet.add(value.userId)
          }

          // 定时输出或根据需求触发输出
          // 在这个例子中，我们每次处理元素时都输出结果，但在实际应用中，你可能希望基于窗口或其他条件来输出。
          out.collect(PvUvResult(pv, uvSet.size))
        }
      })

    // 打印结果（在实际应用中，你会将结果写入到Kafka、数据库或其他存储中）
    pvUvCounts.print()

    // 执行作业
    env.execute("PvUvCount Job")
  }
}