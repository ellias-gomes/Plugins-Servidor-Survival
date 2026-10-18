scoreboard players operation #cur aur_id = @s aur_id
execute as @e[tag=aur_part,tag=!aur_dying,distance=..30] if score @s aur_id = #cur aur_id run scoreboard players set @s aur_ttl 0
