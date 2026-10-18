tag @s add aur_base
scoreboard players add #next aur_id 1
scoreboard players operation @s aur_id = #next aur_id
scoreboard players set @s aur_model 12
scoreboard players set @s aur_ph 0
scoreboard players set @s aur_cyc 0
scoreboard players set @s aur_hold 0
scoreboard players set @s aur_anim 0
scoreboard players set @s aur_px 0
scoreboard players set @s aur_pz 0
effect give @s minecraft:invisibility infinite 0 true
attribute @s minecraft:scale base set 2.0
item replace entity @s weapon.mainhand with minecraft:air
item replace entity @s weapon.offhand with minecraft:air
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_coluna"],block_state:"minecraft:obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.4500f,0.0000f,-0.4500f],scale:[0.9000f,2.8000f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_topo"],block_state:"minecraft:crying_obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.6000f,2.7500f,-0.6000f],scale:[1.2000f,0.3000f,1.2000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_cristal"],block_state:"minecraft:amethyst_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.3500f,3.4500f,-0.3500f],scale:[0.7000f,0.7000f,0.7000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_orbita0"],block_state:"minecraft:crying_obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.0900f,3.7100f,0.8100f],scale:[0.1800f,0.1800f,0.1800f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_orbita1"],block_state:"minecraft:crying_obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[0.8100f,3.7100f,-0.0900f],scale:[0.1800f,0.1800f,0.1800f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_orbita2"],block_state:"minecraft:crying_obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.0900f,3.7100f,-0.9900f],scale:[0.1800f,0.1800f,0.1800f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_pilar_vazio_orbita3"],block_state:"minecraft:crying_obsidian",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.9900f,3.7100f,-0.0900f],scale:[0.1800f,0.1800f,0.1800f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
execute as @e[tag=aur_new,distance=..3] run function aurelion:attach_fin
