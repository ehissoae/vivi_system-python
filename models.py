#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table as AlchemyTable

Session = sessionmaker(bind=engine)
session = Session()

class SelectAlias(Base):
	__tablename__ = 'select_alias'

	id = Column(Integer, primary_key=True)
	name = Column(Text)

	select_expressions = relationship(
			'SelectExpression',
			secondary=AlchemyTable('selectexpression_selectalias', Base.metadata,
						Column('select_alias_id', Integer, ForeignKey('select_alias.id'),
									primary_key=True),
						Column('select_expression_id', Integer, ForeignKey('select_expression.id'),
									primary_key=True)
					),
			backref='select_aliases'
			)

class SelectExpression(Base):
	__tablename__ = 'select_expression'

	id = Column(Integer, primary_key=True)
	raw_expression = Column(Text)
	parametrized_expression = Column(Text)

class TableField(Base):
	__tablename__ = 'table_field'

	id = Column(Integer, primary_key=True)
	name = Column(Text)

	table = relationship('Table', back_populates='table_fields')
	table_id = Column(Integer, ForeignKey('table.id'))

	select_expressions = relationship(
			'SelectExpression',
			secondary=AlchemyTable('selectexpression_tablefields', Base.metadata,
						Column('table_field_id', Integer, ForeignKey('table_field.id'),
									primary_key=True),
						Column('select_expression_id', Integer, ForeignKey('select_expression.id'),
									primary_key=True)
					),
			backref='table_fields'
			)

class Table(Base):
	__tablename__ = 'table'

	id = Column(Integer, primary_key=True)
	name = Column(Text)

	table_fields = relationship('TableField', back_populates='table')

class TableAlias(Base):
	__tablename__ = 'table_alias'

	id = Column(Integer, primary_key=True)
	name = Column(Text)

	tables = relationship(
			'Table',
			secondary=AlchemyTable('table_tablealias', Base.metadata,
						Column('table_id', Integer, ForeignKey('table.id'),
									primary_key=True),
						Column('table_alias_id', Integer, ForeignKey('table_alias.id'),
									primary_key=True)
					),
			backref='table_aliases'
			)

Base.metadata.create_all(engine)

# alias = SelectAlias(name='yay')
# session.add(alias)

# expr = SelectExpression(raw_expression='nay', parametrized_expression='Nay')
# session.add(expr)

# alias.select_expressions.extend([expr])


# aliases = list(session.query(SelectAlias).order_by(SelectAlias.id))
# exprs = list(session.query(SelectExpression).order_by(SelectExpression.id))

# print '*************************8'
# for instance in aliases:
# 	print(instance.id, instance.name)

# for instance in exprs:
# 	print(instance.id, instance.raw_expression, instance.parametrized_expression)

# session.commit()