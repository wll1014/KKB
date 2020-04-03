package com.kedacom.ops.flink.etl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.kedacom.ops.flink.etl.generator.h225source;
import org.apache.flink.api.common.functions.MapFunction;
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
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.datastream.KeyedStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.io.IOException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Locale;
import java.util.Properties;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class H323Etl {
    public static void main(String[] args) throws Exception {
        // set up the streaming execution environment
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.setParallelism(1);
        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> h323_consumer = new FlinkKafkaConsumer<String>("ods.h323", new SimpleStringSchema(), properties);
        DataStreamSource<String> h323 = env.addSource(h323_consumer);
        DataStream<String> source_h323= h323.map(new SourceMap());
        KeyedStream<String,String> keyed_h323 =source_h323.keyBy(new h225source.MyKey());

        source_h323.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.h323",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.h323");

        // execute program
        env.execute("H.323 ETL");
    }
    public static void etl() throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        env.setParallelism(1);
        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> h323_consumer = new FlinkKafkaConsumer<String>("ods.h323", new SimpleStringSchema(), properties);
        DataStreamSource<String> h323 = env.addSource(h323_consumer);
        DataStream<String> source_h323= h323.map(new SourceMap());
        KeyedStream<String,String> keyed_h323 =source_h323.keyBy(new h225source.MyKey());

        source_h323.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.h323",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.h323");

        // execute program
        env.execute("H.323-Etl");
    }

    private static String getTime(String inputtime){
        String pattern = " \\S+$";
        Pattern p=Pattern.compile(pattern);
        Matcher m = p.matcher(inputtime);
        m.find();
        String CSTtime=m.group(0);
        String localtime=inputtime.split(CSTtime)[0];
        String puretime=localtime.replace("  "," ");
        String day=puretime.split(",")[0].split(" ")[1];
        String mon=puretime.split(",")[0].split(" ")[0];
        String yeartime=puretime.split(",")[1];

        String newday="";
        if(day.length()==1)
            newday="0"+day;
        else
            newday=day;
        String newtime=mon+" "+newday+","+yeartime;

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm:ss.n", Locale.ENGLISH);

        LocalDateTime localDateTime = LocalDateTime.parse(newtime, formatter);
        ZonedDateTime zonedDateTime = ZonedDateTime.of(localDateTime, ZoneId.systemDefault());
        zonedDateTime = zonedDateTime.withZoneSameInstant(ZoneId.of("UTC"));
        return zonedDateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"));
    }
    private static class SourceMap implements MapFunction<String,String>{
        private String pattern = " \\d+ ";
        private Pattern p=Pattern.compile(pattern);
        @Override
        public String map(String in){

            JSONObject data = new JSONObject();
            JSONObject source = JSONObject.parseObject(in);
            String summary = source.getString("summary");
            String timestamp = getTime(source.getString("timestamp"));
            Matcher m = p.matcher(summary);
            String length="";
            if (m.find( )){
                length=m.group(0);
            }
            String origins[] = summary.split(length);
            String info="";
            if(origins.length==2)
                info = origins[1];
            //from source
            String h245_ip="";
            String h245_port="";
            String guid="";         //ok
            String source164="";    //ok
            String dest164="";      //ok
            String srcport="";      //ok
            String dstport="";      //ok
            String requestSeqNum="";

            String tmp[]=summary.split(" ");
            System.out.println();
            System.out.println(summary);

            //from summary
            String src_ip=tmp[2];
            String dst_ip=tmp[3];
            String protocol=tmp[4];

            //guid
            if(summary.indexOf("RAS: registrationRequest")!=-1){
                guid="";
                h245_ip="";
                h245_port="";
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject RasMessage_tree = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject registrationRequest_element = RasMessage_tree.getJSONObject("h225.registrationRequest_element");
                requestSeqNum = registrationRequest_element.getString("h225.requestSeqNum");

            }
            else if(summary.indexOf("RAS: registrationConfirm")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject RasMessage_tree = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject registrationConfirm_element = RasMessage_tree.getJSONObject("h225.registrationConfirm_element");
                requestSeqNum = registrationConfirm_element.getString("h225.requestSeqNum");

            }
            else if(summary.indexOf("RAS: serviceControlIndication")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject RasMessage_tree = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject serviceControlIndication_element = RasMessage_tree.getJSONObject("h225.serviceControlIndication_element");
                JSONObject genericData_tree = serviceControlIndication_element.getJSONObject("h225.genericData_tree");
                JSONObject Signalling_Traversal =genericData_tree.getJSONObject("Item 0: Signalling Traversal");
                JSONObject genericData_element = Signalling_Traversal.getJSONObject("h225.GenericData_element");
                JSONObject parameters_tree = genericData_element.getJSONObject("h225.parameters_tree");
                JSONObject IncomingCallIndication = parameters_tree.getJSONObject("Item 0: IncomingCallIndication");
                JSONObject EnumeratedParameter_element = IncomingCallIndication.getJSONObject("h225.EnumeratedParameter_element");
                JSONObject content_tree = EnumeratedParameter_element.getJSONObject("h225.content_tree");
                JSONObject IncomingCallIndication_element = content_tree.getJSONObject("h460.18.IncomingCallIndication_element");
                JSONObject callID_element =IncomingCallIndication_element.getJSONObject("h460.18.callID_element");
                guid = callID_element.getString("h225.guid");
                requestSeqNum = serviceControlIndication_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("RAS: serviceControlResponse")!=-1){
                guid="";
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject RasMessage_tree = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject serviceControlResponse_element = RasMessage_tree.getJSONObject("h225.serviceControlResponse_element");
                requestSeqNum = serviceControlResponse_element.getString("h225.requestSeqNum");
            }
            //不带:的都是异常包，内部通常含有unknown字样
            else if(summary.indexOf(":")==-1){
                //1759 \xe2\x86\x92 1719 Len=127[UNKNOWN PER: unknown extension root index in choice][Malformed Packet]
                guid="";
            }
            else if(summary.indexOf("CS: releaseComplete")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.H323_UserInformation_element");
                JSONObject uu_pdu = userinfo_element.getJSONObject("h225.h323_uu_pdu_element");
                JSONObject message_body_tree = uu_pdu.getJSONObject("h225.h323_message_body_tree");
                JSONObject releaseComplete_element = message_body_tree.getJSONObject("h225.releaseComplete_element");
                JSONObject callIdentifier_element = releaseComplete_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
            }
            else if(summary.indexOf("RAS: disengageRequest")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject disengageRequest_element = userinfo_element.getJSONObject("h225.disengageRequest_element");
                JSONObject callIdentifier_element = disengageRequest_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
                requestSeqNum = disengageRequest_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("RAS: disengageReject")!=-1){
                guid="";
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject disengageReject_element = userinfo_element.getJSONObject("h225.disengageReject_element");
                requestSeqNum = disengageReject_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("RAS: admissionRequest")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject admissionRequest_element = userinfo_element.getJSONObject("h225.admissionRequest_element");
                JSONObject callIdentifier_element = admissionRequest_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
                requestSeqNum = admissionRequest_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("RAS: admissionConfirm")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                guid= all_fields.getString("h225.guid");
                JSONObject RasMessage_tree= all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject admissionConfirm_element = RasMessage_tree.getJSONObject("h225.admissionConfirm_element");
                requestSeqNum = admissionConfirm_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("RAS: infoRequestResponse")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.RasMessage_tree");
                JSONObject infoRequestResponse_element = userinfo_element.getJSONObject("h225.infoRequestResponse_element");
                JSONObject perCallInfo_tree = infoRequestResponse_element.getJSONObject("h225.perCallInfo_tree");
                JSONObject item0 = perCallInfo_tree.getJSONObject("Item 0");
                JSONObject perCallInfo_item_element = item0.getJSONObject("h225.perCallInfo_item_element");
                JSONObject callIdentifier_element = perCallInfo_item_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
                requestSeqNum = infoRequestResponse_element.getString("h225.requestSeqNum");
            }
            else if(summary.indexOf("CS: facility")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.H323_UserInformation_element");
                JSONObject uu_pdu = userinfo_element.getJSONObject("h225.h323_uu_pdu_element");
                JSONObject message_body_tree = uu_pdu.getJSONObject("h225.h323_message_body_tree");
                JSONObject facility_element = message_body_tree.getJSONObject("h225.facility_element");
                JSONObject callIdentifier_element = facility_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
                //h245.ip h245.port
                if(facility_element.containsKey("h225.h245Address_tree")) {
                    JSONObject h245Address_tree = facility_element.getJSONObject("h225.h245Address_tree");
                    JSONObject ipAddress_element = h245Address_tree.getJSONObject("h225.ipAddress_element");
                    h245_ip=ipAddress_element.getString("h225.ip");
                    h245_port=ipAddress_element.getString("h225.port");
                }
            }
            else if(summary.indexOf("CS: alerting")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.H323_UserInformation_element");
                JSONObject uu_pdu = userinfo_element.getJSONObject("h225.h323_uu_pdu_element");
                JSONObject message_body_tree = uu_pdu.getJSONObject("h225.h323_message_body_tree");
                JSONObject alerting_element = message_body_tree.getJSONObject("h225.alerting_element");
                JSONObject callIdentifier_element = alerting_element.getJSONObject("h225.callIdentifier_element");
                guid = callIdentifier_element.getString("h225.guid");
            }
            else if(info.indexOf("CS: connect")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.H323_UserInformation_element");
                JSONObject uu_pdu = userinfo_element.getJSONObject("h225.h323_uu_pdu_element");
                JSONObject message_body_tree = uu_pdu.getJSONObject("h225.h323_message_body_tree");
                JSONObject connect_element = message_body_tree.getJSONObject("h225.connect_element");
                JSONObject callidentifier= connect_element.getJSONObject("h225.callIdentifier_element");
                guid=callidentifier.getString("h225.guid");
                JSONObject address_tree = connect_element.getJSONObject("h225.h245Address_tree");
                JSONObject ipaddress_element = address_tree.getJSONObject("h225.ipAddress_element");
                h245_ip = ipaddress_element.getString("h225.ip");
                h245_port = ipaddress_element.getString("h225.port");
            }
            else if(info.indexOf("CS: setup")!=-1){
                JSONObject h225 = source.getJSONObject("h225");
                JSONObject all_fields= h225.getJSONObject("_all_fields");
                JSONObject userinfo_element = all_fields.getJSONObject("h225.H323_UserInformation_element");
                JSONObject uu_pdu = userinfo_element.getJSONObject("h225.h323_uu_pdu_element");
                JSONObject message_body_tree = uu_pdu.getJSONObject("h225.h323_message_body_tree");
                JSONObject setup_element= message_body_tree.getJSONObject("h225.setup_element");
                JSONObject sourceAddress_tree = setup_element.getJSONObject("h225.sourceAddress_tree");
                JSONObject sourceitem0 = sourceAddress_tree.getJSONObject("Item 0");
                JSONObject sourceaddr= sourceitem0.getJSONObject("h225.AliasAddress_tree");
                if(setup_element.containsKey("h225.destinationAddress_tree")) {
                    JSONObject destinationAddress_tree = setup_element.getJSONObject("h225.destinationAddress_tree");
                    JSONObject destitem0 = destinationAddress_tree.getJSONObject("Item 0");
                    JSONObject destaddr = destitem0.getJSONObject("h225.AliasAddress_tree");
                    dest164=destaddr.getString("h225.dialledDigits");
                }
                JSONObject callIdentifier_element= setup_element.getJSONObject("h225.callIdentifier_element");
                guid=callIdentifier_element.getString("h225.guid");
                //h225.dialledDigits
                source164=sourceaddr.getString("h225.dialledDigits");

            }
            else{
                guid="";
            }

            //src dst port
            JSONObject udp = source.getJSONObject("udp");
            JSONObject tcp = source.getJSONObject("tcp");
            if (udp.containsKey("_all_fields")) {
                JSONObject all_fields = udp.getJSONObject("_all_fields");
                srcport = all_fields.getString("udp.srcport");
                dstport = all_fields.getString("udp.dstport");
            }
            else {
                JSONObject all_fields = tcp.getJSONObject("_all_fields");
                srcport = all_fields.getString("tcp.srcport");
                dstport = all_fields.getString("tcp.dstport");
            }

            //data.put("source",source);
            data.put("source","");
            data.put("proto",protocol);
            data.put("guid", guid);
            data.put("info",info);
            JSONObject src=new JSONObject();
            src.put("ip",src_ip);
            src.put("port",srcport);
            JSONObject dst= new JSONObject();
            dst.put("ip", dst_ip);
            dst.put("port",dstport);
            data.put("src",src);
            data.put("dst", dst);
            JSONObject h245_addr= new JSONObject();
            h245_addr.put("ip",h245_ip);
            h245_addr.put("port", h245_port);
            data.put("h245",h245_addr);
            JSONObject dialledDigits = new JSONObject();
            dialledDigits.put("src", source164);
            dialledDigits.put("dst", dest164);
            data.put("dialledDigits", dialledDigits);
            data.put("requestSeqNum",requestSeqNum);
            data.put("@timestamp", timestamp);
            return JSON.toJSONString(data);
        }
    }
}
