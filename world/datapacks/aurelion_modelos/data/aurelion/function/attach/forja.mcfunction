tag @s add aur_base
scoreboard players add #next aur_id 1
scoreboard players operation @s aur_id = #next aur_id
scoreboard players set @s aur_model 11
scoreboard players set @s aur_ph 0
scoreboard players set @s aur_cyc 0
scoreboard players set @s aur_hold 0
scoreboard players set @s aur_anim 0
scoreboard players set @s aur_px 0
scoreboard players set @s aur_pz 0
effect give @s minecraft:invisibility infinite 0 true
attribute @s minecraft:scale base set 1.4
item replace entity @s weapon.mainhand with minecraft:air
item replace entity @s weapon.offhand with minecraft:air
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_forja_base"],block_state:"minecraft:magma_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-1.0000f,0.0000f,-1.0000f],scale:[2.0000f,0.6000f,2.0000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_forja_fornalha"],block_state:"minecraft:blast_furnace",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.9000f,0.6000f,-0.9000f],scale:[1.8000f,1.6000f,1.8000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_forja_chamine"],block_state:"minecraft:polished_blackstone_bricks",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[0.2500f,2.1000f,-0.6500f],scale:[0.5000f,1.2000f,0.5000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_forja_brasa"],block_state:"minecraft:shroomlight",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.4500f,2.3500f,-0.4500f],scale:[0.9000f,0.2000f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_forja_bigorna"],block_state:"minecraft:iron_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.3000f,2.5750f,-0.2500f],scale:[0.6000f,0.3500f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
execute as @e[tag=aur_new,distance=..3] run function aurelion:attach_fin
