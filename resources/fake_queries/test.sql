SELECT
	pc.sku_config,
	pc.sale_price,
	-- pc.sale_price,
	"yay" as nothing,

	pc.gross_cost * (1 - pc.vat_out) as net_cost,
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

	pc.gross_cost * (1 - pc.vat_out) as net_cost,
	pc.gross_cost * (1 - pc.vat_out) net_cost,
	pc.gross_cost * (1 - pc.vat_out),

	CONCAT(pc.sku_config, "-", ps.size) as sku_plus_size,
	CONCAT(pc.sku_config, "-", ps.size) sku_plus_size,
	CONCAT(pc.sku_config, "-", ps.size)
from star_schema.dim_product_config pc
INNER JOIN star_schema.dim_product_simple ps on ps.fk_product_config = pc.id_product_config
LIMIT 100


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
