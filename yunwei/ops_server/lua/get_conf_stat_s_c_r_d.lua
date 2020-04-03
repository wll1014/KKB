-- query conf  cmu_ip/speaker/chairman/dualstream/recs

local conf_e164s = ARGV   -- args
local results = {}
local paths = {"speaker", "chairman", "dualstream", "recs"}  -- check path

for i, conf_e164 in ipairs(conf_e164s)  -- single conf loop
do
    local conf_info = {}
    if redis.call("EXISTS", string.format("conf/%s", conf_e164)) == 1 then

         -- cmu_ip
        local cmu_ip = ""
        if redis.call("EXISTS", string.format("confex/%s", conf_e164)) == 1 then
            cmu_ip = redis.call("hget", string.format("confex/%s", conf_e164), "cmu")
        end
        table.insert(conf_info, cmu_ip)

        for j, path in ipairs(paths)  -- path loop
        do
            local mt_id = ""
            if redis.call("EXISTS", string.format("conf/%s/%s", conf_e164, path)) == 1 then
                if path == "recs" then
                    -- recorder
                    local recs = redis.call("SMEMBERS", string.format("conf/%s/%s", conf_e164, path))
                    local recs_stat = {}
                    for j,rec in ipairs(recs)
                    do
                        local rec_stat = redis.call("hget", string.format("conf/%s/rec/%s", conf_e164, rec), "recmode")
                        if rec_stat == nil then
                            table.insert(recs_stat, "")
                        else
                            table.insert(recs_stat, rec_stat)
                        end
                    end
                    table.insert(conf_info, recs_stat)
                else
                    -- other
                    mt_id = redis.call("hget", string.format("conf/%s/%s", conf_e164, path), "mtid")
                    local mt_alias = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "mtalias")
                    if mt_alias == nil then
                        local mt_e164 = redis.call("hget", string.format("conf/%s/mt/%s", conf_e164, mt_id), "e164")
                        table.insert(conf_info, mt_e164)
                    else
                        table.insert(conf_info, mt_alias)
                    end
                end
            else
                table.insert(conf_info, mt_id)
            end
        end
    end
    table.insert(results, conf_info)
end
return results


