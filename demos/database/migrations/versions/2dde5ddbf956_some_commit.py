"""some commit

Revision ID: 2dde5ddbf956
Revises: 
Create Date: 2021-03-03 16:36:56.473729

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '2dde5ddbf956'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('t_adr')
    op.drop_index('ix_t_user_age', table_name='t_user')
    op.drop_table('t_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('t_user',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('address', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('age', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('dad', mysql.VARCHAR(length=128), nullable=True),
    sa.Column('name', mysql.VARCHAR(length=20), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_t_user_age', 't_user', ['age'], unique=False)
    op.create_table('t_adr',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('detail', mysql.VARCHAR(length=20), nullable=True),
    sa.Column('user_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['t_user.id'], name='t_adr_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_default_charset='utf8',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###