connect inet://localhost/mytest user sysdba password 521000;
delete from item;
insert into item
(
	item_id
	,description
	,cost
	,shipping_cost
	,image_url
	,product_url
)
select 
	'T501WHX'
	,'JanSport SuperBreak School Backpack - White'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_WHX_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-white.html'
union all
select
	'T50109P'
	,'JanSport SuperBreak School Backpack - RED NEW CALIFORNIA REPUBLIC'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_09P_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-red-new-california-republic.html'
union all
select
	'T501ZQ1'
	,'JanSport SuperBreak School Backpack - Multi/Blue Drip Dye'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_ZQ1_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-blue-drip-dye.html'
union all
select
	'T501ZK1'
	,'JanSport SuperBreak School Backpack - SHADY GREY SPRINKLED FLORAL'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_ZK1_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-shady-grey-sprinkled-floral.html'
union all
select
	'TDN701H'
	,'JanSport Big Student School Backpack - SPANISH TEAL'
	,2500
	,690
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/TDN7001H01.jpg'
	,'http://www.fantasyard.com/jansport-big-student-school-backpack-spanish-teal.html'
union all
select
	'T50109Z'
	,'JanSport SuperBreak School Backpack - BLACK ELE FANCY'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_09Z_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-black-ele-fancy.html'
union all
select
	'TYP701E'
	,'JanSport RIGHT PACK BACKPACK - ORANGE GOLD'
	,2500
	,690
	,'https://www.fantasyard.com/images/thumbnails/14/100/100/TYP7_01E_front.jpg'
	,'http://www.fantasyard.com/jansport-right-pack-backpack-orange-gold.html'
union all
select 
	'T5010DU'
	,'JanSport SuperBreak School Backpack - Multi Painted Ditzy'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/T501_0DU_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-painted-ditzy.html'
union all
select
	'T50102K'
	,'JanSport SuperBreak School Backpack - NAVY SUPER STRIPE'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/11/100/100/T501_02K_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-navy-super-stripe.html'
union all
select
	'T5010EG'
	,'JanSport SuperBreak School Backpack - CYBER PINK BLOCK FLORAL'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/T501_0EG_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-cyber-pink-block-floral.html'
union all
select
	'T50102C'
	,'JanSport SuperBreak School Backpack - Purple Night Color Ombre'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/11/100/100/T501_02C_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-purple-night-color-ombre.html'
union all
select
	'TDN70EK'
	,'JanSport Big Student School Backpack - BLACK/WHITE BEBOP'
	,2800
	,750
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/TDN70EK-1.jpg'
	,'http://www.fantasyard.com/jansport-big-student-school-backpack-black-white-bebop.html'
union all
select
	'T50109Y'
	,'JanSport SuperBreak School Backpack - MULTI DONUTS'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_09Y_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-donuts.html'
union all
select
	'T5010DS'
	,'JanSport SuperBreak School Backpack - NAVY MOONSHINE ISLAND OMBRE'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/16/100/100/T501_0DS_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-navy-moonshine-island-ombre.html'
union all
select
	'T5010C6'
	,'JanSport SuperBreak School Backpack - AQUA DASH ZOU BISOU'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_0C6_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-aqua-dash-zou-bisou.html'
union all
select
	'T501003'
	,'JanSport SuperBreak School Backpack - Navy'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_003_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-navy.html'
union all
select	
	'T50101Z'
	,'JanSport SuperBreak School Backpack - CORAL DUSK TRIBAL MOSAICo'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/14/100/100/T501_01Z_front.jpg'
	,'JanSport SuperBreak School Backpack - CORAL DUSK TRIBAL MOSAIC'
union all
select
	'T5010BE'
	,'JanSport SuperBreak School Backpack - GREY RABBIT SYLVIA DOT'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_0BE_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-grey-rabbit-sylvia-dot.html'
union all
select
	'T5010D5'
	,'JanSport SuperBreak School Backpack - Tahitian Orange'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/T501_0D5_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-tahitian-orange.html'
union all
select
	'T5010E2'
	,'Jansport Superbreak Backpack- Multi Navy Mountain Meadow'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/718W739H3tL._SL1200_.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-backpack-multi-navy-mountain-meadow.html'
