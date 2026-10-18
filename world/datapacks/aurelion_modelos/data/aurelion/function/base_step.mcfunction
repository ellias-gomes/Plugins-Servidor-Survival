scoreboard players set @s aur_cyc 0
scoreboard players set #t aur_tmp 0
execute if score @s aur_ph matches 0 run scoreboard players set #t aur_tmp 1
scoreboard players operation @s aur_ph = #t aur_tmp
scoreboard players set #pose aur_tmp 0
execute if score #mv aur_tmp matches 1 run scoreboard players set #pose aur_tmp 2
scoreboard players operation #pose aur_tmp += @s aur_ph
function aurelion:dispatch
