package com.kedacom.ops.flink;

import com.kedacom.ops.flink.etl.H323Etl;
import com.kedacom.ops.flink.agg.H323Agg;

public class H323Main {
    public static void main(String[] args) throws Exception {
        System.out.println(args[0]);
        if(args[0].equals("etl"))
            H323Etl.etl();
        else if(args[0].equals("agg"))
            H323Agg.agg();
        else
        {}
    }
}
