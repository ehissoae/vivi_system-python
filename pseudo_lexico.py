#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import session, SelectAlias, SelectExpression, TableField, Table, TableAlias

BASE_TOKEN_TYPES = [
	'string',
	'constant',
	'function',
	'table_field',
	# 'keyword',
]

KEYWORDS = {
	'select',
	'as',
	'case',
	'when',
	'then',
	'else',
	'end',
	'from',
	'full',
	'outer',
	'left',
	'right',
	'inner',
	'join',
	'where',
	'group',
	'by',
	'order',
	'desc',
	'asc',
	'limit',
	'offset',
}

# COMPOUND_KEYWORDS = [
# 	('left', 'join'),
# 	('right', 'join'),
# 	('inner', 'join'),

# 	('group', 'by'),
# 	('order', 'by'),
# ]

COMPOUND_KEYWORDS = {
	'left': {'join': True},
	'right': {'join': True},
	'inner': {'join': True},

	'group': {'by': True},
	'order': {'by': True},
}

import re

SEPARATOR_REGEX = re.compile(r'[^\w\.]')
def is_token_separator(char):
	# provavelmente lerdo
	return bool(SEPARATOR_REGEX.match(char))

INLINE_COMMENT_REGEX = re.compile(r'-- [^\n]*')
MULTILINE_COMMENT_REGEX = re.compile(r'/\*(.|\n)*\*\/')
def clean_comments(statement):
	# ignorando o caso de ter algo q parece comentario em uma string... (ae eh sacanagem)

	# print statement
	statement = INLINE_COMMENT_REGEX.sub('', statement)
	statement = MULTILINE_COMMENT_REGEX.sub('', statement)

	# print '********'
	# print statement

	# raise Exception()
	return statement

def base_tokenize(statement):
	current_token_chars = []
	tokens = []
	quote_type = ''
	for char in sql_statement:
		if char in ('"', "'"):
			if quote_type:
				if char == quote_type:
					quote_type = '' # sai da string

				current_token_chars.append(char)

				token_value = ''.join(current_token_chars)
				token_type = 'string'

				token = {
					'value': token_value,
					'type': token_type,
				}

				tokens.append(token)
				current_token_chars = []

			else:
				quote_type = char

				current_token_chars.append(char)

		elif quote_type:
			current_token_chars.append(char)

		elif is_token_separator(char):
			if current_token_chars:
				token_value = ''.join(current_token_chars).lower()
				token_type = 'table_field'
				try:
					int(token_value)
					token_type = 'const'
				except Exception as e:
					try:
						float(token_value)
						token_type = 'const'
					except Exception as e:
						pass

				if token_type == 'table_field' and token_value in KEYWORDS:
					token_type = 'keyword'
					

				token = {
					'value': token_value,
					'type': token_type,
				}

				tokens.append(token)
				current_token_chars = []

				# print '*********'
				# print "'%s'" % token

			if char.strip():
				token_value = char
				token_type = char

				token = {
					'value': token_value,
					'type': token_type,
				}

				tokens.append(token)

		else:
			current_token_chars.append(char)

	return tokens

