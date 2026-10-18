tag @s add aur_base
scoreboard players add #next aur_id 1
scoreboard players operation @s aur_id = #next aur_id
scoreboard players set @s aur_model 8
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
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_torso"],block_state:"minecraft:basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-1.2000f,1.6000f,-0.8000f],scale:[2.4000f,2.2000f,1.6000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_nucleo"],block_state:"minecraft:magma_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.5000f,2.2000f,0.7900f],scale:[1.0000f,1.0000f,0.1200f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_rachadura1"],block_state:"minecraft:magma_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.8000f,2.9500f,0.7800f],scale:[0.2000f,0.7000f,0.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_rachadura2"],block_state:"minecraft:magma_block",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[0.7000f,1.8000f,0.7800f],scale:[0.2000f,0.8000f,0.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_head"],block_state:"minecraft:smooth_basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.5500f,3.8500f,-0.4500f],scale:[1.1000f,0.9000f,1.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_olho"],block_state:"minecraft:shroomlight",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.3500f,4.2800f,0.6300f],scale:[0.7000f,0.1400f,0.0800f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f,brightness:{block:15,sky:15}}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_cristal_a"],block_state:"minecraft:amethyst_block",transformation:{left_rotation:[0.0000f,0.0000f,0.1305f,0.9914f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-0.7414f,3.5748f,-0.7500f],scale:[0.3000f,0.8000f,0.3000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_cristal_b"],block_state:"minecraft:amethyst_block",transformation:{left_rotation:[0.0000f,0.0000f,-0.1305f,0.9914f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[0.3257f,3.7559f,-0.7500f],scale:[0.3000f,1.0000f,0.3000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_braco_l"],block_state:"minecraft:basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-2.0500f,1.1000f,-0.4500f],scale:[0.9000f,2.4000f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_punho_l"],block_state:"minecraft:smooth_basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-2.2000f,0.5000f,-0.6000f],scale:[1.2000f,1.0000f,1.2000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_perna_l"],block_state:"minecraft:smooth_basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[-1.1500f,0.0000f,-0.5500f],scale:[1.0000f,1.7000f,1.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_braco_r"],block_state:"minecraft:basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[1.1500f,1.1000f,-0.4500f],scale:[0.9000f,2.4000f,0.9000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_punho_r"],block_state:"minecraft:smooth_basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[1.0000f,0.5000f,-0.6000f],scale:[1.2000f,1.0000f,1.2000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
summon minecraft:block_display ~ ~ ~ {Tags:["aur_part","aur_new","aur_golem_perna_r"],block_state:"minecraft:smooth_basalt",transformation:{left_rotation:[0.0000f,0.0000f,0.0000f,1.0000f],right_rotation:[0.0f,0.0f,0.0f,1.0f],translation:[0.1500f,0.0000f,-0.5500f],scale:[1.0000f,1.7000f,1.1000f]},teleport_duration:2,interpolation_duration:0,view_range:2.0f}
execute as @e[tag=aur_new,distance=..3] run function aurelion:attach_fin
