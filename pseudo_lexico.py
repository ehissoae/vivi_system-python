#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import session, SelectAlias, SelectExpression, TableField, Table, TableAlias

TOKEN_TYPES = [
	'string',
	'constant',
	'function',
	'table_field',
	'keyword',
]

KEYWORDS = [
	'select',
	'as',
	'case',
	'when',
	'then',
	'end',
	'from',
	'full',
	'outer',
	'left',
	'right',
	'join',
	'where',
	'group',
	'by',
	'order',
	'desc',
	'asc',
	'limit',
	'offset',
]

COMPOUND_KEYWORDS = [
	('left', 'join'),
	('right', 'join'),
	('inner', 'join'),

	('group', 'by'),
	('order', 'by'),
]

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
				token_value = ''.join(current_token_chars)
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

				# if token_type == 'table_field':
				# 	# checar se eh 'function'
				# 	pass

				token = {
					'value': token_value.lower(),
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
	for token in base_tokens:


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

		if token_value in ('left', 'right', 'inner', 'join'):
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

def get_alias(tokens):
	last_token = tokens[-1]
	if last_token['type'] != 'table_field':
		return _join_tokens(tokens)

	if len(tokens) == 1:
		return last_token['value'].split('.')[-1]

	before_last_token = tokens[-2]
	if before_last_token['value'] == 'as':
		return last_token['value']

	if before_last_token['value'] in '+/-*':
		return _join_tokens(tokens)

	return last_token['value']

def separate_table_expression(tokens):
	table = None
	alias = None
	on_conditions = None

	token_values = [x['value'] for x in tokens]
	on_index = get_index(token_values, 'on')
	if on_index:
		on_conditions = tokens[on_index+1:]
		tokens = tokens[:on_index]

	table = tokens[0]
	if len(tokens) > 1:
		alias = tokens[1]

	return table, alias, on_conditions
		
test_file = open('resources/fake_queries/test.sql', 'r')
test_sql = test_file.read()
# test_sql = clean_comments(test_sql)

for sql_statement in test_sql.split(';')[:1]: # problema se tiver ; em comentario ou string
	sql_statement = clean_comments(sql_statement)

	tokens = tokenize(sql_statement)
	select_tokens = get_select_tokens(tokens)
	select_expressions = separate_by_select_statement(select_tokens)

	for select_expression in select_expressions:
		alias_name = get_alias(select_expression)
		raw_select_expression = _join_tokens(select_expression)

		db_alias = SelectAlias(name=alias_name)
		db_expression = SelectExpression(raw_expression=raw_select_expression, parametrized_expression='Nay')

		session.add(db_alias)
		session.add(db_expression)
		db_alias.select_expressions.extend([db_expression])

	session.commit()

	from_tokens = get_from_tokens(tokens)
	# print '\n'.join([x['value'] for x in from_tokens])

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

	session.commit()
		
	print '================'
	print '\n'.join(["%s" % (str([y['value'] for y in x])) for x in table_expressions])

	# print '\n'.join(["%s: %s" % (get_alias(x), str([y['value'] for y in x])) for x in select_expressions])
	# print '*********************'