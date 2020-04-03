package com.kedacom.ops.flink.etl;

import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.util.Properties;

public class LogEtl {
    public static void logetl() throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> log = new FlinkKafkaConsumer<String>("ods.formatlog", new SimpleStringSchema(), properties);
        DataStreamSource<String> log_stream = env.addSource(log);

        log_stream.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.media",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.media");

        env.execute("log etl");
    }
    public static void main(String[] args) throws Exception {
        logetl();
    }
}
