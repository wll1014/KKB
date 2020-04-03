package com.kedacom.ops.flink;

import com.alibaba.fastjson.JSONObject;
import org.apache.flink.api.common.functions.FilterFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.DataStreamSource;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;

import java.util.Properties;

public class NmsEtl {
    public static void main(String[] args) throws Exception {
        StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        env.setParallelism(4);
        Properties properties = new Properties();
        properties.put("bootstrap.servers","10.67.18.100:9092");
        properties.put("zookeeper.connect","10.67.18.100:2180");
        properties.put("group.id","test-consumer-group");
        FlinkKafkaConsumer<String> nms_consumer = new FlinkKafkaConsumer<String>("ods.nms", new SimpleStringSchema(), properties);
        DataStreamSource<String> nms = env.addSource(nms_consumer);
        DataStream<String> machine = nms.filter(new machineFilter());
        DataStream<String> mt = nms.filter(new mtFilter());
        DataStream<String> amc= nms.filter(new amcFilter());
        DataStream<String> amcapi = nms.filter(new amcapiFilter());
        DataStream<String> pas = nms.filter(new pasFilter());
        DataStream<String> api= nms.filter(new apiFilter());
        DataStream<String> apicore = nms.filter(new apicoreFilter());
        DataStream<String> aps = nms.filter(new apsFilter());
        DataStream<String> bmc = nms.filter(new bmcFilter());
        DataStream<String> cds = nms.filter(new cdsFilter());
        DataStream<String> cmc = nms.filter(new cmcFilter());
        DataStream<String> cmdataproxy = nms.filter(new cmdataproxyFilter());
        DataStream<String> cmu = nms.filter(new cmuFilter());
        DataStream<String> css = nms.filter(new cssFilter());
        DataStream<String> dcs = nms.filter(new dcsFilter());
        DataStream<String> dms = nms.filter(new dmsFilter());
        DataStream<String> dssmaster = nms.filter(new dssmasterFilter());
        DataStream<String> dssworker = nms.filter(new dssworkerFilter());
        DataStream<String> ejabberd = nms.filter(new ejabberdFilter());
        DataStream<String> glusterfs = nms.filter(new glusterfsFilter());
        DataStream<String> glusterfsd = nms.filter(new glusterfsdFilter());
        DataStream<String> graphite = nms.filter(new graphiteFilter());
        DataStream<String> hduapiagent = nms.filter(new hduapiagentFilter());
        DataStream<String> hdupool = nms.filter(new hdupoolFilter());
        DataStream<String> mediamaster = nms.filter(new mediamasterFilter());
        DataStream<String> mediaworker =nms.filter(new mediaworkerFilter());
        DataStream<String> modb =nms.filter(new modbFilter());
        DataStream<String> mysql = nms.filter(new mysqlFilter());
        DataStream<String> nds = nms.filter(new ndsFilter());
        DataStream<String> nms_bridge26 =nms.filter(new nmsbridge26Filter());
        DataStream<String> nms_bridge48 =nms.filter(new nmsbridge48Filter());
        DataStream<String> nms_collector = nms.filter(new nmscollectorFilter());
        DataStream<String> nms_starter = nms.filter(new nmsstarterFilter());
        DataStream<String> nms_webserver = nms.filter(new nmswebserverFilter());
        DataStream<String> pms = nms.filter(new pmsFilter());
        DataStream<String> portal = nms.filter(new portalFilter());
        DataStream<String> portalcore = nms.filter(new portalcoreFilter());
        DataStream<String> prsworker = nms.filter(new prsworkerFilter());
        DataStream<String> rabbitmq = nms.filter(new rabbitmqFilter());
        DataStream<String> redis = nms.filter(new redisFilter());
        DataStream<String> redis_nms = nms.filter(new redisnmsFilter());
        DataStream<String> restapi = nms.filter(new restapiFilter());
        DataStream<String> rms = nms.filter(new rmsFilter());
        DataStream<String> service = nms.filter(new serviceFilter());
        DataStream<String> servicecore =nms.filter(new servicecoreFilter());
        DataStream<String> sm = nms.filter(new smFilter());
        DataStream<String> sso = nms.filter(new ssoFilter());
        DataStream<String> ssocore = nms.filter(new ssocoreFilter());
        DataStream<String> sus = nms.filter(new susFilter());
        DataStream<String> susmgr = nms.filter(new susmgrFilter());
        DataStream<String> tomcat = nms.filter(new tomcatFilter());
        DataStream<String> upu = nms.filter(new upuFilter());
        DataStream<String> upucore = nms.filter(new upucoreFilter());
        DataStream<String> vrs = nms.filter(new vrsFilter());
        DataStream<String> zookeeper = nms.filter(new zookeeperFilter());

        machine.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.machine",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.machine");

