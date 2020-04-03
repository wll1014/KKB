-- query real_conf mts from redis
-- return mt informations

local conf_id = ARGV[1]
local start_time = ARGV[2]
local conf_info = {}

if redis.call("EXISTS", string.format("conf/%s", conf_id)) == 1 then
    local st = redis.call("HGET", string.format("conf/%s", conf_id), "starttime")
    if st ~= start_time then
        return conf_info
    end

    local conf_mts = redis.call("SMEMBERS", string.format("conf/%s/mts", conf_id))
    for i, mt_num in ipairs(conf_mts) do
        if redis.call("EXISTS", string.format("conf/%s/mt/%s", conf_id, mt_num)) == 1 then
            local is_online = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "online")
            -- if is_online == '1' then
            local mt_info = {}
            local e164 = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "e164")
            local mtalias = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mtalias")
            local mtip = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mtip")
            local mttype = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "mttype")
            local bitrate = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "bitrate")
            local protocol = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "protocol")
            local productid = redis.call("HGET",string.format("conf/%s/mt/%s", conf_id, mt_num), "productid")
            table.insert(mt_info, e164)
            table.insert(mt_info, mtalias)
            table.insert(mt_info, mtip)
            table.insert(mt_info, mttype)
            table.insert(mt_info, bitrate)
            table.insert(mt_info, protocol)
            table.insert(mt_info, productid)
            table.insert(mt_info, is_online)

            table.insert(conf_info, mt_info)
        end
    end
end
return conf_info
