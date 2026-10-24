execute as @e[tag=aur_base] at @s run function aurelion:base_tick
execute as @e[tag=aur_part,tag=!aur_dying] run function aurelion:part_tick
execute as @e[tag=aur_part,tag=aur_dying] run function aurelion:part_dying
execute unless entity @e[tag=aur_base,scores={aur_model=1}] run bossbar set aurelion:boss_1 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=1}] run bossbar set aurelion:boss_1 players
execute unless entity @e[tag=aur_base,scores={aur_model=2}] run bossbar set aurelion:boss_2 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=2}] run bossbar set aurelion:boss_2 players
execute unless entity @e[tag=aur_base,scores={aur_model=3}] run bossbar set aurelion:boss_3 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=3}] run bossbar set aurelion:boss_3 players
execute unless entity @e[tag=aur_base,scores={aur_model=4}] run bossbar set aurelion:boss_4 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=4}] run bossbar set aurelion:boss_4 players
execute unless entity @e[tag=aur_base,scores={aur_model=5}] run bossbar set aurelion:boss_5 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=5}] run bossbar set aurelion:boss_5 players
execute unless entity @e[tag=aur_base,scores={aur_model=6}] run bossbar set aurelion:semi_1 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=6}] run bossbar set aurelion:semi_1 players
execute unless entity @e[tag=aur_base,scores={aur_model=7}] run bossbar set aurelion:semi_2 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=7}] run bossbar set aurelion:semi_2 players
execute unless entity @e[tag=aur_base,scores={aur_model=8}] run bossbar set aurelion:semi_3 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=8}] run bossbar set aurelion:semi_3 players
execute unless entity @e[tag=aur_base,scores={aur_model=9}] run bossbar set aurelion:semi_4 visible false
execute unless entity @e[tag=aur_base,scores={aur_model=9}] run bossbar set aurelion:semi_4 players
