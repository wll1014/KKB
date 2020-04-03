package com.kedacom.ops.flink;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.kedacom.ops.flink.basic.PasMeetingList;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.BroadcastState;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.state.ReadOnlyBroadcastState;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.BroadcastStream;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.co.BroadcastProcessFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.util.Collector;

import java.util.Properties;

public class PasP2PMeetingAgg {
    private static MapStateDescriptor<String, String> MeetingStateDescriptor =new MapStateDescriptor<String, String>(
            "Meeting State",
            BasicTypeInfo.STRING_TYPE_INFO,
            BasicTypeInfo.STRING_TYPE_INFO
    );

    public static void pasP2PMeetingAgg() throws Exception {
        System.out.println("pasP2PMeetingAgg start");
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);
        env.setStreamTimeCharacteristic(TimeCharacteristic.ProcessingTime);

        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> pas = new FlinkKafkaConsumer<String>("dwd.nms.pas", new SimpleStringSchema(), properties);
        FlinkKafkaConsumer<String> pasmeetinglist = new FlinkKafkaConsumer<String>("dwd.gen.nms.pas-p2p-meeting", new SimpleStringSchema(), properties);
        FlinkKafkaConsumer<String> aps = new FlinkKafkaConsumer<String>("dwd.gen.nms.aps", new SimpleStringSchema(), properties);
        DataStreamSource<String> pas_stream = env.addSource(pas);
        DataStreamSource<String> pas_meeting_list = env.addSource(pasmeetinglist);
        DataStreamSource<String> aps_stream = env.addSource(aps);
        DataStream<String> pas_info = pas_stream.filter(new GetPasInfo());
        //pas_stream.print();
        //pas_info.print();
        //pas_meeting_list.print();

        BroadcastStream<String> pas_meeting_broadcast = pas_meeting_list.broadcast(MeetingStateDescriptor);
        DataStream<String> pas_meeting_count=pas_info.connect(pas_meeting_broadcast).process(new CorrectConfmtcount());

        //t.print();
        pas_meeting_count.print();

        pas_meeting_count.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "ads.nms.pas-p2p-meeting",//dest topic，会重新创建一�?
                new SimpleStringSchema()
        )).setParallelism(1).name("ads.nms.pas-p2p-meeting");


        env.execute("Pas-P2P-Meeting-Agg");
    }

    private static class CorrectConfmtcount extends BroadcastProcessFunction<String, String, String> {
        @Override
        public void processElement(String s, ReadOnlyContext ctx, Collector<String> collector) throws Exception{
            ReadOnlyBroadcastState<String, String> broadcastState = ctx.getBroadcastState(MeetingStateDescriptor);
            if(broadcastState.get("pas_p2p_meeting_list")!=null) {
                System.out.println("get broadcast state:    " + broadcastState.get("pas_p2p_meeting_list"));
                String p2pmeetinglist=broadcastState.get("pas_p2p_meeting_list");
                String dev_moid=getDevMoid(s);
                System.out.println("dev_moid    :"+dev_moid);
                PasMeetingList pmeetinglist=JSON.parseObject(p2pmeetinglist, PasMeetingList.class);
                int meetingcount=pmeetinglist.getMeetingLength(dev_moid);
                System.out.println("meeting count:  "+meetingcount);
                String out=changeConftcount(s,meetingcount);
                System.out.println("out:    "+out);
                collector.collect(out);
            }
            else
                System.out.println("get broadcast state--null, not show.");
        }
        @Override
        public void processBroadcastElement(String s, Context ctx, Collector<String> collector) throws Exception{
            BroadcastState<String, String> broadcastState = ctx.getBroadcastState(MeetingStateDescriptor);
            //PasMeetingList pmlist=JSON.parseObject(s,PasMeetingList.class);
            //int meetingcount=pmlist.getMeetingCount();
            //System.out.println("processBroadcastElement:    "+s);
            broadcastState.put("pas_p2p_meeting_list", s);
        }

        private String changeConftcount(String in, int meetingcount){
            JSONObject object = JSONObject.parseObject(in);
            JSONObject source = object.getJSONObject("source");
            JSONObject pasinfo = source.getJSONObject("pasinfo");
            pasinfo.put("confmtcount",meetingcount*2);
            String out=JSON.toJSONString(object);
            return out;
        }
        private String getDevMoid(String in){
            JSONObject object = JSONObject.parseObject(in);
            JSONObject beat = object.getJSONObject("beat");
            String dev_moid = beat.getString("dev_moid");
            return dev_moid;
        }
    }
    public static class CorrectP2P implements MapFunction<String, String>{
        @Override
        public String map(String input){
            JSONObject object = JSONObject.parseObject(input);
            JSONObject source = object.getJSONObject("source");
            JSONObject pasinfo = source.getJSONObject("pasinfo");
            String confmtcount = pasinfo.getString("confmtcount");
            System.out.println("original confmtcount:   "+confmtcount);
            pasinfo.put("confmtcount",1);
            return "";
        }
    }
    public static class GetPasInfo implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            if(sentence.indexOf("EV_PAS_INFO")!=-1)
                return true;
            else
                return false;
        }
    }
}
