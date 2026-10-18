execute as @e[tag=aur_base] at @s run function aurelion:base_tick
execute as @e[tag=aur_part,tag=!aur_dying] run function aurelion:part_tick
execute as @e[tag=aur_part,tag=aur_dying] run function aurelion:part_dying
