SELECT
	pc.sku_config,
	pc.sale_price,
	-- pc.sale_price,
	"yay" as nothing,

	pc.gross_cost * (1 - pc.vat_in) as net_cost,
	case 
		when pc.is_private_label then "PL"
		when pc.is_crossdocking then "XDOC" 
		when 1+1=3 then "ERRO!"
		when 1+1=4 then concat("AINDA MAIS", " ERRO! ", "CASE WHEN ERRADO!!!")
		else "BR"
	end as yay,

	ps.sku_simple,
	-- ps.sku_simple,
	ps.size,
	/*
	ps.size,
	ps.size,
	ps.size,
	*/

	-- sem o 'as'
	CONCAT(pc.sku_config, "-", ps.size) as sku_plus_size
FROM star_schema.dim_product_config pc
INNER JOIN star_schema.dim_product_simple ps on ps.fk_product_config = pc.id_product_config
ORDER BY pc.sku_config
LIMIT 100
;



SELECT
	pc.sale_price,
	pc.sale_price as yay,
	pc.sale_price yay,

	"yay" as nothing,
	"yay" nothing,
	"yay",

	pc.gross_cost * (1 - pc.vat_in) as net_cost,
	pc.gross_cost * (1 - pc.vat_in) net_cost,
	pc.gross_cost * (1 - pc.vat_in),

	CONCAT(pc.sku_config, "-", ps.size) as sku_plus_size,
	CONCAT(pc.sku_config, "-", ps.size) sku_plus_size,
	CONCAT(pc.sku_config, "-", ps.size)
from star_schema.dim_product_config pc
INNER JOIN star_schema.dim_product_simple ps on ps.fk_product_config = pc.id_product_config
LIMIT 100
;


select 
    sa.name as select_alias,
    se.raw_expression as select_exp,
    tf.name as field,
    t.name as _table
from select_alias sa
inner join selectexpression_selectalias se_sa on se_sa.select_alias_id = sa.id
inner join select_expression se on se_sa.select_expression_id = se.id
inner join selectexpression_tablefields se_tf on se_tf.select_expression_id = se.id
inner join table_field tf on se_tf.table_field_id = tf.id
inner join table t on t.id = tf.table_id
;


select
	oi.price*oi.quantity as net_rev
from orderitems as oi
inner join orders as o on oi.order_id = o.id
where product_id = 1
	and o.created_at >= subdate(curdate(), 7)
	and o.status in (2,3,4,5,6)
;



/*
CONFIG
sku_config 
	-> pc.sku_config
		-> star_schema.dim_product_config (pc)
sale_price 
	-> pc.sale_price
		-> star_schema.dim_product_config (pc)
net_cost 
	-> pc.gross_cost * (1 - pc.vat_out)
		-> star_schema.dim_product_config (pc)

SIMPLE
sku_simple 
	-> ps.sku_simple
		-> star_schema.dim_product_simple (ps)
size 
	-> ps.size
		-> star_schema.dim_product_simple (ps)

MIXED
sku_plus_size
	-> CONCAT(pc.sku_config, '-', ps.size)
		-> star_schema.dim_product_config (pc)
		-> star_schema.dim_product_simple (ps)




fields = {
	'field1': [
		{
			# usar alias (pc/ps) ou o nome inteirno da tabela?
			# pra mostrar pro usuario o nome inteiro pode ser muito grande 
			# mas ao mesmo tempo pode ser confuso nao saber qual tabela aquele alias se refere 
			'expression': "CONCAT(pc.sku_config, '-', ps.size)",
			'tables': set(
				('star_schema.dim_product_config', 'pc'),
				('star_schema.dim_product_simple', 'ps'),
			),
			'joins': [
				set('ps.fk_product_config', 'pc.id_product_config'),
			]
		},
	],	
}


*/
