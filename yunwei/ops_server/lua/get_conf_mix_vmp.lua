-- query conf mix/vmp information from redis

local conf_e164s = ARGV   -- args
local results = {}
local paths = {"vmp/1", "mix/1"}  -- check path

for i, conf_e164 in ipairs(conf_e164s)  -- single conf loop
do
    local conf_info = {}
    for j, path in ipairs(paths)  -- path loop
    do
        local single = {}

        local stat = ""
        local mode = ""
        local mts = {}

        if redis.call("EXISTS", string.format("conf/%s/%s", conf_e164, path)) == 1 then
            stat = "1"
            if path == "vmp/1" then
                -- vmp
                mode = redis.call("hget", string.format("conf/%s/%s", conf_e164, path), "mode")
                local mt_nums = redis.call("hget", string.format("conf/%s/%s", conf_e164, path), "chnnum")
                for k=0,mt_nums do
                    if redis.call("EXISTS", string.format("conf/%s/%s/channel/%s", conf_e164, path, k)) == 1 then
                        local mt_id = redis.call("hget", string.format("conf/%s/%s/channel/%s", conf_e164, path, k), "mtid")
                        if mt_id ~= "" then
                            local mt164 = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "e164")
                            local mtalias = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "mtalias")
                            table.insert(mts, mt164)
                            table.insert(mts, mtalias)
                        end
                    end
                end
            else
                -- mix
                mode = redis.call("hget", string.format("conf/%s/%s", conf_e164, path), "mixmode")
                if mode == "2" then  -- custom
                    local mt_nums = redis.call("hget", string.format("conf/%s/%s", conf_e164, path), "mtnum")
                    for k=0,mt_nums do
                        if redis.call("EXISTS", string.format("conf/%s/%s/member/%s", conf_e164, path, k)) == 1 then
                            local mt_id = redis.call("hget", string.format("conf/%s/%s/member/%s", conf_e164, path, k), "mtid")
                            local mt164 = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "e164")
                            local mtalias = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "mtalias")
                            table.insert(mts, mt164)
                            table.insert(mts, mtalias)
                        end
                    end
                end
            end
        else
            stat = "0"
        end
        table.insert(single, stat)
        table.insert(single, mode)
        table.insert(single, mts)

        table.insert(conf_info, single)
    end
    table.insert(results, conf_info)
end

return results