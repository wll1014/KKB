package com.kedacom.ops.flink;

import com.kedacom.ops.flink.etl.DssPbEtl;
import com.kedacom.ops.flink.agg.DssSwitchAgg;

public class MediaSwitchMain {
    public static void main(String[] args) throws Exception {
        System.out.println(args[0]);
        if(args[0].equals("etl"))
            DssPbEtl.dssetl();
        else if(args[0].equals("agg")) {
            DssSwitchAgg.dssswitchagg();
        }
        else
        {}
    }
}