def tokenize(statement):
	base_tokens = base_tokenize(statement)

	tokens = []
	possible_merge_tokens = []
	possible_merge_type = None
	def flush_possible_merge_tokens():
		for not_m_token in possible_merge_tokens:
			tokens.append(not_m_token)

		possible_merge_tokens[:] = []

	for token in base_tokens:
		# print '**************'
		# print token

		if token['type'] == 'keyword':
			if possible_merge_type != 'keyword':
				flush_possible_merge_tokens()

			# print 'maybe keyword'
			# verificar keyword
			possible_merge_tokens.append(token)

			merge_dict = COMPOUND_KEYWORDS
			for m_token in possible_merge_tokens:
				# print possible_merge_tokens
				merge_dict = merge_dict.get(m_token['value'])

			if merge_dict is None:
				# tentou seguir o dicionario mas falhou
				# print '-- not really kword...'
				flush_possible_merge_tokens()
				possible_merge_type = None

			elif merge_dict is True:
				merged_token = {
					'type': 'keyword',
					'value': _join_tokens(possible_merge_tokens),
				}
				tokens.append(merged_token)
				possible_merge_tokens = []
				possible_merge_type = None

				# print '-- really kword!'

			else:
				possible_merge_type = 'keyword'
				# print '-- not sure yet'

		elif token['type'] == 'table_field':
			flush_possible_merge_tokens()

			possible_merge_tokens.append(token)
			possible_merge_type = 'function'

		elif token['type'] == '(' and possible_merge_type == 'function' and possible_merge_tokens:
			if len(possible_merge_tokens) != 1:
				raise Exception(possible_merge_tokens)

			function_token = {
				'type': 'function',
				'value': _join_tokens(possible_merge_tokens),
			}
			tokens.append(function_token)

			possible_merge_tokens = []
			possible_merge_type = None

			tokens.append(token)

		else:
			flush_possible_merge_tokens()
			possible_merge_type = None
			tokens.append(token)


	return tokens

# ignorando sub queries
def get_select_tokens(tokens):
	token_values = [x['value'] for x in tokens]

	start = token_values.index('select')
	end = token_values.index('from')

	return tokens[start+1:end]

def get_index(search_list, value):
	try:
		return search_list.index(value)
	except Exception as e:
		return None

def get_from_tokens(tokens):
	token_values = [x['value'] for x in tokens]

	start = token_values.index('from')
	end_where = get_index(token_values, 'where')
	end_group = get_index(token_values, 'group by') # precisa mudar tokenizer para pegar key words
	end_order = get_index(token_values, 'order by') # precisa mudar tokenizer para pegar key words
	end_limit = get_index(token_values, 'limit')

	end = end_where or end_group or end_order or end_limit or len(token_values)
	return tokens[start+1:end]

def separate_by_select_statement(tokens):
	select_expressions = []
	select_expression_tokens = []
	parentesis_depth = 0
	for token in tokens:
		token_value = token['value']

		select_expression_tokens.append(token)

		if token_value == '(':
			parentesis_depth = parentesis_depth + 1

		elif token_value == ')':
			parentesis_depth = parentesis_depth - 1

		elif token_value == ',' and not parentesis_depth:
			select_expression_tokens = select_expression_tokens[:-1] # coisa horrivel pra tirar a virgula

			# select_expression = ' '.join(select_expression_tokens)
			select_expressions.append(select_expression_tokens)

			select_expression_tokens = []

	if select_expression_tokens:
		select_expressions.append(select_expression_tokens)

	return select_expressions

def separate_by_table_statement(tokens):
	table_expressions = []
	table_expression_tokens = []
	for token in tokens:
		token_value = token['value']

		if token_value in ('left join', 'right join', 'inner join', 'join'):
			if table_expression_tokens:
				# table_expression = ' '.join(table_expression_tokens)
				table_expressions.append(table_expression_tokens)

				table_expression_tokens = []
		else:
			table_expression_tokens.append(token)

	if table_expression_tokens:
		table_expressions.append(table_expression_tokens)

	return table_expressions

def _join_tokens(tokens):
	if not tokens:
		return ''

	return ' '.join([x['value'] for x in tokens])

def _get_token_value(token):
	if not token:
		return None

	return token.get('value')

def separate_alias(tokens):
	last_token = tokens[-1]
	if last_token['type'] != 'table_field':
		return tokens, _join_tokens(tokens)

	if len(tokens) == 1:
		return tokens, last_token['value'].split('.')[-1]

	before_last_token = tokens[-2]
	if before_last_token['value'] == 'as':
		return tokens[:-2], last_token['value']

	if before_last_token['value'] in '+/-*':
		return tokens, _join_tokens(tokens)

	return tokens[:-1], last_token['value']

