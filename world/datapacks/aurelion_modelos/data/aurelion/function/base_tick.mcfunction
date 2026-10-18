# executado AS base AT @s, todo tick
execute if data entity @s {Health:0.0f} run return run function aurelion:base_dead
scoreboard players operation #cur aur_id = @s aur_id
execute as @e[tag=aur_part,tag=!aur_dying,distance=..30] if score @s aur_id = #cur aur_id run function aurelion:part_follow
# detecção de movimento (centésimos de bloco por tick)
execute store result score #nx aur_tmp run data get entity @s Pos[0] 100
execute store result score #nz aur_tmp run data get entity @s Pos[2] 100
scoreboard players operation #dx aur_tmp = #nx aur_tmp
scoreboard players operation #dx aur_tmp -= @s aur_px
scoreboard players operation #dz aur_tmp = #nz aur_tmp
scoreboard players operation #dz aur_tmp -= @s aur_pz
scoreboard players operation @s aur_px = #nx aur_tmp
scoreboard players operation @s aur_pz = #nz aur_tmp
scoreboard players set #mv aur_tmp 0
execute if score #dx aur_tmp matches 3.. run scoreboard players set #mv aur_tmp 1
execute if score #dx aur_tmp matches ..-3 run scoreboard players set #mv aur_tmp 1
execute if score #dz aur_tmp matches 3.. run scoreboard players set #mv aur_tmp 1
execute if score #dz aur_tmp matches ..-3 run scoreboard players set #mv aur_tmp 1
# dano recebido -> pose "hurt" (se nenhuma animação em curso)
execute if data entity @s {HurtTime:10s} unless score @s aur_hold matches 1.. unless score @s aur_anim matches 4.. run scoreboard players set @s aur_anim 6
execute if score @s aur_anim matches 4.. run function aurelion:base_anim
execute if score @s aur_hold matches 1.. run scoreboard players remove @s aur_hold 1
execute if score @s aur_hold matches 0 run function aurelion:base_cycle
