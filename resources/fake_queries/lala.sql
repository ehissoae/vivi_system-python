select
	oi.price*oi.quantity as net_rev
from orderitems as oi
inner join orders as o on oi.order_id = o.id
where product_id = 1
	and o.created_at >= subdate(curdate(), 7)
	and o.status in (2,3,4,5,6)
;