        mt.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.mt",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.mt");

        amc.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.amc",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.amc");

        amcapi.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.amcapi",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.amcapi");

        pas.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.pas",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.pas");

        api.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.api",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.api");

        apicore.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.apicore",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.apicore");

        aps.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.aps",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.aps");

        bmc.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.bmc",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.bmc");

        cds.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.cds",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.cds");

        cmc.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.cmc",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.cmc");

        cmdataproxy.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.cmdataproxy",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.cmdataproxy");

        cmu.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.cmu",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.cmu");

        css.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.css",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.css");

        dcs.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.dcs",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.dcs");

        dms.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.dms",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.dms");

        dssmaster.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.dssmaster",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.dssmaster");

        dssworker.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.dssworker",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.dssworker");

        ejabberd.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.ejabberd",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.ejabberd");

        glusterfs.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.glusterfs",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.glusterfs");

        glusterfsd.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.glusterfsd",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.glusterfsd");

        graphite.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.graphite",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.graphite");

        hduapiagent.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.hduapiagent",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.hduapiagent");

        hdupool.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.hdupool",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.hdupool");

        mediamaster.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.media-master",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.media-master");

        mediaworker.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.media-worker",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.media-worker");

        modb.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.modb",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.modb");

        mysql.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.mysql",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.mysql");

        nds.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nds",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nds");

        nms_bridge26.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nms_bridge26",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nms_bridge26");

        nms_bridge48.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nms_bridge48",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nms_bridge48");

        nms_collector.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nms_collector",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nms_collector");

        nms_starter.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nms_starter",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nms_starter");

        nms_webserver.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.nms_webserver",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.nms_webserver");

        pms.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.pms",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.pms");

        portal.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.portal",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.portal");

        portalcore.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.portalcore",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.portalcore");

        prsworker.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.prsworker",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.prsworker");

        rabbitmq.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.rabbitmq",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.rabbitmq");

        redis.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.redis",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.redis");

        redis_nms.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.redis_nms",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.redis_nms");

        restapi.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.restapi",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.restapi");

        rms.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.rms",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.rms");

        service.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.service",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.service");

        servicecore.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.servicecore",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.servicecore");

        sm.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.sm",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.sm");

        sso.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.sso",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.sso");

        ssocore.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.ssocore",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.ssocore");

        sus.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.sus",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.sus");

        susmgr.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.susmgr",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.susmgr");

        tomcat.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.tomcat",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.tomcat");

        upu.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.upu",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.upu");

        upucore.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.upucore",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.upucore");

        vrs.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.vrs",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.vrs");

        zookeeper.addSink(new FlinkKafkaProducer<String>(
                "10.67.18.100:9092",
                "dwd.nms.zookeeper",
                new SimpleStringSchema()
        )).setParallelism(1).name("dwd.nms.zookeeper");

        env.execute("Nms-Etl");
    }
    public static class machineFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            if(src_type.equals("x86_server"))
                return true;
            else if(src_type.equals("smu"))
                return true;
            else if(src_type.equals("hdu"))
                return true;
            else if(src_type.equals("ceu"))
                return true;
            else if(src_type.equals("ceu_e"))
                return true;
            else if(src_type.equals("jd1000"))
                return true;
            else if(src_type.equals("jd2000"))
                return true;
            else if(src_type.equals("jd4000"))
                return true;
            else return src_type.equals("umm");
        }
    }
    public static class mtFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            if(src_type.equals("bridge26"))
                return true;
            else return src_type.equals("bridge48");
        }
    }
    public static class pasFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            if(src_type.equals("pas"))
                return true;
            else return false;
        }
    }
    public static class amcFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            JSONObject object = JSONObject.parseObject(sentence);
            JSONObject beat = object.getJSONObject("beat");
            String src_type=beat.getString("src_type");
            if(src_type.equals("amc"))
                return true;
            else return false;
        }
    }
    public static class amcapiFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            JSONObject object = JSONObject.parseObject(sentence);
            JSONObject beat = object.getJSONObject("beat");
            String src_type=beat.getString("src_type");
            if(src_type.equals("amcapi"))
                return true;
            else return false;
        }
    }
    public static class apiFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("api");
        }
    }
    public static class apicoreFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("apicore");
        }
    }
    public static class apsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("aps");
        }
    }
    public static class bmcFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("bmc");
        }
    }
    public static class cdsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("cds");
        }
    }
    public static class cmcFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("cmc");
        }
    }
    public static class cmdataproxyFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("cmdataproxy");
        }
    }
    public static class cmuFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("cmu");
        }
    }
    public static class cssFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("css");
        }
    }
    public static class dcsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("dcs");
        }
    }
    public static class dmsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("dms");
        }
    }
    public static class dssmasterFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("dssmaster");
        }
    }
    public static class dssworkerFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("dssworker");
        }
    }
    public static class ejabberdFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("ejabberd");
        }
    }
    public static class glusterfsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("glusterfs");
        }
    }
    public static class glusterfsdFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("glusterfsd");
        }
    }
    public static class graphiteFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("graphite");
        }
    }
    public static class hduapiagentFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("hduapiagent");
        }
    }
    public static class hdupoolFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("hdupool");
        }
    }
    public static class mediamasterFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("media-master");
        }
    }
    public static class mediaworkerFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("media-worker");
        }
    }
    public static class modbFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("modb");
        }
    }
    public static class mysqlFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("mysql");
        }
    }
    public static class ndsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nds");
        }
    }
    public static class nmsbridge26Filter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nms_bridge26");
        }
    }
    public static class nmsbridge48Filter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nms_bridge48");
        }
    }
    public static class nmscollectorFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nms_collector");
        }
    }
    public static class pmsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("pms");
        }
    }
    public static class nmsstarterFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nms_starter");
        }
    }
    public static class nmswebserverFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("nms_webserver");
        }
    }
    public static class portalFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("portal");
        }
    }
    public static class portalcoreFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("portalcore");
        }
    }
    public static class prsworkerFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("prsworker");
        }
    }
    public static class rabbitmqFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("rabbitmq");
        }
    }

    public static class redisFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("redis");
        }
    }
    public static class redisnmsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("redis_nms");
        }
    }
    public static class restapiFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("restapi");
        }
    }
    public static class rmsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("rms");
        }
    }
    public static class serviceFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("service");
        }
    }
    public static class servicecoreFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("servicecore");
        }
    }
    public static class smFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("sm");
        }
    }
    public static class ssoFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("sso");
        }
    }
    public static class ssocoreFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("ssocore");
        }
    }
    public static class susFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("sus");
        }
    }
    public static class susmgrFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("susmgr");
        }
    }
    public static class tomcatFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("tomcat");
        }
    }
    public static class upuFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("upu");
        }
    }
    public static class upucoreFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("upucore");
        }
    }
    public static class vrsFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("vrs");
        }
    }
    public static class zookeeperFilter implements FilterFunction<String> {
        @Override
        public boolean filter(String sentence) throws Exception {
            String src_type=getSrcType(sentence);
            return src_type.equals("zookeeper");
        }
    }

    private static String getSrcType(String sentence){
        JSONObject object = JSONObject.parseObject(sentence);
        JSONObject beat = object.getJSONObject("beat");
        return beat.getString("src_type");
    }
}
