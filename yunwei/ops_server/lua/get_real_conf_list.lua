-- query real_conf list from redis
-- return conf_id and start_time/creatormoid

local domain_moid = ARGV[1]
local conf_type = ARGV[2]
local conf_e164s = redis.call("SMEMBERS", "confs")
local confs_info = {}

for count, conf_e164 in ipairs(conf_e164s)
    do
    if redis.call("EXISTS", string.format("conf/%s", conf_e164)) then
        local is_domain = true
        local moid = redis.call("hget", string.format("conf/%s", conf_e164), "moid")
        if domain_moid ~= "" then
            if moid ~= domain_moid then
                is_domain = false
            end
        end
        if conf_type ~= "" then
            local conftype = redis.call("hget", string.format("conf/%s", conf_e164), "conftype")
            if conftype ~= conf_type then
                is_domain = false
            end
        end

        if is_domain == true then
            local conf_info = {}
            local start_time = redis.call("hget", string.format("conf/%s", conf_e164), "starttime")
            --local creatormoid = redis.call("hget", string.format("conf/%s", conf_e164), "creatormoid")
            table.insert(conf_info, conf_e164)
            table.insert(conf_info, start_time)
            table.insert(conf_info, moid)
            table.insert(confs_info, conf_info)
        end
    end
    end
return confs_info