union all
select
	'T5010K6'
	,'JanSport SuperBreak School Backpack - Navy Night Sky'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/T501_0K6_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-navy-night-sky.html'	
union all
select
	'T5010L2'
	,'Jansport Superbreak Backpack- Multi Wet Sloth'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/wet_sloth_front_.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-backpack-multi-wet-sloth.html'
union all
select
	'T5011Q4'
	,'JanSport SuperBreak School Backpack - FLUORESCENT RED'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/11/100/100/T5011Q4-1.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-fluorescent-red.html'
union all
select
	'T5012D5'
	,'JanSport SuperBreak School Backpack - Lorac Yellow'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_2D5_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-lorac-yellow.html'
union all
select
	'T5016XD'
	,'JanSport SuperBreak School Backpack - Forge Grey'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_6XD_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-forge-grey.html'
union all
select
	'T5019ZG'
	,'JanSport SuperBreak School Backpack - Aqua Dash'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/11/100/100/T501_9ZG_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-aqua-dash.html'
union all
select
	'T50F5CS'
	,'JanSport DIGIBREAK BACKPACK - BLUE STREAK'
	,0
	,0
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T50F_5CS_front.jpg'
	,'http://www.fantasyard.com/jansport-digibreak-backpack-blue-streak.html'
union all
select
	'TAN19RX'
	,'JanSport FIFTH AVENUE WAISTPACK - FLUORESCENT PINK'
	,0
	,0
	,'https://www.fantasyard.com/images/thumbnails/13/100/100/TAN1_9RX_front.jpg'
	,'http://www.fantasyard.com/jansport-fifth-ave-waistpack-fluorescent-pink.html'
union all
select
	'TDN70E9'
	,'JanSport Big Student School Backpack - MULTI SUNSET STRIPE'
	,0
	,0
	,'https://www.fantasyard.com/images/thumbnails/17/100/100/TDN70E9-1.jpg'
	,'http://www.fantasyard.com/jansport-big-student-school-backpack-multi-sunset-stripe.html'
union all
select
	'T26L9ER'	
	,'JanSport ALL PURPOSE Backpack - BLUE WASH'
	,0
	,0
	,'https://www.fantasyard.com/images/thumbnails/13/100/100/T26L_9ER_front.jpg'
	,'http://www.fantasyard.com/jansport-all-purpose-backpack-blue-wash.html'
union all
select
	'T50109N'
	,'JanSport SuperBreak School Backpack - MULTI MIXTAPES'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_09N_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-mixtapes.html'
union all
select
	'T5010A1'
	,'JanSport SuperBreak School Backpack - MULTI GREY FLORAL FLOURISH'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_0A1_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-grey-floral-flourish.html'
union all
select
	'T5010AA'
	,'JanSport SuperBreak School Backpack - BLACK LUCKY DAISY'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_0AA_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-black-lucky-daisy.html'
union all
select
	'T5010AD'
	,'JanSport SuperBreak School Backpack - MULTI PURPLE OMBRE DAISY'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/15/100/100/T501_0AD_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-multi-purple-ombre-daisy.html'
union all
select
	'T5015KS'
	,'JanSport SuperBreak School Backpack - High Risk Red'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_5KS_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-high-risk-red.html'
union all
select
	'T5019FL'
	,'JanSport SuperBreak School Backpack - Viking Red'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_9FL_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-viking-red.html'
union all
	'T5019RW'
	,'JanSport SuperBreak School Backpack - Mammoth Blue'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_9RW_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-mammoth-blue.html'
union all
	'T5019RX'
	,'JanSport SuperBreak School Backpack - Fluorescent Pink'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_9RX_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-fluorescent-pink.html'
union all
	'T5019SA'
	,'JanSport SuperBreak School Backpack - Coral Peaches'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/12/100/100/T501_9SA_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-coral-peaches.html'
union all
	'T501ZE6'
	,'JanSport SuperBreak School Backpack - GREY TAR WILD AT HEART'
	,1900
	,350
	,'https://www.fantasyard.com/images/thumbnails/11/100/100/T501_ZE6_front.jpg'
	,'http://www.fantasyard.com/jansport-superbreak-school-backpack-grey-tar-wild-at-heart.html';


