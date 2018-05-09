#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
engine = create_engine('sqlite:///:memory:', echo=True)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table

Session = sessionmaker(bind=engine)
session = Session()

class SelectAlias(Base):
	__tablename__ = 'select_alias'

	id = Column(Integer, primary_key=True)
	name = Column(Text)

	select_expressions = relationship(
			"SelectExpression",
			secondary=Table('selectexpression_alias', Base.metadata,
						Column("select_alias_id", Integer, ForeignKey('select_alias.id'),
									primary_key=True),
						Column("select_expression_id", Integer, ForeignKey('select_expression.id'),
									primary_key=True)
					),
			backref="select_aliases"
			)

class SelectExpression(Base):
	__tablename__ = 'select_expression'

	id = Column(Integer, primary_key=True)
	raw_expression = Column(Text)
	parametrized_expression = Column(Text)

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