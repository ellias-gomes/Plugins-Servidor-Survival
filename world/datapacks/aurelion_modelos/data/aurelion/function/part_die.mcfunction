tag @s add aur_dying
scoreboard players set @s aur_ttl 24
data merge entity @s {start_interpolation:0,interpolation_duration:20,transformation:{scale:[0.0f,0.0f,0.0f]}}
particle minecraft:poof ~ ~ ~ 0.3 0.3 0.3 0.02 4
