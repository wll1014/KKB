-- query real_time conf_id and mts_mttype

local confs = {}

local conf_e164s = redis.call("SMEMBERS","confs")
for i,conf_e164 in ipairs(conf_e164s)
do
    local conf = {}
    table.insert(conf, conf_e164)
    local start_time = redis.call("hget",string.format("conf/%s", conf_e164), "starttime")
    table.insert(conf, start_time)
    local mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_e164))
    for ii, id in ipairs(mts)
    do
        local mt_id = redis.call("hget",string.format("conf/%s/mt/%s", conf_e164, id), "e164")
        local mt_type = redis.call("hget",string.format("conf/%s/mt/%s", conf_e164, id),"mttype")
        table.insert(conf, mt_id)
        table.insert(conf, mt_type)
    end
    table.insert(confs, conf)
end
return confs