def separate_table_expression(tokens):
	table = None
	alias = None
	on_conditions = None

	token_values = [x['value'] for x in tokens]
	on_index = get_index(token_values, 'on')
	if on_index:
		on_conditions = tokens[on_index+1:]
		tokens = tokens[:on_index]

	tokens = [x for x in tokens if x['value'] != 'as']

	table = tokens[0]
	if len(tokens) > 1:
		alias = tokens[1]

	return table, alias, on_conditions
		
test_file = open('resources/fake_queries/test.sql', 'r')
test_sql = test_file.read()
# test_sql = clean_comments(test_sql)

for sql_statement in test_sql.split(';')[2:3]: # problema se tiver ; em comentario ou string
	session.query(SelectAlias).delete()
	session.query(SelectExpression).delete()
	session.query(TableField).delete()
	session.query(Table).delete()
	session.query(TableAlias).delete()

	session.execute('delete from selectexpression_selectalias;')
	session.execute('delete from selectexpression_tablefields;')
	session.execute('delete from table_tablealias;')

	session.commit()

	sql_statement = clean_comments(sql_statement)
	sql_statement = sql_statement.replace('`', '')

	# TODO: considerar ` (crase) usada para dar escape em palavras-chave
	tokens = tokenize(sql_statement)
	# print '\n'.join(["%s: %s" % (x['type'].ljust(12), x['value']) for x in tokens])
	# print '\n'.join(["%s: %s" % (x['type'].ljust(12), x['value']) for x in tokens if x['type'] == 'table_field'])
	# raise Exception()

	from_tokens = get_from_tokens(tokens)
	# print '\n'.join([x['value'] for x in from_tokens])

	db_alias_dict = {}
	table_expressions = separate_by_table_statement(from_tokens)
	for table_expression in table_expressions:
		table, alias, on_conditions = separate_table_expression(table_expression)

		print '*********'
		print _join_tokens(table_expression)
		print "%s - %s - %s" % (_get_token_value(table), _get_token_value(alias), _join_tokens(on_conditions))

		db_table = Table(name=table['value'])
		session.add(db_table)
		if alias:
			db_table_alias = TableAlias(name=alias['value'])
			session.add(db_table_alias)

			db_table.table_aliases.extend([db_table_alias])

			db_alias_dict[alias['value']] = db_table

		db_alias_dict[table['value']] = db_table

	select_tokens = get_select_tokens(tokens)
	select_expressions = separate_by_select_statement(select_tokens)

	# print '************'
	# print '\n'.join([str([y['value'] for y in x]) for x in select_expressions])
	# raise Exception()

	for select_expression in select_expressions:
		not_alias_tokens, alias_name = separate_alias(select_expression)
		raw_select_expression = _join_tokens(not_alias_tokens)

		db_alias = SelectAlias(name=alias_name)
		db_expression = SelectExpression(raw_expression=raw_select_expression, parametrized_expression='Nay')

		db_table_fields = []
		for token in not_alias_tokens:
			if token['type'] == 'table_field':
				name = token['value'].split('.')[-1]
				table_alias = '.'.join(token['value'].split('.')[:-1])
				# table_alias = token['value'][:(len(token['value'])-len(name)-1)]

				db_table_field = TableField(name=name)
				db_table_field.table = db_alias_dict.get(table_alias)

				db_table_fields.append(db_table_field)

				if not db_table_field.table:
					raise Exception("t_alias: %s \nraw: %s \nfield: %s" % (table_alias, token['value'], name))


		session.add(db_alias)
		session.add(db_expression)
		for x in db_table_fields:
			session.add(x)

		db_alias.select_expressions.extend([db_expression])
		db_expression.table_fields.extend(db_table_fields)

		# print '************'
		# print alias_name
		# print raw_select_expression

	session.commit()
		
	# print '================'
	# print '\n'.join(["%s" % (str([y['value'] for y in x])) for x in table_expressions])

	# print '\n'.join(["%s: %s" % (separate_alias(x), str([y['value'] for y in x])) for x in select_expressions])
	# print '*********************'