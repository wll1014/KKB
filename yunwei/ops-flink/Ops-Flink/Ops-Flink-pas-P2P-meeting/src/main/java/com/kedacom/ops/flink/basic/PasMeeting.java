package com.kedacom.ops.flink.basic;

public class PasMeeting {
    private String caller;
    private String callee;
    private Long createtime;
    public PasMeeting(String caller,String callee, Long createtime){
        this.caller=caller;
        this.callee=callee;
        this.createtime=createtime;
    }
    public PasMeeting(){

    }
    public String getCallee() {
        return callee;
    }
    public void setCallee(String callee) {
        this.callee = callee;
    }
    public String getCaller(){
        return caller;
    }
    public void setCaller(String caller){
        this.caller=caller;
    }
    public void setCreatetime(Long createtime){
        this.createtime=createtime;
    }
    public Long getCreatetime(){
        return createtime;
    }

    public boolean equals(PasMeeting pasmeeting){
        if(this.caller.equals(pasmeeting.getCaller()) && this.callee.equals(pasmeeting.getCallee()))
            return true;
        else
            return false;
    }

}
