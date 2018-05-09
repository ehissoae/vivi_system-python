#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models import session, SelectAlias, SelectExpression

TOKEN_TYPES = [
	'string',
	'constant',
	'function',
	'table_field',
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

def tokenize(statement):
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

				if token_type == 'table_field':
					# checar se eh 'function'
					pass

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

# ignorando sub queries
def get_select_tokens(tokens):
	token_values = [x['value'] for x in tokens]

	start = token_values.index('select')
	end = token_values.index('from')

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

def _join_tokens(tokens):
	return ' '.join([x['value'] for x in tokens])

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
		
test_file = open('resources/fake_queries/test.sql', 'r')
test_sql = test_file.read()
# test_sql = clean_comments(test_sql)

for sql_statement in test_sql.split(';')[:1]: # problema se tiver ; em comentario ou string
	sql_statement = clean_comments(sql_statement)

	tokens = tokenize(sql_statement)
	tokens = get_select_tokens(tokens)
	select_expressions = separate_by_select_statement(tokens)

	for select_expression in select_expressions:
		alias_name = get_alias(select_expression)
		raw_select_expression = _join_tokens(select_expression)

		db_alias = SelectAlias(name=alias_name)
		db_expression = SelectExpression(raw_expression=raw_select_expression, parametrized_expression='Nay')

		session.add(db_alias)
		session.add(db_expression)
		db_alias.select_expressions.extend([db_expression])

	session.commit()

	# print '\n'.join(["%s: %s" % (get_alias(x), str([y['value'] for y in x])) for x in select_expressions])
	# print '*********************'