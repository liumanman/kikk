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



select
source_id
,item_id
,tracking_number
,shipping_full_addr
from "order" as a
inner join "tracking_number" as b
on a.order_id=b.order_id
where a.status='S'
