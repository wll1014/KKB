package com.kedacom.ops.flink.agg;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.apache.flink.api.common.functions.RichMapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.api.java.functions.KeySelector;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Properties;

public class H323Agg {
    public static void main(String[] args) throws Exception {
        // set up the streaming execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.setParallelism(1);
        Properties properties = new Properties();
        properties.put("bootstrap.servers", "10.67.18.100:9092");
        properties.put("zookeeper.connect", "10.67.18.100:2180");
        properties.put("group.id", "test-consumer-group");
        FlinkKafkaConsumer<String> h323_consumer = new FlinkKafkaConsumer<String>("dwd.h323", new SimpleStringSchema(), properties);
        DataStream<String> source_h323= env.addSource(h323_consumer);
        KeyedStream<String,String> keyed_h323 =source_h323.keyBy(new MyKey());
        DataStream<String> h323_with_guid = keyed_h323.map(new RecInfo());
        h323_with_guid.print();

        source_h323.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "ads.h323",
                new SimpleStringSchema()
        )).setParallelism(1).name("ads.h323");

        env.execute("H323 agg");
    }
    public static void agg() throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.setParallelism(1);
        Properties properties = new Properties();
        properties.put("bootstrap.servers", "10.67.18.100:9092");
        properties.put("zookeeper.connect", "10.67.18.100:2180");
        properties.put("group.id", "test-consumer-group");
        FlinkKafkaConsumer<String> h323_consumer = new FlinkKafkaConsumer<String>("dwd.h323", new SimpleStringSchema(), properties);
        DataStream<String> source_h323= env.addSource(h323_consumer);
        KeyedStream<String,String> keyed_h323 =source_h323.keyBy(new MyKey());
        DataStream<String> h323_with_guid = keyed_h323.map(new RecInfo());
        h323_with_guid.print();

        source_h323.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "ads.h323",
                new SimpleStringSchema()
        )).setParallelism(1).name("ads.h323");

        env.execute("H323-Agg");
    }

    private static String getSeqNum(String in) {
        JSONObject info = JSONObject.parseObject(in);
        return info.getString("requestSeqNum");
    }
    private static String getGuid(String in){
        JSONObject info = JSONObject.parseObject(in);
        return info.getString("guid");
    }
    private static String getInfo(String in){
        JSONObject info = JSONObject.parseObject(in);
        return info.getString("info");
    }
    private static String getProtocol(String in){
        JSONObject info = JSONObject.parseObject(in);
        return info.getString("proto");
    }
    private static String getH245IpPort(String in){
        JSONObject info = JSONObject.parseObject(in);
        JSONObject h245 = info.getJSONObject("h245");
        String ip = h245.getString("ip");
        String port = h245.getString("port");
        return ip+" "+port;
    }
    //获取h.245包的src和dst
    private static Tuple2<String,String> getSrcDstIpPort(String in){
        JSONObject info = JSONObject.parseObject(in);
        JSONObject dst = info.getJSONObject("dst");
        JSONObject src = info.getJSONObject("src");
        return new Tuple2<>(src.getString("ip")+" "+src.getString("port"), dst.getString("ip")+" "+dst.getString("port"));
    }

    private static String updateGuid(String in, String guid){
        JSONObject info = JSONObject.parseObject(in);
        info.put("guid",guid);
        return JSON.toJSONString(info);
    }
    private static String clearSeqNum(String in){
        JSONObject info = JSONObject.parseObject(in);
        info.put("requestSeqNum","");
        return JSON.toJSONString(info);
    }

    public static class MyKey implements KeySelector<String, String> {
        @Override
        public String getKey(String in) {
            return "H323";
        }
    }

    private static class RecInfo extends RichMapFunction<String,String> {
        private transient ValueState<HashMap<String, String>> record;
        @Override
        public String map(String in) throws IOException {
            HashMap<String, String> currentrecord = record.value();
            String guid=getGuid(in);
            String seqnum= getSeqNum(in);
            String info = getInfo(in);
            String out=in;
            String h245ipport=getH245IpPort(in);
            String protocol=getProtocol(in);

            //get requestSeqNum:guid
            //get h245 ip+port:guid
            if(guid.length()>0){

                if(seqnum.length()>0){
                    System.out.println("get guid and seqNum:"+guid+"    "+seqnum);
                    currentrecord.put(seqnum, guid);
                    record.update(currentrecord);
                }
                if(info.equals("CS: connect")){
                    System.out.println("get guid and h245ipport:"+guid+"    "+h245ipport);
                    currentrecord.put(guid,h245ipport);
                    currentrecord.put(h245ipport,guid);
                    record.update(currentrecord);
                }
            }
            //update data
            //对facility�?
            if(info.equals("CS: facility")){
                if(currentrecord.containsKey(guid)) {
                    currentrecord.put(guid,h245ipport);
                    currentrecord.put(h245ipport,guid);
                    System.out.printf("update facility h245ipport: %s",h245ipport);
                }
                else
                    out=in;
            }
            //对所有没有guid的包
            if(guid.equals("")){
                if(currentrecord.containsKey(seqnum)){
                    //update guid
                    if(currentrecord.containsKey(seqnum)) {
                        String matchedguid = currentrecord.get(seqnum);
                        System.out.println("update all packets without guid by seqNum:"+matchedguid);
                        String middle = updateGuid(in, matchedguid);
                        out = clearSeqNum(middle);
                    }
                    else
                        out=in;
                }
                //对所有h245�?
                if(protocol.equals("H.245")){
                    System.out.println("protocol=H.245");
                    Tuple2<String,String> src_dst=getSrcDstIpPort(in);
                    System.out.println("src and dst:"+src_dst);
                    if(currentrecord.containsKey(src_dst.f0)) {
                        System.out.println("update guid by src:"+currentrecord.get(src_dst.f0));
                        out = updateGuid(in, currentrecord.get(src_dst.f0));
                    }
                    else if(currentrecord.containsKey(src_dst.f1)) {
                        System.out.println("update guid by dst:"+currentrecord.get(src_dst.f1));
                        out = updateGuid(in, currentrecord.get(src_dst.f1));
                    }
                    else
                        out=in;
                }
            }

            //清除guid
            if(info.equals("CS: releaseComplete")){
                if(currentrecord.containsValue(guid)) {
                    currentrecord.values().removeAll(Arrays.asList(guid));
                }
                if(currentrecord.containsKey(guid)){
                    currentrecord.remove(guid);
                }
                record.update(currentrecord);
            }
            return out;
        }
        @Override
        public void open(Configuration config) {
            HashMap<String,String> nomap=new HashMap<>();
            ValueStateDescriptor<HashMap<String, String>> descriptor =
                    new ValueStateDescriptor<>(
                            "average", // the state name
                            TypeInformation.of(new TypeHint<HashMap<String, String>>() {}), // type information
                            nomap); // default value of the state, if nothing was set
            record = getRuntimeContext().getState(descriptor);
        }
    }
}
