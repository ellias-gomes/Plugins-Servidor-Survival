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
scoreboard objectives add aur_phase dummy
scoreboard objectives add aur_shield dummy
execute unless score #next aur_id matches 0.. run scoreboard players set #next aur_id 0
gamerule send_command_feedback false
gamerule command_block_output false
bossbar add aurelion:boss_1 "§a§lVerdelith, o Guardião do Musgo"
bossbar set aurelion:boss_1 color green
bossbar set aurelion:boss_1 style notched_10
bossbar set aurelion:boss_1 visible false
bossbar add aurelion:boss_2 "§b§lThalassa, Rainha das Marés"
bossbar set aurelion:boss_2 color blue
bossbar set aurelion:boss_2 style notched_10
bossbar set aurelion:boss_2 visible false
bossbar add aurelion:boss_3 "§c§lKorvan, o Ferreiro Caído"
bossbar set aurelion:boss_3 color red
bossbar set aurelion:boss_3 style notched_10
bossbar set aurelion:boss_3 visible false
bossbar add aurelion:boss_4 "§d§lSeraphel, o Oráculo Quebrado"
bossbar set aurelion:boss_4 color pink
bossbar set aurelion:boss_4 style notched_10
bossbar set aurelion:boss_4 visible false
bossbar add aurelion:boss_5 "§5§lO Eclipse"
bossbar set aurelion:boss_5 color purple
bossbar set aurelion:boss_5 style notched_20
bossbar set aurelion:boss_5 visible false
bossbar add aurelion:semi_1 "§c§l⚔ Thorgar, o Carniceiro dos Ermos"
bossbar set aurelion:semi_1 color red
bossbar set aurelion:semi_1 style notched_6
bossbar set aurelion:semi_1 visible false
bossbar add aurelion:semi_2 "§9§l☠ Morvath, o Necromante da Cripta"
bossbar set aurelion:semi_2 color blue
bossbar set aurelion:semi_2 style notched_6
bossbar set aurelion:semi_2 visible false
bossbar add aurelion:semi_3 "§6§l⛰ Gólem Esquecido de Basalto"
bossbar set aurelion:semi_3 color yellow
bossbar set aurelion:semi_3 style notched_6
bossbar set aurelion:semi_3 visible false
bossbar add aurelion:semi_4 "§5§l🗡 Valeria, a Lâmina Sombria"
bossbar set aurelion:semi_4 color purple
bossbar set aurelion:semi_4 style notched_6
bossbar set aurelion:semi_4 visible false
