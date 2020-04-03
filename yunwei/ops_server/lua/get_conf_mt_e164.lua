local conf_e164s = redis.call("SMEMBERS", "confs")
local keys = {}
for i, conf_e164 in ipairs(conf_e164s)
do
    local conf_name = redis.call("hget", string.format("conf/%s", conf_e164), "confname")
    keys[conf_e164] = { conf_name }
    local key = redis.call("hkeys", string.format("conf/%s/e164tomtid", conf_e164))
    local index = 2
    for ii, mt_e164 in ipairs(key)
    do
        local mtid = redis.call("hget", string.format("conf/%s/e164tomtid", conf_e164), mt_e164)
        local is_online = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mtid), 'online')
        if is_online == '1' then
            keys[conf_e164][index] = mt_e164
            index = index + 1
        end
    end
end
keys = cjson.encode(keys)
return keys
