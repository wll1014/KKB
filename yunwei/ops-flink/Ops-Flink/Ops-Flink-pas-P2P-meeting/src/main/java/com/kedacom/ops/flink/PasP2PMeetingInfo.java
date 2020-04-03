package com.kedacom.ops.flink;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.kedacom.ops.flink.basic.PasMeetingList;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.common.state.MapStateDescriptor;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.util.Properties;

public class PasP2PMeetingInfo {
    private static PasMeetingList pasmeetinglist=new PasMeetingList();

    private static MapStateDescriptor<String, String> ApsDescriptor =new MapStateDescriptor<String, String>(
            "Aps",
            BasicTypeInfo.STRING_TYPE_INFO,
            BasicTypeInfo.STRING_TYPE_INFO
    );

    public static void writeP2PMeetingList() throws Exception {
        System.out.println("writeP2PMeetingList start");
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> pas = new FlinkKafkaConsumer<String>("dwd.nms.pas", new SimpleStringSchema(), properties);
        FlinkKafkaConsumer<String> aps = new FlinkKafkaConsumer<String>("dwd.nms.aps", new SimpleStringSchema(), properties);

        DataStreamSource<String> pas_stream = env.addSource(pas);
        DataStreamSource<String> aps_stream = env.addSource(aps);

        //pas_stream.print();
        DataStream<String> p2p_meeting_create=pas_stream.filter(new GetPasCreateMeetingInfo());
        DataStream<String> p2p_meeting_destroy=pas_stream.filter(new GetPasReleaseMeetingInfo());
        DataStream<String> aps_pas_online=aps_stream.filter(new GetPasOnOffInfo());
        //p2p_meeting_destroy.print();
        //p2p_meeting_create.print();
        DataStream<String> pasmessage = env.addSource(new PasP2PMessage());
        //pasmessage.print();

        pasmessage.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.gen.nms.pas-p2p-meeting",//dest topic，会重新创建一�?
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.gen.nms.pas-p2p-meeting");
        env.execute("Pas-P2P-Meeting-Info-Agg");
    }

    public static class GetPasOnOffInfo implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            if(sentence.indexOf("EV_DEV_ONLINE")!=-1) {
                JSONObject object = JSONObject.parseObject(sentence);
                JSONObject beat=object.getJSONObject("beat");
                String dev_moid=beat.getString("dev_moid");
                pasmeetinglist.addPas(dev_moid);
                return true;
            }
            else if(sentence.indexOf("EV_DEV_OFFLINE")!=-1){
                JSONObject object = JSONObject.parseObject(sentence);
                JSONObject beat=object.getJSONObject("beat");
                String dev_moid=beat.getString("dev_moid");
                pasmeetinglist.deletePas(dev_moid);
                return true;
            }
            else
                return false;
        }
    }

    public static class GetPasReleaseMeetingInfo implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            if(sentence.indexOf("EV_PAS_P2PCONF_DESTROY")!=-1) {
                JSONObject object = JSONObject.parseObject(sentence);
                JSONObject beat=object.getJSONObject("beat");
                String dev_moid=beat.getString("dev_moid");
                JSONObject source = object.getJSONObject("source");
                String createtimestr=source.getString("rpttimestamp");
                JSONObject confinfo=source.getJSONObject("confinfo");
                String callerE164=confinfo.getString("callerE164");
                String calleeE164=confinfo.getString("calleeE164");

                pasmeetinglist.destroyMeeting(dev_moid,callerE164, calleeE164);
                return true;
            }
            else
                return false;
        }
    }
    public static class GetPasCreateMeetingInfo implements FilterFunction<String> {
        //"devid":"dbbf9d4c-b8d7-11e8-b470-a4bf01306d06",
        @Override
        public boolean filter(String sentence) throws Exception {
            if(sentence.indexOf("EV_PAS_P2PCONF_CREATE")!=-1) {
                //System.out.println(sentence);
                JSONObject object = JSONObject.parseObject(sentence);
                JSONObject beat=object.getJSONObject("beat");
                String dev_moid=beat.getString("dev_moid");
                JSONObject source = object.getJSONObject("source");
                JSONObject confinfo=source.getJSONObject("confinfo");
                JSONObject caller=confinfo.getJSONObject("caller");
                String caller_devname=caller.getString("devname");
                JSONObject callee=confinfo.getJSONObject("callee");
                String callee_devname=callee.getString("devname");
                String createtimestr=source.getString("rpttimestamp");
                Long createtime=Long.parseLong(createtimestr)/1000;
                //System.out.println("new meeting:    "+dev_moid+createtimestr+caller_devname+callee_devname);

                pasmeetinglist.addMeeting(dev_moid,createtime,caller_devname,callee_devname);
                //System.out.println("pasmeetinglist: "+JSON.toJSONString(pasmeetinglist));
                return true;
            }
            else
                return false;
        }
    }

    private static class PasP2PMessage implements SourceFunction<String> {
        private volatile boolean isRunning = true;
        @Override
        public void run(SourceContext<String> ctx) throws Exception {

            while (isRunning) {
                Thread.sleep(30000);
                System.out.println("pasmeetinglist:     "+JSON.toJSONString(pasmeetinglist));
                ctx.collect(JSON.toJSONString(pasmeetinglist));
            }
        }
        @Override
        public void cancel() {
            isRunning = false;
        }
    }
}
