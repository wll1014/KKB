package com.kedacom.ops.flink.etl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.google.protobuf.ByteString;
import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.Message;
import com.googlecode.protobuf.format.JsonFormat;
import org.apache.flink.api.common.functions.FlatMapFunction;
import org.apache.flink.api.common.serialization.AbstractDeserializationSchema;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.watermark.Watermark;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.Properties;

import com.kedacom.ops.flink.etl.proto.Dssevent.*;
import com.kedacom.ops.flink.etl.proto.Dssevstruct.*;
import com.kedacom.ops.flink.etl.proto.Dssevenum.*;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.util.Collector;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DssPbEtl {
    private final static Logger logger = LoggerFactory.getLogger(DssPbEtl.class);
    public static void dssetl() throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(1);

        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<byte[]> dss = new FlinkKafkaConsumer<byte[]>("ods.dsspb", new MyByte(), properties);
        DataStreamSource<byte[]> dss_stream = env.addSource(dss);
        //dss_stream.print();
        DataStream<String> dss_out = dss_stream.flatMap(new JsonMap());
        //dss_out.print();

        dss_out.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.dsspb",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.dsspb");

        env.execute("DssPb-Etl");
    }
    public static void main(String[] args) throws Exception {
        dssetl();
    }
    private static class MyByte extends AbstractDeserializationSchema<byte[]> {
        public byte[] deserialize(byte[] message) throws IOException {
         return message;
        }
    }
    private static String getCurTime(){
        Date d = new Date();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'");
        String newtime=sdf.format(d);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.ENGLISH);

        LocalDateTime localDateTime = LocalDateTime.parse(newtime, formatter);
        ZonedDateTime zonedDateTime = ZonedDateTime.of(localDateTime, ZoneId.systemDefault());
        zonedDateTime = zonedDateTime.withZoneSameInstant(ZoneId.of("UTC"));
        return zonedDateTime.format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"));
    }
    private static String getMessageJson(byte[] pb) throws InvalidProtocolBufferException {
        //System.out.println(pb.length);
        DssMessageWrap dss= DssMessageWrap.parseFrom(pb);
        Message message=dss;
        CltDssEvent event=dss.getEvent();
        ByteString message_body_string =dss.getMessageBody();
        JsonFormat jsonFormat = new JsonFormat();
        byte[] message_body=message_body_string.toByteArray();
        String curtime=getCurTime();

        if(event.toString().indexOf("PING")!=-1 || event.toString().indexOf("PONG")!=-1)
            return "";
        String out="";
        switch (event){
            case CLT_DSS_ADDDUMP_REQ:
                CltDssAddDumpReq adddumpreq=CltDssAddDumpReq.parseFrom(message_body);
                message=adddumpreq.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case CLT_DSS_ADDSWITCH_REQ:
                CltDssAddSwitchReq addswitchreq=CltDssAddSwitchReq.parseFrom(message_body);
                //message = addswitchreq.getDefaultInstance();
                //out = jsonFormat.printToString(message);
                message=addswitchreq.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_SENDTOBRIDGE_ACK:
                DssCltSendToBridgeAck sendtobridgeack=DssCltSendToBridgeAck.parseFrom(message_body);
                message=sendtobridgeack.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_RECEIVEFROMBRIDGE_ACK:
                DssCltReceiveFromBridgeAck receivefrombridgeack=DssCltReceiveFromBridgeAck.parseFrom(message_body);
                message=receivefrombridgeack.toBuilder().build();
                out=JsonFormat.printToString(message);
                break;
            case DSS_CLT_REMOVEDUMP_ACK:
                DssCltRemoveDumpAck removedumpack=DssCltRemoveDumpAck.parseFrom(message_body);
                message=removedumpack.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_REMOVESWITCH_ACK:
                DssCltRemoveSwitchAck removeswitchack=DssCltRemoveSwitchAck.parseFrom(message_body);
                message=removeswitchack.toBuilder().build();
                out=JsonFormat.printToString(message);
                break;
            case DSS_CLT_REMOVEBRIDGE_ACK:
                DssCltRemoveBridgeAck cltremovebridgeack=DssCltRemoveBridgeAck.parseFrom(message_body);
                message = cltremovebridgeack.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_STOPSENDTOBRIDGE_ACK:
                DssCltStopSendToBridgeAck cltstopsendtobridgeack=DssCltStopSendToBridgeAck.parseFrom(message_body);
                message = cltstopsendtobridgeack.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_STOPRECEIVEFROMBRIDGE_ACK:
                DssCltStopReceiveFromBridgeAck cltstopreceivefrombridge =DssCltStopReceiveFromBridgeAck.parseFrom(message_body);
                message = cltstopreceivefrombridge.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_REMOVECLIENT_NTF:
                DssCltRemoveClientNtf cltremoveclientntf=DssCltRemoveClientNtf.parseFrom(message_body);
                message = cltremoveclientntf.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            case DSS_CLT_RELEASEPORT_ACK:
                DssCltReleasePortAck cltreleaseportack = DssCltReleasePortAck.parseFrom(message_body);
                message = cltreleaseportack.toBuilder().build();
                out = jsonFormat.printToString(message);
                break;
            default:
                out="others";
        }
        if(!out.equals("others")) {
            JSONObject outjson = JSONObject.parseObject(out);
            outjson.put("@timestamp",curtime);
            outjson.put("message",event.toString());
            out=JSON.toJSONString(outjson);

            String type=event.toString();

            System.out.println(out);
        }
        return out;

    }
    private static class JsonMap implements FlatMapFunction<byte[],String> {
        @Override
        public void flatMap(byte[] in, Collector<String> out) throws InvalidProtocolBufferException {
            String tmp=getMessageJson(in);
            if(tmp.length()!=0 && !tmp.equals("others")) {
                out.collect(tmp);
            }
        }
    }
}
