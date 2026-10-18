scoreboard objectives add aur_id dummy
scoreboard objectives add aur_model dummy
scoreboard objectives add aur_ph dummy
scoreboard objectives add aur_cyc dummy
scoreboard objectives add aur_hold dummy
scoreboard objectives add aur_anim dummy
scoreboard objectives add aur_ttl dummy
scoreboard objectives add aur_px dummy
scoreboard objectives add aur_pz dummy
scoreboard objectives add aur_tmp dummy
execute unless score #next aur_id matches 0.. run scoreboard players set #next aur_id 0
gamerule send_command_feedback false
gamerule command_block_output false
