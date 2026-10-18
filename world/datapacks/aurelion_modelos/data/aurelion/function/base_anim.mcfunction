scoreboard players operation #pose aur_tmp = @s aur_anim
scoreboard players set @s aur_anim 0
scoreboard players set @s aur_hold 16
execute if score #pose aur_tmp matches 6 run scoreboard players set @s aur_hold 5
scoreboard players set @s aur_cyc 10
function aurelion:dispatch
