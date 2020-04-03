package com.kedacom.ops.flink;

import com.kedacom.ops.flink.PasP2PMeetingInfo;
import com.kedacom.ops.flink.PasP2PMeetingAgg;

public class PasP2PMeetingMain {
    public static void main(String[] args) throws Exception {
        System.out.println(args[0]);
        if(args[0].equals("pasmeetinginfo"))
            PasP2PMeetingInfo.writeP2PMeetingList();
        else if(args[0].equals("pasmeetingagg"))
            PasP2PMeetingAgg.pasP2PMeetingAgg();
        else
        {}
    }
}
