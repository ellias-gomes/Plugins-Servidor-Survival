tag @s add aur_base
scoreboard players add #next aur_id 1
scoreboard players operation @s aur_id = #next aur_id
scoreboard players set @s aur_model 10
scoreboard players set @s aur_ph 0
scoreboard players set @s aur_cyc 0
scoreboard players set @s aur_hold 0
scoreboard players set @s aur_anim 0
scoreboard players set @s aur_px 0
scoreboard players set @s aur_pz 0
effect give @s minecraft:invisibility infinite 0 true
attribute @s minecraft:scale base set 2.2
item replace entity @s weapon.mainhand with minecraft:air
item replace entity @s weapon.offhand with minecraft:air
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_raiz_tronco"],block_state:"minecraft:oak_log",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.4500f,0.0000f,-0.4500f],scale:[0.9000f,2.4000f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_raiz_raizes"],block_state:"minecraft:mangrove_roots",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.7500f,0.0000f,-0.7500f],scale:[1.5000f,0.4000f,1.5000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_raiz_copa"],block_state:"minecraft:azalea_leaves",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.7500f,2.3000f,-0.7500f],scale:[1.5000f,1.0000f,1.5000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_raiz_seiva"],block_state:"minecraft:verdant_froglight",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.1500f,1.1500f,0.4100f],scale:[0.3000f,0.9000f,0.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_raiz_seiva_t"],block_state:"minecraft:verdant_froglight",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.1500f,1.1500f,-0.5100f],scale:[0.3000f,0.9000f,0.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
execute as @e[tag=aur_new,distance=..3] run function aurelion:attach_fin
