local e164 = ARGV[1]

-- 遍历数组
local function IsInTable(value, tbl)
for k,v in ipairs(tbl) do
  if v == value then
  return true;
  end
end
return false;
end

local confs = redis.call("SMEMBERS", "confs")
for count, conf_e164 in ipairs(confs)
    do
    if redis.call("EXISTS", string.format("conf/%s/e164tomtid", conf_e164)) then
        local conf_mts = redis.call("HKEYS", string.format("conf/%s/e164tomtid", conf_e164))
        if IsInTable(e164, conf_mts) then

            return conf_e164
        end
    end
end
return ""
